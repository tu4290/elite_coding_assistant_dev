import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, HttpUrl, validator, Field

logger = logging.getLogger(__name__)

# --- Pydantic Models for Configuration Files ---

class SystemConfig(BaseModel):
    log_level: str = "INFO"
    log_file: str = "elite_coding_assistant.log"
    max_concurrent_requests: int = 3
    request_timeout: int = 300
    enable_metrics: bool = True
    metrics_file: str = "metrics.json"
    ollama_host: str = "http://localhost" # Changed to include scheme for ollama.AsyncClient
    ollama_port: int = 11434

    @validator('ollama_host')
    def ensure_ollama_host_scheme(cls, v):
        if not v.startswith(('http://', 'https://')):
            logger.warning(f"Ollama host '{v}' does not have a scheme. Prepending 'http://'.")
            return f"http://{v}"
        return v

    @property
    def ollama_base_url(self) -> str:
        # The ollama.AsyncClient expects host like "http://localhost:11434"
        # So, if ollama_host already contains the port, use it, otherwise append.
        if str(self.ollama_port) in self.ollama_host:
             return self.ollama_host

        # Ensure no double slashes if host ends with /
        host = self.ollama_host.rstrip('/')
        return f"{host}:{self.ollama_port}"


class ModelPerformanceConfig(BaseModel):
    temperature: float = 0.3
    max_tokens: int = 2048
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 40
    repeat_penalty: Optional[float] = 1.1
    context_length: Optional[int] = 4096
    timeout: int = 30 # Added timeout, default 30 seconds

class IndividualModelConfig(BaseModel):
    name: str # User-friendly name, e.g., "Project Manager"
    model_id: str # Ollama model ID, e.g., "openhermes:7b"
    role: str # e.g., "router", "math_specialist"
    system_prompt: str = ""
    priority: int = 1
    performance: ModelPerformanceConfig = Field(default_factory=ModelPerformanceConfig)
    enabled: bool = True

class ModelsConfig(BaseModel):
    # Using a dictionary where keys are roles, matching common access patterns
    router: IndividualModelConfig
    math_specialist: IndividualModelConfig
    lead_developer: IndividualModelConfig
    senior_developer: IndividualModelConfig
    principal_architect: IndividualModelConfig
    # Could add a Dict[str, IndividualModelConfig] for arbitrary other models if needed

    def get_model_config_by_role(self, role_name: str) -> Optional[IndividualModelConfig]:
        return getattr(self, role_name, None)

    def get_all_model_configs(self) -> List[IndividualModelConfig]:
        return [
            self.router, self.math_specialist, self.lead_developer,
            self.senior_developer, self.principal_architect
        ]

# Main configuration object that will be passed around
class EnhancedConfig(BaseModel):
    system: SystemConfig
    models: ModelsConfig
    # Add other top-level config sections here if any (e.g., database, external_apis)

class ConfigManager:
    """
    Manages loading and accessing application configurations.
    """
    def __init__(self,
                 system_config_path: Path = Path("config/system.json"),
                 models_config_path: Path = Path("config/models.json")):
        self.system_config_path = system_config_path
        self.models_config_path = models_config_path
        self.config: Optional[EnhancedConfig] = None
        self.load_config()

    def load_config(self) -> EnhancedConfig:
        try:
            with open(self.system_config_path, 'r') as f:
                system_data = json.load(f)
            system_cfg = SystemConfig(**system_data)

            with open(self.models_config_path, 'r') as f:
                models_data = json.load(f)
            # Ensure models_data is a dictionary where keys are roles
            # The Pydantic model ModelsConfig expects fields like 'router', 'math_specialist' etc.
            models_cfg = ModelsConfig(**models_data)

            self.config = EnhancedConfig(system=system_cfg, models=models_cfg)
            logger.info("Configuration loaded successfully.")
            logger.info(f"Ollama Base URL determined as: {self.config.system.ollama_base_url}")
            return self.config
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e.filename}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON configuration: {e}")
            raise
        except Exception as e: # Catch Pydantic validation errors and others
            logger.error(f"Error loading or validating configuration: {e}")
            raise

    def get_config(self) -> EnhancedConfig:
        if not self.config:
            self.load_config()
        if not self.config: # Should not happen if load_config raises on failure
            raise RuntimeError("Configuration not loaded.")
        return self.config

    def get_system_config(self) -> SystemConfig:
        return self.get_config().system

    def get_models_config(self) -> ModelsConfig:
        return self.get_config().models

    def get_model_config(self, role_name: str) -> Optional[IndividualModelConfig]:
        return self.get_models_config().get_model_config_by_role(role_name)

# Example usage (typically done once at application startup)
# if __name__ == "__main__":
#     try:
#         config_manager = ConfigManager()
#         app_config = config_manager.get_config()
#         print("System Config:", app_config.system)
#         print("Router Model Config:", app_config.models.router)
#         print("Ollama URL from config:", app_config.system.ollama_base_url)
#     except Exception as e:
#         print(f"Failed to load config: {e}")
