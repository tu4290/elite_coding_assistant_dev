import json
import pytest
from pathlib import Path
from pydantic import ValidationError

from main.config_manager import ConfigManager, SystemConfig, ModelsConfig, IndividualModelConfig, EnhancedConfig

# Sample valid config data
VALID_SYSTEM_JSON = {
    "log_level": "DEBUG",
    "ollama_host": "http://127.0.0.1",
    "ollama_port": 11435
}

VALID_MODELS_JSON = {
    "router": {
        "name": "Router Model", "model_id": "openhermes:7b", "role": "router",
        "system_prompt": "Route tasks.", "priority": 1,
        "performance": {"temperature": 0.1, "max_tokens": 50}
    },
    "math_specialist": {
        "name": "Math Model", "model_id": "mathstral:7b", "role": "math_specialist",
        "system_prompt": "Solve math.", "priority": 2,
        "performance": {"temperature": 0.2, "max_tokens": 1000}
    },
    "lead_developer": {
        "name": "Lead Dev Model", "model_id": "deepseek-coder-v2:16b-lite-instruct", "role": "lead_developer",
        "system_prompt": "Code general tasks.", "priority": 1,
        "performance": {"temperature": 0.3, "max_tokens": 2000}
    },
    "senior_developer": {
        "name": "Senior Dev Model", "model_id": "codellama:13b", "role": "senior_developer",
        "system_prompt": "Code robustly.", "priority": 3,
        "performance": {"temperature": 0.2, "max_tokens": 1500}
    },
    "principal_architect": {
        "name": "Architect Model", "model_id": "wizardcoder:13b-python", "role": "principal_architect",
        "system_prompt": "Design complex systems.", "priority": 4,
        "performance": {"temperature": 0.4, "max_tokens": 3000}
    }
}

@pytest.fixture
def temp_config_files(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"

    with open(system_file, 'w') as f:
        json.dump(VALID_SYSTEM_JSON, f)
    with open(models_file, 'w') as f:
        json.dump(VALID_MODELS_JSON, f)

    return system_file, models_file

def test_config_manager_load_success(temp_config_files):
    system_file, models_file = temp_config_files
    cm = ConfigManager(system_config_path=system_file, models_config_path=models_file)
    config = cm.get_config()

    assert isinstance(config, EnhancedConfig)
    assert isinstance(config.system, SystemConfig)
    assert isinstance(config.models, ModelsConfig)
    assert config.system.log_level == "DEBUG"
    assert config.system.ollama_host == "http://127.0.0.1" # Validator prepends http if missing
    assert config.system.ollama_port == 11435
    assert config.system.ollama_base_url == "http://127.0.0.1:11435"

    assert config.models.router.name == "Router Model"
    assert config.models.math_specialist.performance.temperature == 0.2

def test_config_manager_system_file_not_found(tmp_path: Path):
    models_file = tmp_path / "config" / "models.json" # Create dummy models file
    (tmp_path / "config").mkdir()
    with open(models_file, 'w') as f: json.dump(VALID_MODELS_JSON, f)

    with pytest.raises(FileNotFoundError):
        ConfigManager(system_config_path=tmp_path / "config" / "non_existent_system.json", models_config_path=models_file)

def test_config_manager_models_file_not_found(tmp_path: Path):
    system_file = tmp_path / "config" / "system.json" # Create dummy system file
    (tmp_path / "config").mkdir()
    with open(system_file, 'w') as f: json.dump(VALID_SYSTEM_JSON, f)

    with pytest.raises(FileNotFoundError):
        ConfigManager(system_config_path=system_file, models_config_path=tmp_path / "config" / "non_existent_models.json")

def test_config_manager_invalid_system_json(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"
    with open(system_file, 'w') as f: f.write("{invalid_json_}")
    with open(models_file, 'w') as f: json.dump(VALID_MODELS_JSON, f)

    with pytest.raises(json.JSONDecodeError):
        ConfigManager(system_config_path=system_file, models_config_path=models_file)

def test_config_manager_invalid_models_json(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"
    with open(system_file, 'w') as f: json.dump(VALID_SYSTEM_JSON, f)
    with open(models_file, 'w') as f: f.write("{invalid_json_}")

    with pytest.raises(json.JSONDecodeError):
        ConfigManager(system_config_path=system_file, models_config_path=models_file)

def test_system_config_pydantic_validation(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"

    invalid_system_data = {"ollama_port": "not_an_int"} # Missing log_level, ollama_host, wrong port type
    with open(system_file, 'w') as f: json.dump(invalid_system_data, f)
    with open(models_file, 'w') as f: json.dump(VALID_MODELS_JSON, f)

    with pytest.raises(ValidationError): # Pydantic's ValidationError
        ConfigManager(system_config_path=system_file, models_config_path=models_file)

def test_models_config_pydantic_validation_missing_role(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"

    invalid_models_data = VALID_MODELS_JSON.copy()
    del invalid_models_data["router"] # Missing a required role

    with open(system_file, 'w') as f: json.dump(VALID_SYSTEM_JSON, f)
    with open(models_file, 'w') as f: json.dump(invalid_models_data, f)

    with pytest.raises(ValidationError):
        ConfigManager(system_config_path=system_file, models_config_path=models_file)

def test_models_config_pydantic_validation_bad_perf_data(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    system_file = config_dir / "system.json"
    models_file = config_dir / "models.json"

    invalid_models_data = VALID_MODELS_JSON.copy()
    invalid_models_data["router"]["performance"]["temperature"] = "not_a_float"

    with open(system_file, 'w') as f: json.dump(VALID_SYSTEM_JSON, f)
    with open(models_file, 'w') as f: json.dump(invalid_models_data, f)

    with pytest.raises(ValidationError):
        ConfigManager(system_config_path=system_file, models_config_path=models_file)

def test_get_model_config_by_role(temp_config_files):
    system_file, models_file = temp_config_files
    cm = ConfigManager(system_config_path=system_file, models_config_path=models_file)

    router_cfg = cm.get_model_config("router")
    assert router_cfg is not None
    assert router_cfg.name == "Router Model"

    non_existent_cfg = cm.get_model_config("non_existent_role")
    assert non_existent_cfg is None

def test_ollama_host_validator():
    cfg1 = SystemConfig(ollama_host="localhost", ollama_port=11434)
    assert cfg1.ollama_host == "http://localhost"
    assert cfg1.ollama_base_url == "http://localhost:11434"

    cfg2 = SystemConfig(ollama_host="http://myollama.server", ollama_port=11434)
    assert cfg2.ollama_host == "http://myollama.server"
    assert cfg2.ollama_base_url == "http://myollama.server:11434"

    cfg3 = SystemConfig(ollama_host="https://secureollama", ollama_port=443)
    assert cfg3.ollama_host == "https://secureollama"
    assert cfg3.ollama_base_url == "https://secureollama:443"

    cfg4 = SystemConfig(ollama_host="http://localhost:11434", ollama_port=11434) # Port in host
    assert cfg4.ollama_base_url == "http://localhost:11434"

    cfg5 = SystemConfig(ollama_host="http://localhost/", ollama_port=11434) # Trailing slash
    assert cfg5.ollama_base_url == "http://localhost:11434"

def test_get_all_model_configs(temp_config_files):
    system_file, models_file = temp_config_files
    cm = ConfigManager(system_config_path=system_file, models_config_path=models_file)
    all_configs = cm.get_models_config().get_all_model_configs()
    assert len(all_configs) == 5
    assert isinstance(all_configs[0], IndividualModelConfig)
    role_names = [cfg.role for cfg in all_configs]
    assert "router" in role_names
    assert "math_specialist" in role_names
    assert "lead_developer" in role_names
    assert "senior_developer" in role_names
    assert "principal_architect" in role_names

def test_default_model_performance_config():
    # Test that IndividualModelConfig gets a default ModelPerformanceConfig if none provided
    model_data_no_perf = {
        "name": "Test Model", "model_id": "test:7b", "role": "test_role",
        "system_prompt": "Test.", "priority": 1, "enabled": True
    }
    model_cfg = IndividualModelConfig(**model_data_no_perf)
    assert model_cfg.performance is not None
    assert model_cfg.performance.temperature == 0.3 # Default value
    assert model_cfg.performance.max_tokens == 2048 # Default value
    assert model_cfg.performance.timeout == 30 # Default value
    assert model_cfg.performance.context_length == 4096 # Default value
