import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import asyncio

from utils.local_llm_client import LocalLLMClient, ModelConfig, ModelRole, ModelResponse
from main.config_manager import SystemConfig, IndividualModelConfig, ModelPerformanceConfig # For IndividualModelConfig type

# --- Fixtures ---
@pytest.fixture
def minimal_system_config_for_client():
    # LocalLLMClient expects an object with 'ollama_base_url'
    return SystemConfig(ollama_host="http://mockhost", ollama_port=12345)

@pytest.fixture
@patch('utils.local_llm_client.AsyncClient', autospec=True) # Mock the ollama.AsyncClient class
def local_llm_client_with_mocked_ollama(MockAsyncOllamaClient, minimal_system_config_for_client):
    # This provides an instance of LocalLLMClient where ollama.AsyncClient is mocked
    mock_ollama_instance = MockAsyncOllamaClient.return_value
    mock_ollama_instance.list = AsyncMock(return_value={'models': []}) # Default for connect
    mock_ollama_instance.chat = AsyncMock()
    mock_ollama_instance.embeddings = AsyncMock()

    client = LocalLLMClient(config=minimal_system_config_for_client)
    # The actual ollama.AsyncClient instance used by LocalLLMClient is mock_ollama_instance
    client.client = mock_ollama_instance # Ensure our client uses the mocked ollama instance
    return client, mock_ollama_instance # Return both client and the mocked ollama instance

@pytest.fixture
def sample_ext_model_configs():
    # Simulating IndividualModelConfig objects that ModelManager would pass
    return [
        IndividualModelConfig(name="Router", model_id="router:7b", role="router", system_prompt="Route tasks.",
                              performance=ModelPerformanceConfig(temperature=0.1, max_tokens=50, top_p=0.8, top_k=30, repeat_penalty=1.05, context_length=2000, timeout=20)),
        IndividualModelConfig(name="Coder", model_id="coder:13b", role="lead_developer", system_prompt="Code tasks.",
                              performance=ModelPerformanceConfig(temperature=0.5, max_tokens=1024, context_length=4096, timeout=45)),
    ]

# --- Test Cases ---

@pytest.mark.asyncio
async def test_prime_model_configurations(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, _ = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)

    assert len(client.models) == 2
    assert "router:7b" in client.models
    assert "coder:13b" in client.models

    router_cfg_internal = client.models["router:7b"]
    assert isinstance(router_cfg_internal, ModelConfig)
    assert router_cfg_internal.name == "router:7b"
    assert router_cfg_internal.role == ModelRole.ROUTER
    assert router_cfg_internal.temperature == 0.1
    assert router_cfg_internal.max_tokens == 50
    assert router_cfg_internal.context_window == 2000 # from context_length
    assert router_cfg_internal.enabled is True # Default from IndividualModelConfig if not specified

    assert len(client.performance_metrics) == 2
    assert "router:7b" in client.performance_metrics

@pytest.mark.asyncio
async def test_connect_success(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs) # Prime first

    # Simulate Ollama having the primed models
    mock_ollama_instance.list.return_value = {
        'models': [{'name': 'router:7b'}, {'name': 'coder:13b'}]
    }

    connected = await client.connect()
    assert connected is True
    assert client.is_connected is True
    assert client.models["router:7b"].enabled is True
    mock_ollama_instance.list.assert_called_once()

@pytest.mark.asyncio
async def test_connect_missing_models(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)

    mock_ollama_instance.list.return_value = {'models': [{'name': 'router:7b'}]} # coder:13b is missing

    connected = await client.connect() # Should return False as not all required models are present
    assert connected is False
    assert client.is_connected is True # Connection to Ollama itself was fine
    assert client.models["router:7b"].enabled is True
    assert client.models["coder:13b"].enabled is False # Should be marked as disabled

@pytest.mark.asyncio
async def test_generate_response_non_streaming(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)
    await client.connect() # To enable models

    model_name = "coder:13b"
    prompt = "Write a function."
    system_prompt = "You are a coder."

    ollama_chat_response = {
        'model': model_name,
        'created_at': datetime.now().isoformat(),
        'message': {'role': 'assistant', 'content': 'def func(): pass'},
        'done': True,
        'total_duration': 1000000000, 'load_duration': 1000000,
        'prompt_eval_count': 10, 'prompt_eval_duration': 2000000,
        'eval_count': 5, 'eval_duration': 3000000
    }
    mock_ollama_instance.chat.return_value = ollama_chat_response

    response = await client.generate_response(
        model_name=model_name,
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7, max_tokens=150, top_p=0.9, top_k=35, repeat_penalty=1.1
    )

    assert isinstance(response, ModelResponse)
    assert response.content == 'def func(): pass'
    assert response.model_name == model_name

    mock_ollama_instance.chat.assert_called_once()
    call_args = mock_ollama_instance.chat.call_args
    assert call_args[1]['model'] == model_name
    assert call_args[1]['messages'] == [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt}
    ]
    assert call_args[1]['options']['temperature'] == 0.7
    assert call_args[1]['options']['num_predict'] == 150
    assert call_args[1]['options']['top_p'] == 0.9
    assert call_args[1]['options']['top_k'] == 35
    assert call_args[1]['options']['repeat_penalty'] == 1.1
    # num_ctx comes from primed ModelConfig's context_window
    assert call_args[1]['options']['num_ctx'] == client.models[model_name].context_window


@pytest.mark.asyncio
async def test_generate_response_streaming(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)
    await client.connect()

    model_name = "coder:13b"
    async def mock_ollama_stream():
        yield {'message': {'content': 'def '}, 'done': False}
        yield {'message': {'content': 'func():'}, 'done': False}
        yield {'message': {'content': ' pass'}, 'done': True, 'eval_count': 3, 'eval_duration': 1000} # Last chunk with stats

    mock_ollama_instance.chat.return_value = mock_ollama_stream() # Return async generator

    response_gen = await client.generate_response(model_name=model_name, prompt="Stream func", stream=True)

    content_parts = []
    async for part in response_gen: # type: ignore
        content_parts.append(part)

    assert "".join(content_parts) == "def func(): pass"
    mock_ollama_instance.chat.assert_called_once()
    # Check performance metrics update after streaming
    metrics = client.performance_metrics[model_name]
    assert metrics.successful_requests == 1
    assert metrics.tokens_generated == 3 # from eval_count in last chunk

@pytest.mark.asyncio
async def test_generate_embeddings_ollama_success(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    # prime config not strictly necessary for embeddings if model_name is arbitrary, but good practice
    await client.prime_model_configurations(sample_ext_model_configs)

    texts = ["hello", "world"]
    embedding_model = "nomic-embed-text" # Or any model ID Ollama supports for embeddings

    # Simulate ollama.AsyncClient.embeddings response
    mock_ollama_instance.embeddings.side_effect = [
        {"embedding": [0.1, 0.2, 0.3]},
        {"embedding": [0.4, 0.5, 0.6]}
    ]

    embeddings = await client.generate_embeddings_ollama(model_name=embedding_model, texts=texts)

    assert embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert mock_ollama_instance.embeddings.call_count == 2
    mock_ollama_instance.embeddings.assert_any_call(model=embedding_model, prompt="hello")
    mock_ollama_instance.embeddings.assert_any_call(model=embedding_model, prompt="world")

@pytest.mark.asyncio
async def test_generate_embeddings_ollama_failure(local_llm_client_with_mocked_ollama):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama

    mock_ollama_instance.embeddings.side_effect = Exception("Ollama embedding error")

    with pytest.raises(Exception, match="Ollama embedding error"):
        await client.generate_embeddings_ollama(model_name="any_embed_model", texts=["test"])

def test_model_config_dataclass(): # Test the internal ModelConfig
    mc = ModelConfig(name="test_model", role=ModelRole.ROUTER, temperature=0.7, max_tokens=100, context_window=2048)
    assert mc.temperature == 0.7
    assert mc.max_tokens == 100
    assert mc.context_window == 2048

@pytest.mark.asyncio
async def test_health_check(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)

    mock_ollama_instance.list.return_value = {
        'models': [{'name': 'router:7b'}, {'name': 'coder:13b'}] # All models available
    }
    health = await client.health_check()
    assert health['connected'] is True
    assert health['models_available'] == 2
    assert health['models_enabled'] == 2 # Because connect() wasn't called to disable coder:13b if it were missing
    assert not health['issues']

@pytest.mark.asyncio
async def test_health_check_connection_error(local_llm_client_with_mocked_ollama):
    client, mock_ollama_instance = local_llm_client_with_mocked_ollama
    mock_ollama_instance.list.side_effect = Exception("Connection failed")

    health = await client.health_check()
    assert health['connected'] is False
    assert "Connection failed" in health['issues'][0]

@pytest.mark.asyncio
async def test_get_model_by_role(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, _ = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)
    # Assume all models are enabled after priming for this test (connect() might disable them)
    for cfg in sample_ext_model_configs: # Mark them enabled for the test
        if cfg.model_id in client.models:
            client.models[cfg.model_id].enabled = True

    router_model_name = await client.get_model_by_role(ModelRole.ROUTER)
    assert router_model_name == "router:7b"

    coder_model_name = await client.get_model_by_role(ModelRole.LEAD_DEVELOPER)
    assert coder_model_name == "coder:13b"

    non_existent_role = await client.get_model_by_role(ModelRole.SENIOR_DEVELOPER) # Not in sample_ext_model_configs
    assert non_existent_role is None

@pytest.mark.asyncio
async def test_update_performance_metrics(local_llm_client_with_mocked_ollama, sample_ext_model_configs):
    client, _ = local_llm_client_with_mocked_ollama
    await client.prime_model_configurations(sample_ext_model_configs)
    model_name = "router:7b"

    client._update_performance_metrics(model_name, True, 100.0, 10, 0.9)
    metrics = client.performance_metrics[model_name]
    assert metrics.total_requests == 1
    assert metrics.successful_requests == 1
    assert metrics.avg_response_time_ms == 100.0
    assert metrics.avg_tokens_per_second == (10 / (100.0/1000)) # 100 tps
    assert metrics.avg_confidence_score == 0.9

    client._update_performance_metrics(model_name, True, 200.0, 20, 0.7)
    metrics = client.performance_metrics[model_name]
    assert metrics.total_requests == 2
    assert metrics.successful_requests == 2
    assert pytest.approx(metrics.avg_response_time_ms) == 150.0
    # (100*1 + 200) / 2 = 150
    # TPS1 = 100, TPS2 = 20 / 0.2 = 100. Avg TPS = (100*1 + 100)/2 = 100
    assert pytest.approx(metrics.avg_tokens_per_second) == 100.0
    assert pytest.approx(metrics.avg_confidence_score) == 0.8

    client._update_performance_metrics(model_name, False)
    metrics = client.performance_metrics[model_name]
    assert metrics.total_requests == 3
    assert metrics.failed_requests == 1
    assert metrics.successful_requests == 2 # Unchanged

    await client.reset_performance_metrics(model_name)
    assert client.performance_metrics[model_name].total_requests == 0
