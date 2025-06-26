import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from main.coding_director import CodingDirector, CodingRequestContext, CodingDirectorResponse
from main.config_manager import ConfigManager, EnhancedConfig # For type hinting
from main.model_manager import ModelManager
from utils.local_llm_client import ModelResponse as LLMClientModelResponse, ModelRole as LLMClientModelRole

# --- Mocks and Fixtures ---
@pytest.fixture
def mock_config_manager():
    mock = MagicMock(spec=ConfigManager)
    # You might need to set up return values for its methods if CodingDirector uses them directly
    # For now, assuming CodingDirector primarily uses ModelManager which is configured by ConfigManager
    return mock

@pytest.fixture
def mock_model_manager():
    mock = MagicMock(spec=ModelManager)
    mock.is_initialized = True # Assume initialized for most tests
    mock.initialize_clients = AsyncMock()
    mock.get_completion_by_role = AsyncMock()
    # Mock other ModelManager methods if used by CodingDirector
    return mock

@pytest.fixture
def coding_director(mock_config_manager, mock_model_manager):
    # Initialize CodingDirector with mocked dependencies
    director = CodingDirector(config_manager=mock_config_manager, model_manager=mock_model_manager)
    director.is_initialized = True # Default to initialized for direct method tests
    return director

# Helper to create a mock LLMClientModelResponse
def create_mock_llm_response(content: str, model_name: str, role: LLMClientModelRole) -> LLMClientModelResponse:
    return LLMClientModelResponse(
        content=content, model_name=model_name, role=role,
        tokens_generated=len(content.split()), response_time_ms=50.0,
        temperature=0.5, confidence_score=0.9, metadata={}, timestamp=MagicMock()
    )

# --- Test Cases ---

@pytest.mark.asyncio
async def test_coding_director_initialization(coding_director: CodingDirector, mock_config_manager, mock_model_manager):
    assert coding_director.config_manager == mock_config_manager
    assert coding_director.model_manager == mock_model_manager
    assert coding_director.is_initialized # From fixture

@pytest.mark.asyncio
async def test_director_initialize_method(coding_director: CodingDirector, mock_model_manager: MagicMock):
    # Test the explicit initialize method
    coding_director.is_initialized = False # Set to false to test initialization path
    mock_model_manager.is_initialized = False
    mock_model_manager.initialize_clients = AsyncMock() # Reset for this test

    await coding_director.initialize()

    mock_model_manager.initialize_clients.assert_called_once()
    assert coding_director.is_initialized == mock_model_manager.is_initialized # Should reflect manager's status

@pytest.mark.asyncio
async def test_classify_task_math(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_router_response = create_mock_llm_response("math", "openhermes:7b", LLMClientModelRole.ROUTER)
    mock_model_manager.get_completion_by_role.return_value = mock_router_response

    classification = await coding_director.classify_task("Factorial of 5")

    assert classification == "math"
    mock_model_manager.get_completion_by_role.assert_called_once_with(
        role="router",
        prompt='Classify the following user request: "Factorial of 5"'
    )

@pytest.mark.asyncio
async def test_classify_task_general(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_router_response = create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER)
    mock_model_manager.get_completion_by_role.return_value = mock_router_response

    classification = await coding_director.classify_task("Explain JavaScript closures")

    assert classification == "general"

@pytest.mark.asyncio
async def test_classify_task_router_failure(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.return_value = None # Simulate router failure

    classification = await coding_director.classify_task("Some prompt")

    assert classification == "general" # Default fallback classification

@pytest.mark.asyncio
async def test_classify_task_router_unexpected_output(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_router_response = create_mock_llm_response("unexpected_output", "openhermes:7b", LLMClientModelRole.ROUTER)
    mock_model_manager.get_completion_by_role.return_value = mock_router_response

    classification = await coding_director.classify_task("Some prompt")

    assert classification == "general" # Default fallback

@pytest.mark.asyncio
async def test_process_request_math_route_success(coding_director: CodingDirector, mock_model_manager: MagicMock):
    # Mock router
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("math", "openhermes:7b", LLMClientModelRole.ROUTER), # Router classifies as math
        create_mock_llm_response("Factorial calculation...", "mathstral:7b", LLMClientModelRole.QUANTITATIVE_SPECIALIST) # Math specialist responds
    ]

    context = CodingRequestContext(user_prompt="Factorial of 5")
    response = await coding_director.process_request(context)

    assert response.classification == "math"
    assert response.final_response == "Factorial calculation..."
    assert response.model_used == "mathstral:7b"
    assert response.error_message is None

    assert mock_model_manager.get_completion_by_role.call_count == 2
    # Check router call
    assert mock_model_manager.get_completion_by_role.call_args_list[0][1]['role'] == "router"
    # Check math specialist call
    assert mock_model_manager.get_completion_by_role.call_args_list[1][1]['role'] == "math_specialist"

@pytest.mark.asyncio
async def test_process_request_general_route_success(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER),
        create_mock_llm_response("JS closures explained...", "deepseek:16b", LLMClientModelRole.LEAD_DEVELOPER)
    ]

    context = CodingRequestContext(user_prompt="Explain JS closures")
    response = await coding_director.process_request(context)

    assert response.classification == "general"
    assert response.final_response == "JS closures explained..."
    assert response.model_used == "deepseek:16b"
    assert mock_model_manager.get_completion_by_role.call_args_list[1][1]['role'] == "lead_developer"

@pytest.mark.asyncio
async def test_process_request_fallback_to_senior_developer(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER), # Router
        None, # Lead developer fails
        create_mock_llm_response("Senior dev response...", "codellama:13b", LLMClientModelRole.SENIOR_DEVELOPER) # Senior dev succeeds
    ]

    context = CodingRequestContext(user_prompt="Complex general task")
    response = await coding_director.process_request(context)

    assert response.classification == "general"
    assert response.final_response == "Senior dev response..."
    assert response.model_used == "codellama:13b"
    assert mock_model_manager.get_completion_by_role.call_count == 3
    assert mock_model_manager.get_completion_by_role.call_args_list[1][1]['role'] == "lead_developer"
    assert mock_model_manager.get_completion_by_role.call_args_list[2][1]['role'] == "senior_developer"

@pytest.mark.asyncio
async def test_process_request_fallback_to_principal_architect(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER), # Router
        None, # Lead developer fails
        None, # Senior developer fails
        create_mock_llm_response("Architect response...", "wizardcoder:13b", LLMClientModelRole.PRINCIPAL_ARCHITECT) # Architect succeeds
    ]

    context = CodingRequestContext(user_prompt="Very complex general task")
    response = await coding_director.process_request(context)

    assert response.classification == "general"
    assert response.final_response == "Architect response..."
    assert response.model_used == "wizardcoder:13b"
    assert mock_model_manager.get_completion_by_role.call_count == 4
    assert mock_model_manager.get_completion_by_role.call_args_list[3][1]['role'] == "principal_architect"

@pytest.mark.asyncio
async def test_process_request_all_models_fail(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER), # Router
        None, # Lead developer fails
        None, # Senior developer fails
        None  # Principal architect fails
    ]

    context = CodingRequestContext(user_prompt="Extremely complex task")
    response = await coding_director.process_request(context)

    assert response.classification == "general"
    assert response.final_response is None
    assert response.error_message == "All specialist models failed to provide a response."
    assert mock_model_manager.get_completion_by_role.call_count == 4

@pytest.mark.asyncio
async def test_process_request_not_initialized_and_init_fails(mock_config_manager, mock_model_manager):
    # Setup mocks for this specific scenario
    mock_model_manager.is_initialized = False
    mock_model_manager.initialize_clients = AsyncMock(side_effect=lambda: setattr(mock_model_manager, 'is_initialized', False)) # Simulate init failing to set true

    director = CodingDirector(config_manager=mock_config_manager, model_manager=mock_model_manager)
    # director.is_initialized is False by default

    context = CodingRequestContext(user_prompt="A prompt")
    response = await director.process_request(context)

    assert response.error_message == "CodingDirector and its ModelManager are not initialized."
    mock_model_manager.initialize_clients.assert_called_once() # Initialization should be attempted

@pytest.mark.asyncio
async def test_process_request_with_language_context(coding_director: CodingDirector, mock_model_manager: MagicMock):
    mock_model_manager.get_completion_by_role.side_effect = [
        create_mock_llm_response("general", "openhermes:7b", LLMClientModelRole.ROUTER),
        create_mock_llm_response("Python specific answer", "deepseek:16b", LLMClientModelRole.LEAD_DEVELOPER)
    ]

    context = CodingRequestContext(user_prompt="How to declare a variable?", language="python")
    await coding_director.process_request(context)

    # Check that the specialist prompt includes language info
    specialist_call_args = mock_model_manager.get_completion_by_role.call_args_list[1][1]
    assert specialist_call_args['role'] == "lead_developer"
    assert "Language: python" in specialist_call_args['prompt']
    assert "How to declare a variable?" in specialist_call_args['prompt']
