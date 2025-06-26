#!/usr/bin/env python3
"""
Enhanced Elite Coding Assistant - Local LLM Client
=================================================

Local Language Model client for interfacing with Ollama models.
Provides high-level abstractions for model communication, performance monitoring,
and intelligent request handling.

Author: Manus AI
Version: 2.0
Date: June 23, 2025
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
import ollama
from ollama import AsyncClient

from .config_manager import EnhancedConfig


class ModelRole(Enum):
    """Enumeration of model roles in the system."""
    ROUTER = "router"
    QUANTITATIVE_SPECIALIST = "quantitative_specialist"
    LEAD_DEVELOPER = "lead_developer"
    SENIOR_DEVELOPER = "senior_developer"
    PRINCIPAL_ARCHITECT = "principal_architect"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    role: ModelRole
    timeout: int = 30
    temperature: float = 0.3
    max_tokens: int = 2048
    context_window: int = 4096
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['role'] = self.role.value
        return data


@dataclass
class ModelResponse:
    """Response from a model interaction."""
    content: str
    model_name: str
    role: ModelRole
    tokens_generated: int
    response_time_ms: float
    temperature: float
    confidence_score: float
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['role'] = self.role.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ModelPerformanceMetrics:
    """Performance metrics for a model."""
    model_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    avg_tokens_per_second: float = 0.0
    avg_confidence_score: float = 0.0
    last_used: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        data['success_rate'] = self.success_rate
        return data


class LocalLLMClient:
    """
    High-level client for interacting with local Ollama models.
    
    Provides intelligent model management, performance monitoring,
    and robust error handling for the Enhanced Elite Coding Assistant.
    """
    
    def __init__(self, config: EnhancedConfig):
        """
        Initialize the Local LLM Client.
        
        Args:
            config: Enhanced configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Ollama client
        self.client = AsyncClient(host=config.ollama_host)
        
        # Model configurations
        self.models: Dict[str, ModelConfig] = {}
        self.performance_metrics: Dict[str, ModelPerformanceMetrics] = {}
        
        # Connection status
        self.is_connected = False
        self.last_health_check = None
        
        # Load model configurations
        self._load_model_configs()
        
        # Initialize performance tracking
        self._initialize_performance_tracking()
    
    def _load_model_configs(self):
        """Load model configurations from config."""
        model_configs = {
            "openhermes:7b": ModelConfig(
                name="openhermes:7b",
                role=ModelRole.ROUTER,
                timeout=30,
                temperature=0.3,
                max_tokens=2048
            ),
            "mathstral:7b": ModelConfig(
                name="mathstral:7b",
                role=ModelRole.QUANTITATIVE_SPECIALIST,
                timeout=45,
                temperature=0.2,
                max_tokens=4096
            ),
            "deepseek-coder-v2:16b-lite-instruct": ModelConfig(
                name="deepseek-coder-v2:16b-lite-instruct",
                role=ModelRole.LEAD_DEVELOPER,
                timeout=60,
                temperature=0.4,
                max_tokens=8192
            ),
            "codellama:13b": ModelConfig(
                name="codellama:13b",
                role=ModelRole.SENIOR_DEVELOPER,
                timeout=45,
                temperature=0.3,
                max_tokens=4096
            ),
            "wizardcoder:13b-python": ModelConfig(
                name="wizardcoder:13b-python",
                role=ModelRole.PRINCIPAL_ARCHITECT,
                timeout=60,
                temperature=0.5,
                max_tokens=8192
            )
        }
        
        # Override with config values if available
        for model_name, model_config in model_configs.items():
            config_key = model_name.split(':')[0].replace('-', '_')
            if hasattr(self.config, f'{config_key}_config'):
                config_data = getattr(self.config, f'{config_key}_config', {})
                for key, value in config_data.items():
                    if hasattr(model_config, key):
                        setattr(model_config, key, value)
            
            self.models[model_name] = model_config
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for all models."""
        for model_name in self.models.keys():
            self.performance_metrics[model_name] = ModelPerformanceMetrics(
                model_name=model_name
            )
    
    async def connect(self) -> bool:
        """
        Connect to Ollama and verify model availability.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Test connection
            models = await self.client.list()
            self.is_connected = True
            self.last_health_check = datetime.now()
            
            # Verify required models are available
            available_models = {model['name'] for model in models['models']}
            missing_models = []
            
            for model_name in self.models.keys():
                if model_name not in available_models:
                    missing_models.append(model_name)
                    self.models[model_name].enabled = False
                else:
                    self.models[model_name].enabled = True
            
            if missing_models:
                self.logger.warning(f"Missing models: {missing_models}")
                return False
            
            self.logger.info("Successfully connected to Ollama with all required models")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            self.is_connected = False
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Ollama connection and models.
        
        Returns:
            Dict containing health status information
        """
        health_status = {
            "connected": False,
            "models_available": 0,
            "models_enabled": 0,
            "last_check": datetime.now().isoformat(),
            "issues": []
        }
        
        try:
            # Check connection
            models = await self.client.list()
            health_status["connected"] = True
            
            # Check model availability
            available_models = {model['name'] for model in models['models']}
            
            for model_name, model_config in self.models.items():
                if model_name in available_models:
                    health_status["models_available"] += 1
                    if model_config.enabled:
                        health_status["models_enabled"] += 1
                else:
                    health_status["issues"].append(f"Model {model_name} not available")
            
            self.is_connected = True
            self.last_health_check = datetime.now()
            
        except Exception as e:
            health_status["issues"].append(f"Connection error: {str(e)}")
            self.is_connected = False
        
        return health_status
    
    async def generate_response(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[ModelResponse, AsyncGenerator[str, None]]:
        """
        Generate response from specified model.
        
        Args:
            model_name: Name of the model to use
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            stream: Whether to stream the response
            
        Returns:
            ModelResponse object or async generator for streaming
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_config = self.models[model_name]
        if not model_config.enabled:
            raise ValueError(f"Model {model_name} is disabled")
        
        # Prepare request parameters
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": temperature or model_config.temperature,
            "num_predict": max_tokens or model_config.max_tokens,
        }
        
        start_time = time.time()
        
        try:
            if stream:
                return self._stream_response(model_name, messages, options, start_time)
            else:
                return await self._generate_complete_response(
                    model_name, messages, options, start_time
                )
                
        except Exception as e:
            # Update performance metrics for failed request
            self._update_performance_metrics(model_name, success=False)
            self.logger.error(f"Error generating response from {model_name}: {e}")
            raise
    
    async def _generate_complete_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        options: Dict[str, Any],
        start_time: float
    ) -> ModelResponse:
        """Generate complete response (non-streaming)."""
        
        response = await self.client.chat(
            model=model_name,
            messages=messages,
            options=options
        )
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Extract response content
        content = response['message']['content']
        
        # Calculate metrics
        tokens_generated = len(content.split())  # Rough token count
        confidence_score = self._calculate_confidence_score(response)
        
        # Create response object
        model_response = ModelResponse(
            content=content,
            model_name=model_name,
            role=self.models[model_name].role,
            tokens_generated=tokens_generated,
            response_time_ms=response_time_ms,
            temperature=options.get("temperature", 0.3),
            confidence_score=confidence_score,
            metadata={
                "eval_count": response.get("eval_count", 0),
                "eval_duration": response.get("eval_duration", 0),
                "load_duration": response.get("load_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "prompt_eval_duration": response.get("prompt_eval_duration", 0),
                "total_duration": response.get("total_duration", 0)
            },
            timestamp=datetime.now()
        )
        
        # Update performance metrics
        self._update_performance_metrics(
            model_name,
            success=True,
            response_time_ms=response_time_ms,
            tokens_generated=tokens_generated,
            confidence_score=confidence_score
        )
        
        return model_response
    
    async def _stream_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        options: Dict[str, Any],
        start_time: float
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        
        full_content = ""
        
        async for chunk in await self.client.chat(
            model=model_name,
            messages=messages,
            options=options,
            stream=True
        ):
            if chunk['message']['content']:
                content_chunk = chunk['message']['content']
                full_content += content_chunk
                yield content_chunk
        
        # Update metrics after streaming is complete
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        tokens_generated = len(full_content.split())
        
        self._update_performance_metrics(
            model_name,
            success=True,
            response_time_ms=response_time_ms,
            tokens_generated=tokens_generated,
            confidence_score=0.8  # Default for streaming
        )
    
    def _calculate_confidence_score(self, response: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on response metadata.
        
        Args:
            response: Raw response from Ollama
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Basic confidence calculation based on response characteristics
        base_confidence = 0.7
        
        # Adjust based on response length
        content_length = len(response['message']['content'])
        if content_length > 100:
            base_confidence += 0.1
        elif content_length < 20:
            base_confidence -= 0.2
        
        # Adjust based on response time (faster might indicate cached/confident response)
        eval_duration = response.get("eval_duration", 0)
        if eval_duration > 0:
            tokens_per_second = response.get("eval_count", 0) / (eval_duration / 1e9)
            if tokens_per_second > 50:
                base_confidence += 0.1
            elif tokens_per_second < 10:
                base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def _update_performance_metrics(
        self,
        model_name: str,
        success: bool,
        response_time_ms: Optional[float] = None,
        tokens_generated: Optional[int] = None,
        confidence_score: Optional[float] = None
    ):
        """Update performance metrics for a model."""
        
        metrics = self.performance_metrics[model_name]
        metrics.total_requests += 1
        metrics.last_used = datetime.now()
        
        if success:
            metrics.successful_requests += 1
            
            if response_time_ms is not None:
                # Update average response time
                total_time = metrics.avg_response_time_ms * (metrics.successful_requests - 1)
                metrics.avg_response_time_ms = (total_time + response_time_ms) / metrics.successful_requests
                
                # Update tokens per second
                if tokens_generated and response_time_ms > 0:
                    tokens_per_second = tokens_generated / (response_time_ms / 1000)
                    total_tps = metrics.avg_tokens_per_second * (metrics.successful_requests - 1)
                    metrics.avg_tokens_per_second = (total_tps + tokens_per_second) / metrics.successful_requests
            
            if confidence_score is not None:
                # Update average confidence
                total_confidence = metrics.avg_confidence_score * (metrics.successful_requests - 1)
                metrics.avg_confidence_score = (total_confidence + confidence_score) / metrics.successful_requests
        else:
            metrics.failed_requests += 1
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models with their configurations.
        
        Returns:
            List of model information dictionaries
        """
        models_info = []
        
        for model_name, model_config in self.models.items():
            model_info = model_config.to_dict()
            model_info.update({
                "performance_metrics": self.performance_metrics[model_name].to_dict(),
                "available": model_config.enabled
            })
            models_info.append(model_info)
        
        return models_info
    
    async def get_model_by_role(self, role: ModelRole) -> Optional[str]:
        """
        Get model name by role.
        
        Args:
            role: Model role to search for
            
        Returns:
            Model name if found, None otherwise
        """
        for model_name, model_config in self.models.items():
            if model_config.role == role and model_config.enabled:
                return model_name
        return None
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary for all models.
        
        Returns:
            Dictionary containing performance summary
        """
        summary = {
            "total_models": len(self.models),
            "enabled_models": sum(1 for m in self.models.values() if m.enabled),
            "total_requests": sum(m.total_requests for m in self.performance_metrics.values()),
            "total_successful": sum(m.successful_requests for m in self.performance_metrics.values()),
            "overall_success_rate": 0.0,
            "models": {}
        }
        
        if summary["total_requests"] > 0:
            summary["overall_success_rate"] = summary["total_successful"] / summary["total_requests"]
        
        for model_name, metrics in self.performance_metrics.items():
            summary["models"][model_name] = metrics.to_dict()
        
        return summary
    
    async def reset_performance_metrics(self, model_name: Optional[str] = None):
        """
        Reset performance metrics.
        
        Args:
            model_name: Specific model to reset, or None for all models
        """
        if model_name:
            if model_name in self.performance_metrics:
                self.performance_metrics[model_name] = ModelPerformanceMetrics(model_name)
        else:
            for model_name in self.performance_metrics.keys():
                self.performance_metrics[model_name] = ModelPerformanceMetrics(model_name)
    
    async def shutdown(self):
        """Gracefully shutdown the client."""
        self.logger.info("Shutting down Local LLM Client")
        self.is_connected = False
        # Close any open connections if needed
        if hasattr(self.client, 'close'):
            await self.client.close()


# Utility functions for model management

async def test_model_connectivity(config: EnhancedConfig) -> Dict[str, Any]:
    """
    Test connectivity to all configured models.
    
    Args:
        config: Enhanced configuration object
        
    Returns:
        Dictionary containing test results
    """
    client = LocalLLMClient(config)
    
    try:
        connected = await client.connect()
        if not connected:
            return {"success": False, "error": "Failed to connect to Ollama"}
        
        health_status = await client.health_check()
        
        # Test each model with a simple prompt
        test_results = {}
        for model_name in client.models.keys():
            if client.models[model_name].enabled:
                try:
                    response = await client.generate_response(
                        model_name=model_name,
                        prompt="Hello, please respond with 'OK' to confirm you're working.",
                        max_tokens=10
                    )
                    test_results[model_name] = {
                        "success": True,
                        "response_time_ms": response.response_time_ms,
                        "tokens_generated": response.tokens_generated
                    }
                except Exception as e:
                    test_results[model_name] = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                test_results[model_name] = {
                    "success": False,
                    "error": "Model not available"
                }
        
        return {
            "success": True,
            "health_status": health_status,
            "model_tests": test_results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    finally:
        await client.shutdown()


async def benchmark_models(config: EnhancedConfig, test_prompt: str = None) -> Dict[str, Any]:
    """
    Benchmark all available models with a standard prompt.
    
    Args:
        config: Enhanced configuration object
        test_prompt: Custom test prompt, or None for default
        
    Returns:
        Dictionary containing benchmark results
    """
    if test_prompt is None:
        test_prompt = (
            "Write a Python function to calculate the factorial of a number. "
            "Include error handling and documentation."
        )
    
    client = LocalLLMClient(config)
    
    try:
        connected = await client.connect()
        if not connected:
            return {"success": False, "error": "Failed to connect to Ollama"}
        
        benchmark_results = {}
        
        for model_name in client.models.keys():
            if client.models[model_name].enabled:
                try:
                    response = await client.generate_response(
                        model_name=model_name,
                        prompt=test_prompt
                    )
                    
                    benchmark_results[model_name] = {
                        "success": True,
                        "response_time_ms": response.response_time_ms,
                        "tokens_generated": response.tokens_generated,
                        "confidence_score": response.confidence_score,
                        "tokens_per_second": response.tokens_generated / (response.response_time_ms / 1000),
                        "response_length": len(response.content),
                        "role": response.role.value
                    }
                    
                except Exception as e:
                    benchmark_results[model_name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return {
            "success": True,
            "test_prompt": test_prompt,
            "results": benchmark_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    finally:
        await client.shutdown()


if __name__ == "__main__":
    # Example usage and testing
    import asyncio
    from config_manager import EnhancedConfig
    
    async def main():
        config = EnhancedConfig()
        
        # Test connectivity
        print("Testing model connectivity...")
        test_results = await test_model_connectivity(config)
        print(json.dumps(test_results, indent=2))
        
        # Run benchmark
        print("\nRunning model benchmark...")
        benchmark_results = await benchmark_models(config)
        print(json.dumps(benchmark_results, indent=2))
    
    asyncio.run(main())

