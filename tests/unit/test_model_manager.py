import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from main.model_manager import ModelManager
from main.config_manager import EnhancedConfig, SystemConfig, ModelsConfig, IndividualModelConfig, ModelPerformanceConfig
# Import the actual LocalLLMClient to mock its instance methods, not the class itself if it's complex to init
from utils.local_llm_client import LocalLLMClient, ModelResponse as LLMClientModelResponse, ModelRole as LLMClientModelRole


# --- Fixtures for creating configuration objects ---
@pytest.fixture
def minimal_system_config():
    return SystemConfig(ollama_host="http://localhost", ollama_port=11434)

@pytest.fixture
def sample_individual_model_config_data():
    return {
        "router": {
            "name": "Router", "model_id": "openhermes:7b", "role": "router", "system_prompt": "Route.",
            "performance": {"temperature": 0.1, "max_tokens": 50}
        },
        "lead_developer": {
            "name": "LeadDev", "model_id": "deepseek:16b", "role": "lead_developer", "system_prompt": "Code.",
            "performance": {"temperature": 0.5, "max_tokens": 1000}, "enabled": True
        },
        "disabled_model": {
            "name": "Disabled", "model_id": "disabled:7b", "role": "disabled_model_role", "system_prompt": "I am disabled.",
            "enabled": False
        }
    }

@pytest.fixture
def sample_models_config(sample_individual_model_config_data):
    # Adjusting to match the structure of ModelsConfig which expects specific role names as fields
    # For a more flexible ModelsConfig that takes a dict, this would be simpler.
    # Current ModelsConfig expects: router, math_specialist, lead_developer, senior_developer, principal_architect

    # Create default configs for roles not in sample_individual_model_config_data
    # to satisfy ModelsConfig Pydantic model structure if it's strict.
    # For this test, we'll assume ModelsConfig can be flexible or we only use defined roles.
    # Let's make a more flexible ModelsConfig for testing or provide all required.

    # For simplicity, let's ensure our sample_individual_model_config_data provides all required roles for ModelsConfig
    full_model_data = {
        "router": sample_individual_model_config_data["router"],
        "math_specialist": {"name": "Math", "model_id": "math:7b", "role": "math_specialist", "system_prompt": "Calc."},
        "lead_developer": sample_individual_model_config_data["lead_developer"],
        "senior_developer": {"name": "Senior", "model_id": "senior:13b", "role": "senior_developer", "system_prompt": "Review."},
        "principal_architect": {"name": "Arch", "model_id": "arch:13b", "role": "principal_architect", "system_prompt": "Design."}
    }
    return ModelsConfig(**full_model_data)


@pytest.fixture
def sample_enhanced_config(minimal_system_config, sample_models_config):
    return EnhancedConfig(system=minimal_system_config, models=sample_models_config)

@pytest.fixture
@patch('utils.local_llm_client.LocalLLMClient', autospec=True) # Mock the class
def mock_local_llm_client_instance(MockLocalLLMClientClass, minimal_system_config):
    # This fixture provides an instance of the mocked LocalLLMClient
    mock_instance = MockLocalLLMClientClass.return_value # Get the instance that would be created
    mock_instance.connect = AsyncMock(return_value=True) # Mock its connect method
    mock_instance.prime_model_configurations = AsyncMock()
    mock_instance.generate_response = AsyncMock()
    mock_instance.health_check = AsyncMock(return_value={"status": "healthy"})
    # Mock other methods of LocalLLMClient as needed by ModelManager
    return mock_instance


@pytest.fixture
def model_manager(sample_enhanced_config, mock_local_llm_client_instance):
    # When ModelManager is initialized, it creates a LocalLLMClient.
    # The @patch on mock_local_llm_client_instance ensures that this creation
    # results in our mock_instance being used.
    # We pass sample_enhanced_config.system to LocalLLMClient constructor.
    with patch('main.model_manager.LocalLLMClient', return_value=mock_local_llm_client_instance) as PatchedClient:
        mm = ModelManager(config=sample_enhanced_config)
        PatchedClient.assert_called_once_with(sample_enhanced_config.system)
        return mm

# --- Test Cases ---

@pytest.mark.asyncio
async def test_model_manager_initialization(model_manager: ModelManager, mock_local_llm_client_instance, sample_models_config):
    assert model_manager.local_llm_client == mock_local_llm_client_instance
    assert not model_manager.is_initialized

@pytest.mark.asyncio
async def test_initialize_clients_success(model_manager: ModelManager, mock_local_llm_client_instance, sample_models_config):
    await model_manager.initialize_clients()

    mock_local_llm_client_instance.prime_model_configurations.assert_called_once()
    # Check the argument passed to prime_model_configurations
    # It should be a list of IndividualModelConfig objects
    primed_configs_arg = mock_local_llm_client_instance.prime_model_configurations.call_args[0][0]
    assert isinstance(primed_configs_arg, list)
    assert len(primed_configs_arg) == len(sample_models_config.get_all_model_configs())
    assert all(isinstance(cfg, IndividualModelConfig) for cfg in primed_configs_arg)

    mock_local_llm_client_instance.connect.assert_called_once()
    assert model_manager.is_initialized

@pytest.mark.asyncio
async def test_initialize_clients_connection_failure(model_manager: ModelManager, mock_local_llm_client_instance):
    mock_local_llm_client_instance.connect.return_value = False # Simulate connection failure

    await model_manager.initialize_clients()

    assert not model_manager.is_initialized
    mock_local_llm_client_instance.connect.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_by_role_success(model_manager: ModelManager, mock_local_llm_client_instance, sample_models_config):
    await model_manager.initialize_clients() # Ensure initialized

    mock_response_content = "Router classification: general"
    mock_llm_response = LLMClientModelResponse(
        content=mock_response_content, model_name="openhermes:7b", role=LLMClientModelRole.ROUTER,
        tokens_generated=3, response_time_ms=100.0, temperature=0.1,
        confidence_score=0.9, metadata={}, timestamp=MagicMock()
    )
    mock_local_llm_client_instance.generate_response.return_value = mock_llm_response

    prompt = "Classify this task."
    response = await model_manager.get_completion_by_role("router", prompt)

    assert isinstance(response, LLMClientModelResponse)
    assert response.content == mock_response_content

    expected_model_cfg = sample_models_config.router
    mock_local_llm_client_instance.generate_response.assert_called_once_with(
        model_name=expected_model_cfg.model_id,
        prompt=prompt,
        system_prompt=expected_model_cfg.system_prompt,
        temperature=expected_model_cfg.performance.temperature,
        max_tokens=expected_model_cfg.performance.max_tokens,
        stream=False
    )

@pytest.mark.asyncio
async def test_get_completion_by_role_streaming(model_manager: ModelManager, mock_local_llm_client_instance):
    await model_manager.initialize_clients()

    async def mock_stream_generator():
        yield "Hello"
        yield " World"

    mock_local_llm_client_instance.generate_response.return_value = mock_stream_generator()

    prompt = "Stream hello."
    response_stream = await model_manager.get_completion_by_role("lead_developer", prompt, stream=True)

    assert hasattr(response_stream, '__aiter__') # Check if it's an async generator

    # Collect streamed content
    content_parts = [part async for part in response_stream] # type: ignore
    assert "".join(content_parts) == "Hello World"

    mock_local_llm_client_instance.generate_response.assert_called_once()
    call_args = mock_local_llm_client_instance.generate_response.call_args[1]
    assert call_args['stream'] is True


@pytest.mark.asyncio
async def test_get_completion_by_role_not_initialized(model_manager: ModelManager, mock_local_llm_client_instance):
    # ModelManager is not initialized (initialize_clients not called)
    response = await model_manager.get_completion_by_role("router", "A prompt")
    assert response is None # Should return None if not initialized and init fails
    # Check that initialize_clients was attempted
    mock_local_llm_client_instance.connect.assert_called_once()


@pytest.mark.asyncio
async def test_get_completion_by_role_unknown_role(model_manager: ModelManager):
    await model_manager.initialize_clients()
    response = await model_manager.get_completion_by_role("unknown_role", "A prompt")
    assert response is None

@pytest.mark.asyncio
async def test_get_completion_by_role_disabled_model(model_manager_with_disabled: ModelManager, sample_enhanced_config_with_disabled):
    # Need a specific ModelManager instance initialized with a config that has a disabled model
    # For this, we'll create a new config and manager instance within the test or use a dedicated fixture.

    # Create a config where 'router' is disabled
    disabled_models_data = sample_enhanced_config_with_disabled.models.model_dump()
    disabled_models_data["router"]["enabled"] = False

    disabled_models_cfg = ModelsConfig(**disabled_models_data)
    config_with_disabled_router = EnhancedConfig(system=sample_enhanced_config_with_disabled.system, models=disabled_models_cfg)

    with patch('main.model_manager.LocalLLMClient') as PatchedClient_disabled:
        mock_llm_client_disabled_instance = PatchedClient_disabled.return_value
        mock_llm_client_disabled_instance.connect = AsyncMock(return_value=True)
        mock_llm_client_disabled_instance.prime_model_configurations = AsyncMock()

        mm_disabled = ModelManager(config=config_with_disabled_router)
        await mm_disabled.initialize_clients()

        response = await mm_disabled.get_completion_by_role("router", "A prompt")
        assert response is None
        # Ensure generate_response was NOT called for the disabled model
        mock_llm_client_disabled_instance.generate_response.assert_not_called()


@pytest.mark.asyncio
async def test_health_check_models(model_manager: ModelManager, mock_local_llm_client_instance):
    await model_manager.initialize_clients()

    mock_health_data = {"ollama_status": "running", "models_ok": 5}
    mock_local_llm_client_instance.health_check.return_value = mock_health_data

    health_status = await model_manager.health_check_models()

    assert health_status == mock_health_data
    mock_local_llm_client_instance.health_check.assert_called_once()

@pytest.mark.asyncio
async def test_get_embeddings_placeholder(model_manager: ModelManager, mock_local_llm_client_instance):
    # This test acknowledges the placeholder nature of get_embeddings
    await model_manager.initialize_clients()

    # If LocalLLMClient had a 'generate_embeddings_ollama' method:
    mock_local_llm_client_instance.generate_embeddings_ollama = AsyncMock(return_value=[[0.1,0.2]])

    texts = ["text1", "text2"]
    embeddings = await model_manager.get_embeddings(texts) # Uses default model logic

    # Current placeholder returns a fixed list if method doesn't exist
    # If generate_embeddings_ollama was real and mocked:
    # mock_local_llm_client_instance.generate_embeddings_ollama.assert_called_once()
    # assert embeddings == [[0.1,0.2]]

    # For current placeholder:
    assert embeddings is not None
    assert len(embeddings) == len(texts)
    assert len(embeddings[0]) == 10 # Current placeholder dimension

# Fixture for the disabled model test
@pytest.fixture
def sample_enhanced_config_with_disabled(minimal_system_config, sample_models_config):
    # This fixture is just to provide a base config. The test itself modifies it.
    return EnhancedConfig(system=minimal_system_config, models=sample_models_config)

@pytest.fixture
def model_manager_with_disabled(sample_enhanced_config_with_disabled, mock_local_llm_client_instance):
    # This fixture allows setting up a ModelManager with a config that can be modified in the test
    with patch('main.model_manager.LocalLLMClient', return_value=mock_local_llm_client_instance):
        mm = ModelManager(config=sample_enhanced_config_with_disabled)
        return mm
