import asyncio
import logging
from typing import Dict, Any, Optional, Union, AsyncGenerator

from pydantic import BaseModel, Field

# Assuming these will be the actual classes from your project
from main.config_manager import ConfigManager, EnhancedConfig
from main.model_manager import ModelManager
from utils.local_llm_client import ModelResponse as LLMClientModelResponse # For type hinting

logger = logging.getLogger(__name__)

# Placeholder for Pydantic AI Agent base class
# from pydantic_ai import Agent as PydanticAIAgentBase # Actual import
class PydanticAIAgentBase(BaseModel): # Mock for now
    pass

class CodingRequestContext(BaseModel):
    user_prompt: str
    language: Optional[str] = None
    project_context: Optional[Dict[str, Any]] = None
    # Add other relevant context fields

class CodingDirectorResponse(BaseModel):
    classification: Optional[str] = None
    final_response: Optional[str] = None
    error_message: Optional[str] = None
    model_used: Optional[str] = None # The final specialist model that gave the answer
    full_model_response: Optional[LLMClientModelResponse] = None # If returning the rich object

class CodingDirector(PydanticAIAgentBase):
    """
    Main AI orchestrator for the Elite Coding Assistant.
    It uses Pydantic AI principles, classifies tasks, routes them to specialized models,
    and manages fallback logic.
    """
    config_manager: ConfigManager
    model_manager: ModelManager
    is_initialized: bool = Field(default=False, exclude=True)

    def __init__(self, config_manager: ConfigManager, model_manager: ModelManager, **data: Any):
        super().__init__(**data)
        self.config_manager = config_manager
        self.model_manager = model_manager
        # Initialization of clients is handled by ModelManager's own init method now
        logger.info("CodingDirector initialized. Ensure ModelManager clients are initialized before processing.")

    async def initialize(self):
        """Initializes the underlying ModelManager's clients."""
        if not self.model_manager.is_initialized:
            logger.info("CodingDirector: Initializing ModelManager clients...")
            await self.model_manager.initialize_clients()
            self.is_initialized = self.model_manager.is_initialized
            if self.is_initialized:
                logger.info("CodingDirector: ModelManager clients initialized successfully.")
            else:
                logger.error("CodingDirector: Failed to initialize ModelManager clients.")
        else:
            self.is_initialized = True
            logger.info("CodingDirector: ModelManager clients were already initialized.")


    async def classify_task(self, user_prompt: str) -> Optional[str]:
        """
        Uses the router model to classify the user's task.
        Expected classifications: "math" or "general".
        """
        if not self.is_initialized:
            logger.error("CodingDirector not initialized. Cannot classify task.")
            return None

        logger.info(f"Classifying task for prompt: '{user_prompt[:100]}...'")
        # The router's system prompt (in config/models.json) guides it to output 'math' or 'general'
        router_response = await self.model_manager.get_completion_by_role(
            role="router",
            prompt=f"Classify the following user request: \"{user_prompt}\"",
            # System prompt is already set in model config for router
        )

        if router_response and isinstance(router_response, LLMClientModelResponse):
            classification = router_response.content.strip().lower()
            logger.info(f"Task classified as: '{classification}'")
            if classification in ["math", "general"]:
                return classification
            else:
                logger.warning(f"Router returned unexpected classification: '{classification}'. Defaulting to 'general'.")
                return "general" # Default fallback classification
        else:
            logger.error("Failed to get classification from router model.")
            return "general" # Default if router fails

    async def _get_specialist_response(
        self,
        role: str,
        context: CodingRequestContext,
        system_prompt_override: Optional[str] = None
    ) -> Optional[LLMClientModelResponse]:
        """Helper to call a specialist model."""
        if not self.is_initialized:
            logger.error(f"CodingDirector not initialized. Cannot get response for role {role}.")
            return None

        # Construct a more detailed prompt for the specialist if needed
        # For now, just passing the user_prompt. This can be enhanced.
        specialist_prompt = context.user_prompt
        if context.language:
            specialist_prompt = f"Language: {context.language}\nRequest: {context.user_prompt}"

        # Add project context if available (this needs a strategy for how to format it)
        # if context.project_context:
        # specialist_prompt += f"\nProject Context: {json.dumps(context.project_context)}"


        logger.info(f"Requesting completion from specialist role '{role}' for prompt: '{context.user_prompt[:100]}...'")
        response = await self.model_manager.get_completion_by_role(
            role=role,
            prompt=specialist_prompt,
            system_prompt_override=system_prompt_override
        )
        if response and isinstance(response, LLMClientModelResponse) and response.content.strip():
            logger.info(f"Received response from {role}.")
            return response
        else:
            logger.warning(f"No valid response or empty content from {role}.")
            return None

    async def process_request(self, context: CodingRequestContext) -> CodingDirectorResponse:
        """
        Processes a coding assistance request:
        1. Classifies the task.
        2. Routes to the primary specialist.
        3. Implements fallback logic if primary specialist fails.
        """
        if not self.is_initialized:
            await self.initialize() # Attempt to initialize if not already
            if not self.is_initialized:
                return CodingDirectorResponse(error_message="CodingDirector and its ModelManager are not initialized.")

        classification = await self.classify_task(context.user_prompt)
        if not classification:
            return CodingDirectorResponse(classification="unknown", error_message="Task classification failed.")

        primary_role_map = {
            "math": "math_specialist",
            "general": "lead_developer"
        }
        primary_role = primary_role_map.get(classification, "lead_developer")

        response_model: Optional[LLMClientModelResponse] = None

        # Attempt 1: Primary Specialist
        logger.info(f"Attempting primary specialist: {primary_role}")
        response_model = await self._get_specialist_response(primary_role, context)

        # Attempt 2: Senior Developer (Fallback for general tasks or if primary failed)
        if not response_model:
            fallback_role_1 = "senior_developer"
            logger.warning(f"Primary specialist {primary_role} failed or gave empty response. Trying fallback: {fallback_role_1}")
            response_model = await self._get_specialist_response(fallback_role_1, context)

        # Attempt 3: Principal Architect (Final Fallback for any task if others failed)
        if not response_model:
            fallback_role_2 = "principal_architect"
            logger.warning(f"Fallback {fallback_role_1} also failed or gave empty response. Trying final fallback: {fallback_role_2}")
            response_model = await self._get_specialist_response(fallback_role_2, context)

        if response_model:
            return CodingDirectorResponse(
                classification=classification,
                final_response=response_model.content,
                model_used=response_model.model_name, # This is the Ollama model_id
                full_model_response=response_model
            )
        else:
            logger.error(f"All models failed to provide a response for prompt: '{context.user_prompt[:100]}...'")
            return CodingDirectorResponse(
                classification=classification,
                error_message="All specialist models failed to provide a response."
            )

# --- Example Usage ---
async def example_director_usage():
    # This setup would typically happen at the application's entry point.
    try:
        # 1. Initialize ConfigManager
        config_mgr = ConfigManager() # Assumes config files are in default 'config/'
        app_config = config_mgr.get_config()

        # 2. Initialize ModelManager
        model_mgr = ModelManager(config=app_config)
        # ModelManager's own initialize_clients() is called by CodingDirector

        # 3. Initialize CodingDirector
        director = CodingDirector(config_manager=config_mgr, model_manager=model_mgr)
        await director.initialize() # Critical step

        if not director.is_initialized:
            print("Failed to initialize CodingDirector. Exiting example.")
            return

        # Example requests
        request1_context = CodingRequestContext(user_prompt="Calculate the factorial of 5 using Python.")
        response1 = await director.process_request(request1_context)
        print(f"\n--- Response 1 (Prompt: {request1_context.user_prompt}) ---")
        if response1.error_message:
            print(f"Error: {response1.error_message}")
        else:
            print(f"Classification: {response1.classification}")
            print(f"Model Used: {response1.model_used}")
            print(f"Response: {response1.final_response}")

        request2_context = CodingRequestContext(user_prompt="Explain the concept of closures in JavaScript.")
        response2 = await director.process_request(request2_context)
        print(f"\n--- Response 2 (Prompt: {request2_context.user_prompt}) ---")
        if response2.error_message:
            print(f"Error: {response2.error_message}")
        else:
            print(f"Classification: {response2.classification}")
            print(f"Model Used: {response2.model_used}")
            print(f"Response: {response2.final_response}")

        request3_context = CodingRequestContext(user_prompt="This is a very complex and ambiguous request that might fail all models just to test fallback to error.")
        response3 = await director.process_request(request3_context)
        print(f"\n--- Response 3 (Prompt: {request3_context.user_prompt[:50]}...) ---")
        if response3.error_message:
            print(f"Error: {response3.error_message}")
        else:
            print(f"Classification: {response3.classification}")
            print(f"Model Used: {response3.model_used}")
            print(f"Response: {response3.final_response}")


    except FileNotFoundError:
        print("Error: Ensure config/system.json and config/models.json exist in a 'config' directory relative to this script's execution path.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # To run this example:
    # 1. Make sure you have 'config/system.json' and 'config/models.json' accessible.
    #    You might need to create a 'config' folder in the same directory as this script
    #    and copy the JSON files there if running this script directly.
    # 2. Ensure your Ollama server is running with the required models.
    #    (openhermes:7b, mathstral:7b, deepseek-coder-v2:16b-lite-instruct, codellama:13b, wizardcoder:13b-python)
    asyncio.run(example_director_usage())
