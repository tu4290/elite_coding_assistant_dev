import asyncio
import logging
from typing import Dict, Any, Optional, Union, AsyncGenerator

from pydantic import BaseModel, Field, field_validator

# Assuming these will be the actual classes from your project
from main.config_manager import ConfigManager, EnhancedConfig
from main.model_manager import ModelManager
from utils.local_llm_client import ModelResponse as LLMClientModelResponse # For type hinting
from main.prompt_models import PromptContext # Assuming this is the structure from user

logger = logging.getLogger(__name__)

# This will be a standard Python class, not inheriting from a pydantic-ai Agent base.
# Pydantic BaseModel is used for its own configuration or internal states if any.

class CodingTaskRequestContext(BaseModel):
    """
    Input context for a coding task request to the CodingDirector.
    Designed to be compatible with or constructible from main.prompt_models.PromptContext.
    """
    user_id: str
    conversation_id: str
    user_prompt: str = Field(..., min_length=1)
    language: Optional[str] = None

    # Fields from main.prompt_models.PromptContext that might be relevant
    recent_history: List[str] = Field(default_factory=list)
    retrieved_knowledge: List[str] = Field(default_factory=list)
    recognized_patterns: List[str] = Field(default_factory=list)

    # Additional specific context CodingDirector might use
    project_root_path: Optional[str] = None
    current_file_path: Optional[str] = None
    selection_range: Optional[Dict[str, int]] = None # E.g., {"start_line": 10, "end_line": 15}

    # Arbitrary additional context from the calling environment
    extra_context_data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_prompt_context(cls, prompt_context: PromptContext, **kwargs):
        """Helper to create CodingTaskRequestContext from an existing PromptContext."""
        return cls(
            user_id=prompt_context.user_id,
            conversation_id=prompt_context.conversation_id,
            user_prompt=prompt_context.feedback if prompt_context.feedback else "N/A", # Or raise if prompt is essential from PromptContext
            recent_history=prompt_context.recent_history,
            retrieved_knowledge=prompt_context.retrieved_knowledge,
            recognized_patterns=prompt_context.recognized_patterns,
            **kwargs # Allows overriding or adding other fields like language, project_root_path
        )

    @field_validator('language')
    def language_must_be_sensible(cls, v: Optional[str]):
        if v and not v.isalnum(): # Basic check
            raise ValueError("Language should be alphanumeric if provided.")
        return v


class CodingDirectorFinalResult(BaseModel):
    """
    Represents the final structured result from the CodingDirector's processing.
    This should be compatible with or transformable into main.prompt_models.PromptResult if needed,
    though PromptResult seems more about a generated prompt than a final LLM answer.
    """
    classification: Optional[str] = None
    llm_response_content: Optional[str] = None
    error_message: Optional[str] = None

    # Details about the LLM call that produced the final_response_content
    responding_model_id: Optional[str] = None # e.g., "deepseek-coder-v2:16b-lite-instruct"
    responding_model_role: Optional[str] = None # e.g., "lead_developer"

    # Optionally include the full rich response from LocalLLMClient for more details
    full_llm_model_response: Optional[LLMClientModelResponse] = None

    # Metadata about the director's process
    request_context_used: CodingTaskRequestContext # Echo back the context for clarity
    processing_time_seconds: Optional[float] = None

    # If this result itself needs to be compatible with PromptResult structure:
    # def to_prompt_result(self, original_prompt_context: PromptContext) -> 'PromptResult':
    #     # This transformation depends on how PromptResult is used.
    #     # If PromptResult.prompt is the *final answer*, then:
    #     return PromptResult(
    #         prompt=self.llm_response_content or self.error_message or "No response",
    #         context=original_prompt_context, # Or a new context derived from request_context_used
    #         notes=f"Processed by CodingDirector. Classification: {self.classification}. Model: {self.responding_model_id}",
    #         score=None # Or some quality score if available
    #     )


class CodingDirector:
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

    async def initialize(self) -> bool:
        """
        Initializes the underlying ModelManager's clients.
        Returns True if initialization was successful or already done, False otherwise.
        """
        if not self.is_initialized: # Check own flag first
            if not self.model_manager.is_initialized:
                logger.info("CodingDirector: Initializing ModelManager clients...")
                await self.model_manager.initialize_clients()

            self.is_initialized = self.model_manager.is_initialized # Update own flag based on manager's

            if self.is_initialized:
                logger.info("CodingDirector: ModelManager clients initialized successfully.")
            else:
                logger.error("CodingDirector: Failed to initialize ModelManager clients.")
        elif not self.model_manager.is_initialized:
            # This case implies CodingDirector thought it was initialized, but ModelManager is not.
            # Attempt re-initialization.
            logger.warning("CodingDirector was marked initialized, but ModelManager is not. Re-initializing ModelManager.")
            await self.model_manager.initialize_clients()
            self.is_initialized = self.model_manager.is_initialized
            if not self.is_initialized:
                 logger.error("CodingDirector: Failed to re-initialize ModelManager clients.")
        else:
            # Already initialized
            pass # logger.info("CodingDirector: ModelManager clients were already initialized.")
        return self.is_initialized


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
        if not self.is_initialized: # Should have been ensured by process_request
            logger.error(f"CodingDirector not initialized in _get_specialist_response for role {role}.")
            return None

        # Construct a more detailed prompt for the specialist
        prompt_parts = []
        prompt_parts.append(f"User Request: {context.user_prompt}")

        if context.language:
            prompt_parts.append(f"Programming Language: {context.language}")
        if context.current_file_path:
            prompt_parts.append(f"Current File: {context.current_file_path}")
        if context.project_root_path:
            prompt_parts.append(f"Project Root: {context.project_root_path}")
        if context.recent_history:
            history_str = "\n".join([f"- {h}" for h in context.recent_history[-3:]]) # Last 3 history items
            prompt_parts.append(f"Recent Conversation History:\n{history_str}")
        if context.retrieved_knowledge:
            knowledge_str = "\n".join([f"- {k}" for k in context.retrieved_knowledge[:2]]) # Top 2 knowledge items
            prompt_parts.append(f"Relevant Retrieved Knowledge:\n{knowledge_str}")
        if context.recognized_patterns:
            patterns_str = ", ".join(context.recognized_patterns)
            prompt_parts.append(f"Recognized Patterns: {patterns_str}")
        if context.extra_context_data:
            extra_str = json.dumps(context.extra_context_data, indent=2)
            prompt_parts.append(f"Additional Context:\n{extra_str}")

        specialist_prompt = "\n\n".join(prompt_parts)

        logger.info(f"Requesting completion from specialist role '{role}' with constructed prompt for user_prompt: '{context.user_prompt[:50]}...'")

        # The system prompt for the role is handled by ModelManager when it calls LocalLLMClient
        response = await self.model_manager.get_completion_by_role(
            role=role,
            prompt=specialist_prompt, # This is the user-facing part of the prompt
            system_prompt_override=system_prompt_override # CodingDirector can still override if needed for a specific step
        )

        if response and isinstance(response, LLMClientModelResponse) and response.content and response.content.strip():
            logger.info(f"Received valid response from {role} (model: {response.model_name}).")
            return response
        else:
            if response and isinstance(response, LLMClientModelResponse) and (not response.content or not response.content.strip()):
                logger.warning(f"Received empty or whitespace-only content from {role} (model: {response.model_name}).")
            elif not response:
                 logger.warning(f"No response object received from {role}.")
            return None

    async def process_request(self, context: CodingTaskRequestContext) -> CodingDirectorFinalResult:
        """
        Processes a coding assistance request:
        1. Validates input context.
        2. Ensures services are initialized.
        3. Classifies the task.
        4. Routes to the primary specialist.
        5. Implements fallback logic if primary specialist fails.
        6. Returns a structured result.
        """
        start_time = time.time()

        # Input validation is implicitly handled by Pydantic if type hint is CodingTaskRequestContext
        # but can add explicit validation if needed.
        try:
            CodingTaskRequestContext.model_validate(context) # Explicit validation
        except Exception as e: # Catches Pydantic ValidationError
            logger.error(f"Invalid request context: {e}")
            return CodingDirectorFinalResult(
                request_context_used=context, # Echo invalid context
                error_message=f"Invalid request context: {e}",
                processing_time_seconds=time.time() - start_time
            )

        if not await self.initialize(): # Ensures ModelManager and its clients are ready
            return CodingDirectorFinalResult(
                request_context_used=context,
                error_message="CodingDirector services could not be initialized.",
                processing_time_seconds=time.time() - start_time
            )

        classification = await self.classify_task(context.user_prompt)
        # classify_task already defaults to "general" on failure, so classification should always be a string.

        primary_role_map = {
            "math": "math_specialist",
            "general": "lead_developer"
        }
        # If classification is None (e.g. router totally failed and returned None), default to general
        primary_role = primary_role_map.get(classification or "general", "lead_developer")

        final_llm_response: Optional[LLMClientModelResponse] = None
        final_role_used: Optional[str] = None

        # Fallback chain
        roles_to_try = [
            primary_role,
            "senior_developer",
            "principal_architect"
        ]
        # Ensure no duplicate roles if primary_role is one of the fallbacks
        unique_roles_to_try = []
        for r in roles_to_try:
            if r not in unique_roles_to_try:
                unique_roles_to_try.append(r)

        for role_attempt in unique_roles_to_try:
            logger.info(f"Attempting specialist: {role_attempt}")
            final_llm_response = await self._get_specialist_response(role_attempt, context)
            if final_llm_response:
                final_role_used = role_attempt
                break # Success

        processing_time = time.time() - start_time

        if final_llm_response:
            return CodingDirectorFinalResult(
                classification=classification,
                llm_response_content=final_llm_response.content,
                responding_model_id=final_llm_response.model_name,
                responding_model_role=final_role_used or final_llm_response.role.value, # Use role from response if available
                full_llm_model_response=final_llm_response,
                request_context_used=context,
                processing_time_seconds=processing_time
            )
        else:
            error_msg = f"All models in the chain ({', '.join(unique_roles_to_try)}) failed to provide a response for prompt: '{context.user_prompt[:100]}...'"
            logger.error(error_msg)
            return CodingDirectorFinalResult(
                classification=classification,
                error_message=error_msg,
                request_context_used=context,
                processing_time_seconds=processing_time
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
