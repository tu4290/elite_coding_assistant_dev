import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, AsyncGenerator

from main.config_manager import ConfigManager, IndividualModelConfig, ModelsConfig, EnhancedConfig
from utils.local_llm_client import LocalLLMClient, ModelResponse as LLMClientModelResponse, ModelRole as LLMClientModelRole

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages interactions with various language models, using LocalLLMClient for Ollama models.
    It loads configurations via ConfigManager and provides a consistent interface
    for the application to request model completions by role.
    """
    def __init__(self, config: EnhancedConfig): # Expects the fully loaded config object
        self.config = config
        self.models_config: ModelsConfig = config.models

        # Initialize LocalLLMClient with the system part of the config
        # LocalLLMClient expects an object with ollama_host attribute.
        # The ollama_base_url property in SystemConfig now provides the full URL.
        self.local_llm_client = LocalLLMClient(config.system) # Pass the SystemConfig part

        # This will be set after successful connection
        self.is_initialized = False
        logger.info("ModelManager initialized. Call `await self.initialize_clients()` to connect.")

    async def initialize_clients(self):
        """
        Connects the LocalLLMClient to Ollama and verifies models.
        This should be called once at application startup.
        """
        if self.is_initialized:
            logger.info("Model clients already initialized.")
            return

        logger.info("Initializing LocalLLMClient and connecting to Ollama...")
        # The LocalLLMClient's _load_model_configs needs to be refactored
        # to use the configurations from self.models_config.
        # For now, we'll pass it during connect or a new method.

        # Refactor LocalLLMClient to accept model configs during initialization or a dedicated method
        await self.local_llm_client.prime_model_configurations(self.models_config.get_all_model_configs())

        connected = await self.local_llm_client.connect()
        if connected:
            self.is_initialized = True
            logger.info("LocalLLMClient connected successfully and models verified.")
        else:
            self.is_initialized = False
            logger.error("Failed to connect LocalLLMClient to Ollama or verify models.")
            # Consider raising an exception here if connection is critical for startup

    async def get_completion_by_role(
        self,
        role: str, # e.g., "router", "lead_developer"
        prompt: str,
        system_prompt_override: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any # For additional model-specific params like temperature
    ) -> Union[LLMClientModelResponse, AsyncGenerator[str, None], None]:
        """
        Gets a completion from the model assigned to the specified role.

        Args:
            role: The role of the model to use (e.g., "router", "lead_developer").
            prompt: The user prompt.
            system_prompt_override: Optional system prompt to override the default for the model.
            stream: Whether to stream the response.
            **kwargs: Additional parameters to pass to the model (e.g., temperature).

        Returns:
            A ModelResponse object if not streaming, or an AsyncGenerator for streaming.
            Returns None if the model role is not found, not enabled, or an error occurs.
        """
        if not self.is_initialized:
            logger.error("ModelManager not initialized. Call `await initialize_clients()` first.")
            # Or attempt to initialize: await self.initialize_clients()
            # If still not initialized, then return None or raise
            if not self.is_initialized: # Check again after attempting init
                 logger.error("Initialization failed. Cannot get completion.")
                 return None


        model_cfg = self.models_config.get_model_config_by_role(role)
        if not model_cfg:
            logger.error(f"No model configuration found for role: {role}")
            return None
        if not model_cfg.enabled:
            logger.warning(f"Model for role '{role}' ({model_cfg.model_id}) is disabled.")
            return None

        # Prepare parameters for LocalLLMClient
        # System prompt: override > config > default (LocalLLMClient might have its own default)
        final_system_prompt = system_prompt_override if system_prompt_override is not None else model_cfg.system_prompt

        # Performance parameters: kwargs > config > default (LocalLLMClient handles its defaults)
        temperature = kwargs.get('temperature', model_cfg.performance.temperature)
        max_tokens = kwargs.get('max_tokens', model_cfg.performance.max_tokens)
        # Pass all relevant performance parameters
        performance_params = model_cfg.performance

        try:
            logger.debug(f"Requesting completion from model '{model_cfg.model_id}' for role '{role}'.")
            response = await self.local_llm_client.generate_response(
                model_name=model_cfg.model_id,
                prompt=prompt,
                system_prompt=final_system_prompt,
                temperature=temperature, # This uses the override or model_cfg's temp
                max_tokens=max_tokens,   # This uses the override or model_cfg's max_tokens
                stream=stream,
                # Pass other parameters from the model's performance config
                top_p=kwargs.get('top_p', performance_params.top_p),
                top_k=kwargs.get('top_k', performance_params.top_k),
                repeat_penalty=kwargs.get('repeat_penalty', performance_params.repeat_penalty)
                # context_length is usually a load-time param, but LocalLLMClient sets num_ctx from its internal model_config_internal
            )
            return response
        except ValueError as ve: # e.g. model unknown or disabled by LocalLLMClient
            logger.error(f"ValueError from LocalLLMClient for role '{role}' ({model_cfg.model_id}): {ve}")
            return None
        except Exception as e:
            logger.exception(f"Error getting completion for role '{role}' ({model_cfg.model_id}): {e}")
            return None

    async def get_embeddings(self, texts: List[str], model_name: Optional[str] = None) -> Optional[List[List[float]]]:
        """
        Generates embeddings for a list of texts using a specified embedding model.
        If no model_name is provided, it should pick a default embedding model.
        Note: This functionality might be better placed directly in LocalLLMClient or a
              dedicated EmbeddingService if multiple embedding model types are supported.
              For now, assuming LocalLLMClient might be extended or ModelManager picks one.
        """
        if not self.is_initialized:
            logger.error("ModelManager not initialized for embeddings.")
            return None

        # Determine the embedding model. This logic needs to be robust.
        # Option 1: A specific model role for embeddings, e.g., "embedding_generator"
        # Option 2: A default embedding model ID in config
        # Option 3: Pass it through, LocalLLMClient handles it.

        # For now, let's assume if model_name is not given, we need a default.
        # This part needs refinement based on how embedding models are configured.
        # Let's assume there's a configured default or the client handles it.
        # This is a placeholder for actual embedding model selection logic.
        # A more robust solution would involve a dedicated configuration for embedding models
        # or a specific role like "embedding_generator".
        # For now, if a model_name is passed, use it. Otherwise, try a system default.

        embedding_model_id_to_use = model_name
        if not embedding_model_id_to_use:
            # Attempt to get a default embedding model from system config if defined
            # Example: self.config.system.default_embedding_model_id
            # For now, let's hardcode a common one or rely on LocalLLMClient's potential default
            # This should be improved with proper configuration.
            default_ollama_embedding_model = "nomic-embed-text" # A common Ollama embedding model
            logger.warning(f"No specific embedding model name provided. Using default: {default_ollama_embedding_model}")
            embedding_model_id_to_use = default_ollama_embedding_model
            # We should also verify if this default model is listed in self.models_config
            # or if LocalLLMClient can handle arbitrary model_ids for embeddings.
            # The current LocalLLMClient.generate_embeddings_ollama doesn't check against self.models

        if not embedding_model_id_to_use: # Still no model ID
            logger.error("No embedding model could be determined.")
            return None

        logger.info(f"Requesting embeddings for {len(texts)} texts using model '{embedding_model_id_to_use}'")
        try:
            # Now LocalLLMClient has generate_embeddings_ollama
            return await self.local_llm_client.generate_embeddings_ollama(
                model_name=embedding_model_id_to_use,
                texts=texts
            )
        except Exception as e:
            logger.exception(f"Error generating embeddings via ModelManager using {embedding_model_id_to_use}: {e}")
            return None

    async def health_check_models(self) -> Dict[str, Any]:
        """Performs a health check on the connected LLM services via LocalLLMClient."""
        if not self.is_initialized:
            return {"status": "error", "message": "ModelManager not initialized."}
        return await self.local_llm_client.health_check()


# Example Usage (typically done once at application startup)
async def example_mm_usage():
    # This example assumes config files are in default locations
    try:
        config_mgr = ConfigManager() # Loads config/system.json and config/models.json
        app_conf = config_mgr.get_config()

        model_mgr = ModelManager(config=app_conf)
        await model_mgr.initialize_clients() # Connects LocalLLMClient

        if model_mgr.is_initialized:
            print("ModelManager initialized successfully.")

            # Test health check
            health = await model_mgr.health_check_models()
            print("\nModel Health Check:", health)

            # Test getting a completion
            print("\nTesting router completion:")
            router_prompt = "Classify this task: write a python function to sort a list."
            # Using default system prompt from config
            router_response = await model_mgr.get_completion_by_role("router", router_prompt)

            if router_response and isinstance(router_response, LLMClientModelResponse):
                print(f"Router Response: {router_response.content}")
            elif router_response is None:
                print("Router response was None.")
            else: # Streaming case
                print("Router Response (streaming):")
                async for chunk in router_response: # type: ignore
                    print(chunk, end="", flush=True)
                print()

            # Test lead_developer with streaming
            print("\nTesting lead_developer completion (streaming):")
            dev_prompt = "Write a simple Python function that returns 'Hello, World!'"
            dev_response_stream = await model_mgr.get_completion_by_role("lead_developer", dev_prompt, stream=True)
            if dev_response_stream and not isinstance(dev_response_stream, LLMClientModelResponse): # Check it's a generator
                print("Lead Developer Response (streaming):")
                async for chunk in dev_response_stream:
                    print(chunk, end="", flush=True)
                print()
            elif dev_response_stream is None:
                 print("Lead developer stream was None.")
            else:
                 print(f"Lead Developer (non-streamed): {dev_response_stream.content}")


        else:
            print("ModelManager failed to initialize.")

    except FileNotFoundError:
        print("Error: Ensure config/system.json and config/models.json exist.")
    except Exception as e:
        print(f"An error occurred during ModelManager example usage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure config files (system.json, models.json) are present in a 'config' directory
    # relative to where this script is run, or adjust ConfigManager paths.
    # Also, ensure Ollama server is running with the required models.
    # Example:
    # mkdir config
    # cp path_to_your_repo/config/system.json config/
    # cp path_to_your_repo/config/models.json config/
    asyncio.run(example_mm_usage())
