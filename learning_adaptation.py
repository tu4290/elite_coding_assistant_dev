#!/usr/bin/env python3
"""
Enhanced Elite Coding Assistant - Multi-Model Learning and Adaptation Systems
============================================================================

This module implements advanced learning and adaptation systems that enable
the 5-model Elite Coding Assistant to continuously improve performance through
pattern recognition, adaptive routing, and intelligent optimization.

Author: Manus AI
Version: 2.0
Date: June 23, 2025
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from uuid import UUID
from enum import Enum
import statistics
from collections import defaultdict, deque

import numpy as np
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from .main.supabase_learning_client import SupabaseLearningClient
from .main.config_manager import EnhancedConfig


class AdaptationType(str, Enum):
    """Types of system adaptations."""
    ROUTING_OPTIMIZATION = "routing_optimization"
    PROMPT_ENHANCEMENT = "prompt_enhancement"
    PERFORMANCE_TUNING = "performance_tuning"
    THRESHOLD_ADJUSTMENT = "threshold_adjustment"
    MODEL_SELECTION = "model_selection"


class LearningMetric(str, Enum):
    """Learning metrics to track."""
    ROUTING_ACCURACY = "routing_accuracy"
    RESPONSE_QUALITY = "response_quality"
    USER_SATISFACTION = "user_satisfaction"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a model or system component."""
    success_rate: float
    avg_response_time_ms: float
    user_satisfaction: float
    accuracy_score: float
    efficiency_score: float
    sample_size: int
    last_updated: datetime


@dataclass
class LearningPattern:
    """Represents a learned pattern for routing or optimization."""
    pattern_id: str
    pattern_type: str
    conditions: Dict[str, Any]
    action: Dict[str, Any]
    confidence: float
    success_count: int
    failure_count: int
    created_at: datetime
    last_used: datetime


@dataclass
class AdaptationRecommendation:
    """Recommendation for system adaptation."""
    adaptation_type: AdaptationType
    target_component: str
    description: str
    expected_improvement: float
    confidence: float
    implementation_priority: int
    rollback_plan: Dict[str, Any]


class PerformanceTracker:
    """
    Tracks performance metrics across all models and system components.
    Provides real-time analytics and trend analysis for learning optimization.
    """
    
    def __init__(self, config: EnhancedConfig):
        """Initialize performance tracker."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Performance data storage
        self.model_metrics: Dict[str, PerformanceMetrics] = {}
        self.system_metrics: Dict[str, float] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Trend analysis
        self.trend_window_size = 50
        self.performance_thresholds = {
            LearningMetric.SUCCESS_RATE: 0.85,
            LearningMetric.USER_SATISFACTION: 4.0,
            LearningMetric.RESPONSE_TIME: 10000,  # ms
            LearningMetric.ROUTING_ACCURACY: 0.80
        }
    
    def record_interaction(self, model_name: str, response_time_ms: float,
                          success: bool, user_rating: Optional[float] = None):
        """Record an interaction for performance tracking."""
        timestamp = datetime.now()
        
        # Update model metrics
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = PerformanceMetrics(
                success_rate=0.0,
                avg_response_time_ms=0.0,
                user_satisfaction=0.0,
                accuracy_score=0.0,
                efficiency_score=0.0,
                sample_size=0,
                last_updated=timestamp
            )
        
        metrics = self.model_metrics[model_name]
        
        # Update running averages
        old_size = metrics.sample_size
        new_size = old_size + 1
        
        # Success rate
        old_success_rate = metrics.success_rate
        metrics.success_rate = (old_success_rate * old_size + (1.0 if success else 0.0)) / new_size
        
        # Response time
        old_response_time = metrics.avg_response_time_ms
        metrics.avg_response_time_ms = (old_response_time * old_size + response_time_ms) / new_size
        
        # User satisfaction (if provided)
        if user_rating is not None:
            old_satisfaction = metrics.user_satisfaction
            metrics.user_satisfaction = (old_satisfaction * old_size + user_rating) / new_size
        
        # Efficiency score (success per unit time)
        if response_time_ms > 0:
            efficiency = (1.0 if success else 0.0) / (response_time_ms / 1000)
            old_efficiency = metrics.efficiency_score
            metrics.efficiency_score = (old_efficiency * old_size + efficiency) / new_size
        
        metrics.sample_size = new_size
        metrics.last_updated = timestamp
        
        # Record in history
        self.metric_history[f"{model_name}_success_rate"].append(metrics.success_rate)
        self.metric_history[f"{model_name}_response_time"].append(response_time_ms)
        if user_rating is not None:
            self.metric_history[f"{model_name}_satisfaction"].append(user_rating)
        
        self.logger.debug(f"Recorded interaction for {model_name}: "
                         f"success={success}, time={response_time_ms}ms")
    
    def get_model_performance(self, model_name: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a specific model."""
        return self.model_metrics.get(model_name)
    
    def get_performance_trends(self, model_name: str, metric: LearningMetric) -> Dict[str, Any]:
        """Get performance trends for a model and metric."""
        history_key = f"{model_name}_{metric.value}"
        history = list(self.metric_history.get(history_key, []))
        
        if len(history) < 2:
            return {"trend": "insufficient_data", "values": history}
        
        # Calculate trend
        recent_values = history[-self.trend_window_size:]
        if len(recent_values) >= 10:
            # Linear regression for trend
            x = np.arange(len(recent_values))
            y = np.array(recent_values)
            slope = np.polyfit(x, y, 1)[0]
            
            trend = "improving" if slope > 0.01 else "declining" if slope < -0.01 else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "current_value": history[-1] if history else None,
            "average": statistics.mean(recent_values) if recent_values else None,
            "std_dev": statistics.stdev(recent_values) if len(recent_values) > 1 else None,
            "min": min(recent_values) if recent_values else None,
            "max": max(recent_values) if recent_values else None,
            "sample_size": len(recent_values)
        }
    
    def identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Identify models or metrics that are underperforming."""
        issues = []
        
        for model_name, metrics in self.model_metrics.items():
            # Check success rate
            if metrics.success_rate < self.performance_thresholds[LearningMetric.SUCCESS_RATE]:
                issues.append({
                    "model": model_name,
                    "metric": LearningMetric.SUCCESS_RATE,
                    "current_value": metrics.success_rate,
                    "threshold": self.performance_thresholds[LearningMetric.SUCCESS_RATE],
                    "severity": "high" if metrics.success_rate < 0.7 else "medium"
                })
            
            # Check response time
            if metrics.avg_response_time_ms > self.performance_thresholds[LearningMetric.RESPONSE_TIME]:
                issues.append({
                    "model": model_name,
                    "metric": LearningMetric.RESPONSE_TIME,
                    "current_value": metrics.avg_response_time_ms,
                    "threshold": self.performance_thresholds[LearningMetric.RESPONSE_TIME],
                    "severity": "high" if metrics.avg_response_time_ms > 15000 else "medium"
                })
            
            # Check user satisfaction
            if (metrics.user_satisfaction > 0 and 
                metrics.user_satisfaction < self.performance_thresholds[LearningMetric.USER_SATISFACTION]):
                issues.append({
                    "model": model_name,
                    "metric": LearningMetric.USER_SATISFACTION,
                    "current_value": metrics.user_satisfaction,
                    "threshold": self.performance_thresholds[LearningMetric.USER_SATISFACTION],
                    "severity": "high" if metrics.user_satisfaction < 3.0 else "medium"
                })
        
        return issues
    
    def get_best_performing_model(self, metric: LearningMetric) -> Optional[str]:
        """Get the best performing model for a specific metric."""
        if not self.model_metrics:
            return None
        
        best_model = None
        best_value = None
        
        for model_name, metrics in self.model_metrics.items():
            if metrics.sample_size < 5:  # Minimum sample size
                continue
            
            if metric == LearningMetric.SUCCESS_RATE:
                value = metrics.success_rate
            elif metric == LearningMetric.RESPONSE_TIME:
                value = -metrics.avg_response_time_ms  # Lower is better
            elif metric == LearningMetric.USER_SATISFACTION:
                value = metrics.user_satisfaction
            else:
                continue
            
            if best_value is None or value > best_value:
                best_value = value
                best_model = model_name
        
        return best_model


class AdaptiveRoutingEngine:
    """
    Implements adaptive routing that learns and improves over time.
    Uses machine learning techniques to optimize model selection.
    """
    
    def __init__(self, config: EnhancedConfig, supabase_client: SupabaseLearningClient):
        """Initialize adaptive routing engine."""
        self.config = config
        self.supabase_client = supabase_client
        self.logger = logging.getLogger(__name__)
        
        # Routing patterns and rules
        self.routing_patterns: Dict[str, LearningPattern] = {}
        self.routing_rules: List[Dict[str, Any]] = []
        self.pattern_cache: Dict[str, Any] = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.confidence_threshold = config.learning.confidence_threshold
        self.pattern_update_threshold = config.learning.pattern_update_threshold
        
        # Performance tracking
        self.routing_accuracy_history = deque(maxlen=1000)
        self.last_pattern_update = datetime.now()
    
    async def get_routing_decision(self, user_prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get intelligent routing decision based on learned patterns."""
        try:
            # Extract features from the request
            features = self._extract_features(user_prompt, context)
            
            # Get recommendations from learned patterns
            pattern_recommendation = await self._get_pattern_recommendation(features)
            
            # Get fallback recommendation from rules
            rule_recommendation = self._get_rule_recommendation(features)
            
            # Combine recommendations
            final_decision = self._combine_recommendations(
                pattern_recommendation, rule_recommendation, features
            )
            
            # Log decision
            self.logger.info(f"Routing decision: {final_decision['model']} "
                           f"(confidence: {final_decision['confidence']:.3f})")
            
            return final_decision
            
        except Exception as e:
            self.logger.error(f"Error in routing decision: {e}")
            return self._get_fallback_routing()
    
    def _extract_features(self, user_prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from user prompt and context."""
        prompt_lower = user_prompt.lower()
        
        # Keyword analysis
        math_keywords = ['algorithm', 'complexity', 'optimize', 'mathematical', 'calculate',
                        'sort', 'search', 'graph', 'tree', 'dynamic programming', 'recursion']
        architecture_keywords = ['design', 'architecture', 'system', 'scalable', 'microservices',
                               'pattern', 'structure', 'framework']
        debug_keywords = ['debug', 'error', 'fix', 'issue', 'problem', 'bug', 'troubleshoot']
        
        features = {
            'prompt_length': len(user_prompt),
            'word_count': len(user_prompt.split()),
            'math_score': sum(1 for kw in math_keywords if kw in prompt_lower),
            'architecture_score': sum(1 for kw in architecture_keywords if kw in prompt_lower),
            'debug_score': sum(1 for kw in debug_keywords if kw in prompt_lower),
            'has_code': '```' in user_prompt or 'def ' in user_prompt or 'function' in prompt_lower,
            'complexity_indicators': sum(1 for word in ['complex', 'advanced', 'sophisticated'] 
                                       if word in prompt_lower),
            'question_marks': user_prompt.count('?'),
            'context_type': context.get('type', 'general'),
            'domain_hints': context.get('domain_hints', []),
            'user_preferences': context.get('user_preferences', {})
        }
        
        # Calculate estimated complexity
        features['estimated_complexity'] = min(1.0, (
            features['math_score'] * 0.3 +
            features['architecture_score'] * 0.4 +
            features['complexity_indicators'] * 0.3
        ) / 5)
        
        return features
    
    async def _get_pattern_recommendation(self, features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get recommendation based on learned patterns."""
        try:
            # Create feature signature for pattern matching
            feature_signature = self._create_feature_signature(features)
            
            # Check cache first
            if feature_signature in self.pattern_cache:
                cached_result = self.pattern_cache[feature_signature]
                if (datetime.now() - cached_result['timestamp']).seconds < 300:  # 5 min cache
                    return cached_result['recommendation']
            
            # Query database for similar patterns
            keywords = []
            if features['math_score'] > 0:
                keywords.extend(['algorithm', 'mathematical'])
            if features['architecture_score'] > 0:
                keywords.extend(['architecture', 'design'])
            if features['debug_score'] > 0:
                keywords.extend(['debug', 'troubleshoot'])
            
            recommendation = await self.supabase_client.get_routing_recommendation(
                keywords=keywords,
                domain_context=features['domain_hints'],
                complexity=features['estimated_complexity']
            )
            
            if recommendation:
                model_name, confidence = recommendation
                result = {
                    'model': model_name,
                    'confidence': confidence,
                    'source': 'learned_patterns',
                    'reasoning': f"Pattern match with {confidence:.3f} confidence"
                }
                
                # Cache result
                self.pattern_cache[feature_signature] = {
                    'recommendation': result,
                    'timestamp': datetime.now()
                }
                
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting pattern recommendation: {e}")
            return None
    
    def _get_rule_recommendation(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendation based on predefined rules."""
        # Rule-based routing logic
        if features['math_score'] >= 2:
            return {
                'model': 'mathstral:7b',
                'confidence': 0.8,
                'source': 'rule_based',
                'reasoning': f"High math score: {features['math_score']}"
            }
        
        if features['architecture_score'] >= 2 or features['estimated_complexity'] > 0.7:
            return {
                'model': 'wizardcoder:13b-python',
                'confidence': 0.7,
                'source': 'rule_based',
                'reasoning': f"Architecture/complexity indicators"
            }
        
        if features['debug_score'] >= 1:
            return {
                'model': 'codellama:13b',
                'confidence': 0.6,
                'source': 'rule_based',
                'reasoning': f"Debug-related request"
            }
        
        # Default to lead developer
        return {
            'model': 'deepseek-coder-v2:16b-lite-instruct',
            'confidence': 0.5,
            'source': 'rule_based',
            'reasoning': "Default general coding model"
        }
    
    def _combine_recommendations(self, pattern_rec: Optional[Dict[str, Any]],
                               rule_rec: Dict[str, Any], 
                               features: Dict[str, Any]) -> Dict[str, Any]:
        """Combine pattern and rule recommendations."""
        if pattern_rec and pattern_rec['confidence'] >= self.confidence_threshold:
            # Use pattern recommendation if confidence is high enough
            final_decision = pattern_rec.copy()
            final_decision['fallback_models'] = self._get_fallback_models(pattern_rec['model'])
        else:
            # Use rule recommendation
            final_decision = rule_rec.copy()
            final_decision['fallback_models'] = self._get_fallback_models(rule_rec['model'])
            
            # Boost confidence if pattern agrees
            if pattern_rec and pattern_rec['model'] == rule_rec['model']:
                final_decision['confidence'] = min(1.0, rule_rec['confidence'] + 0.2)
                final_decision['reasoning'] += " (confirmed by patterns)"
        
        # Add metadata
        final_decision['features'] = features
        final_decision['timestamp'] = datetime.now().isoformat()
        
        return final_decision
    
    def _get_fallback_models(self, primary_model: str) -> List[str]:
        """Get fallback models for a primary model."""
        fallback_map = {
            'mathstral:7b': ['wizardcoder:13b-python', 'deepseek-coder-v2:16b-lite-instruct'],
            'deepseek-coder-v2:16b-lite-instruct': ['codellama:13b', 'wizardcoder:13b-python'],
            'codellama:13b': ['deepseek-coder-v2:16b-lite-instruct', 'wizardcoder:13b-python'],
            'wizardcoder:13b-python': ['deepseek-coder-v2:16b-lite-instruct', 'codellama:13b']
        }
        
        return fallback_map.get(primary_model, ['deepseek-coder-v2:16b-lite-instruct'])
    
    def _create_feature_signature(self, features: Dict[str, Any]) -> str:
        """Create a signature for feature matching."""
        key_features = [
            features['math_score'],
            features['architecture_score'],
            features['debug_score'],
            int(features['estimated_complexity'] * 10),
            len(features['domain_hints'])
        ]
        return '_'.join(map(str, key_features))
    
    def _get_fallback_routing(self) -> Dict[str, Any]:
        """Get fallback routing when all else fails."""
        return {
            'model': 'deepseek-coder-v2:16b-lite-instruct',
            'confidence': 0.3,
            'source': 'fallback',
            'reasoning': 'Fallback routing due to system error',
            'fallback_models': ['codellama:13b', 'wizardcoder:13b-python'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def update_routing_patterns(self, routing_decision: Dict[str, Any], 
                                    success: bool, user_feedback: Optional[str] = None):
        """Update routing patterns based on outcome."""
        try:
            if 'features' not in routing_decision:
                return
            
            features = routing_decision['features']
            model_used = routing_decision['model']
            
            # Extract keywords and domain context
            keywords = []
            if features['math_score'] > 0:
                keywords.extend(['algorithm', 'mathematical'])
            if features['architecture_score'] > 0:
                keywords.extend(['architecture', 'design'])
            if features['debug_score'] > 0:
                keywords.extend(['debug', 'troubleshoot'])
            
            # Update patterns in database
            await self.supabase_client.update_routing_pattern(
                keywords=keywords,
                domain_context=features['domain_hints'],
                complexity=features['estimated_complexity'],
                model_used=model_used,
                success=success
            )
            
            # Update local accuracy tracking
            self.routing_accuracy_history.append(1.0 if success else 0.0)
            
            # Clear cache to force refresh
            self.pattern_cache.clear()
            
            self.logger.info(f"Updated routing patterns: success={success}")
            
        except Exception as e:
            self.logger.error(f"Error updating routing patterns: {e}")
    
    def get_routing_accuracy(self) -> float:
        """Get current routing accuracy."""
        if not self.routing_accuracy_history:
            return 0.0
        
        return sum(self.routing_accuracy_history) / len(self.routing_accuracy_history)


class SystemAdaptationEngine:
    """
    Implements system-wide adaptations based on learning insights.
    Continuously optimizes performance through intelligent adjustments.
    """
    
    def __init__(self, config: EnhancedConfig, performance_tracker: PerformanceTracker,
                 routing_engine: AdaptiveRoutingEngine):
        """Initialize system adaptation engine."""
        self.config = config
        self.performance_tracker = performance_tracker
        self.routing_engine = routing_engine
        self.logger = logging.getLogger(__name__)
        
        # Adaptation history
        self.adaptation_history: List[Dict[str, Any]] = []
        self.last_adaptation = datetime.now()
        self.adaptation_interval = timedelta(hours=1)  # Adapt every hour
        
        # Adaptation thresholds
        self.adaptation_thresholds = {
            'performance_decline': 0.1,  # 10% decline triggers adaptation
            'accuracy_threshold': 0.75,
            'response_time_threshold': 8000,  # ms
            'satisfaction_threshold': 3.5
        }
    
    async def analyze_system_performance(self) -> List[AdaptationRecommendation]:
        """Analyze system performance and generate adaptation recommendations."""
        recommendations = []
        
        try:
            # Analyze routing performance
            routing_accuracy = self.routing_engine.get_routing_accuracy()
            if routing_accuracy < self.adaptation_thresholds['accuracy_threshold']:
                recommendations.append(AdaptationRecommendation(
                    adaptation_type=AdaptationType.ROUTING_OPTIMIZATION,
                    target_component="routing_engine",
                    description=f"Routing accuracy ({routing_accuracy:.3f}) below threshold",
                    expected_improvement=0.15,
                    confidence=0.8,
                    implementation_priority=1,
                    rollback_plan={"type": "revert_routing_rules"}
                ))
            
            # Analyze model performance
            performance_issues = self.performance_tracker.identify_performance_issues()
            for issue in performance_issues:
                if issue['metric'] == LearningMetric.RESPONSE_TIME:
                    recommendations.append(AdaptationRecommendation(
                        adaptation_type=AdaptationType.PERFORMANCE_TUNING,
                        target_component=issue['model'],
                        description=f"Response time ({issue['current_value']:.1f}ms) exceeds threshold",
                        expected_improvement=0.2,
                        confidence=0.7,
                        implementation_priority=2,
                        rollback_plan={"type": "revert_model_config"}
                    ))
                
                elif issue['metric'] == LearningMetric.SUCCESS_RATE:
                    recommendations.append(AdaptationRecommendation(
                        adaptation_type=AdaptationType.PROMPT_ENHANCEMENT,
                        target_component=issue['model'],
                        description=f"Success rate ({issue['current_value']:.3f}) below threshold",
                        expected_improvement=0.1,
                        confidence=0.6,
                        implementation_priority=1,
                        rollback_plan={"type": "revert_prompts"}
                    ))
            
            # Analyze threshold effectiveness
            if len(recommendations) == 0:
                # System is performing well, consider optimizing thresholds
                recommendations.append(AdaptationRecommendation(
                    adaptation_type=AdaptationType.THRESHOLD_ADJUSTMENT,
                    target_component="system_thresholds",
                    description="System performing well, optimize thresholds for better efficiency",
                    expected_improvement=0.05,
                    confidence=0.5,
                    implementation_priority=3,
                    rollback_plan={"type": "revert_thresholds"}
                ))
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda x: (x.implementation_priority, -x.confidence))
            
            self.logger.info(f"Generated {len(recommendations)} adaptation recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error analyzing system performance: {e}")
            return []
    
    async def implement_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Implement a specific adaptation recommendation."""
        try:
            self.logger.info(f"Implementing adaptation: {recommendation.description}")
            
            success = False
            
            if recommendation.adaptation_type == AdaptationType.ROUTING_OPTIMIZATION:
                success = await self._optimize_routing(recommendation)
            
            elif recommendation.adaptation_type == AdaptationType.PROMPT_ENHANCEMENT:
                success = await self._enhance_prompts(recommendation)
            
            elif recommendation.adaptation_type == AdaptationType.PERFORMANCE_TUNING:
                success = await self._tune_performance(recommendation)
            
            elif recommendation.adaptation_type == AdaptationType.THRESHOLD_ADJUSTMENT:
                success = await self._adjust_thresholds(recommendation)
            
            elif recommendation.adaptation_type == AdaptationType.MODEL_SELECTION:
                success = await self._optimize_model_selection(recommendation)
            
            # Record adaptation
            adaptation_record = {
                'timestamp': datetime.now().isoformat(),
                'type': recommendation.adaptation_type.value,
                'target': recommendation.target_component,
                'description': recommendation.description,
                'success': success,
                'expected_improvement': recommendation.expected_improvement,
                'confidence': recommendation.confidence
            }
            
            self.adaptation_history.append(adaptation_record)
            self.last_adaptation = datetime.now()
            
            if success:
                self.logger.info(f"Successfully implemented adaptation: {recommendation.adaptation_type}")
            else:
                self.logger.warning(f"Failed to implement adaptation: {recommendation.adaptation_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error implementing adaptation: {e}")
            return False
    
    async def _optimize_routing(self, recommendation: AdaptationRecommendation) -> bool:
        """Optimize routing algorithms and thresholds."""
        try:
            # Adjust confidence threshold based on performance
            current_threshold = self.routing_engine.confidence_threshold
            
            if self.routing_engine.get_routing_accuracy() < 0.8:
                # Lower threshold to be more aggressive with pattern matching
                new_threshold = max(0.5, current_threshold - 0.1)
            else:
                # Raise threshold to be more conservative
                new_threshold = min(0.9, current_threshold + 0.05)
            
            self.routing_engine.confidence_threshold = new_threshold
            
            self.logger.info(f"Adjusted routing confidence threshold: {current_threshold} -> {new_threshold}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing routing: {e}")
            return False
    
    async def _enhance_prompts(self, recommendation: AdaptationRecommendation) -> bool:
        """Enhance system prompts for better performance."""
        try:
            # This would implement prompt optimization logic
            # For now, we'll simulate the enhancement
            
            model_name = recommendation.target_component
            self.logger.info(f"Enhanced prompts for {model_name}")
            
            # In a real implementation, this would:
            # 1. Analyze successful vs failed interactions
            # 2. Identify prompt patterns that work better
            # 3. Update system prompts accordingly
            # 4. A/B test the new prompts
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error enhancing prompts: {e}")
            return False
    
    async def _tune_performance(self, recommendation: AdaptationRecommendation) -> bool:
        """Tune performance parameters for models."""
        try:
            model_name = recommendation.target_component
            model_config = self.config.get_model_config(model_name)
            
            if not model_config:
                return False
            
            # Adjust timeout based on performance issues
            if "response time" in recommendation.description.lower():
                # Reduce timeout to fail faster
                new_timeout = max(15, model_config.timeout_seconds - 5)
                self.config.update_model_config(model_name, timeout_seconds=new_timeout)
                
                self.logger.info(f"Reduced timeout for {model_name}: {model_config.timeout_seconds} -> {new_timeout}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tuning performance: {e}")
            return False
    
    async def _adjust_thresholds(self, recommendation: AdaptationRecommendation) -> bool:
        """Adjust system thresholds for optimization."""
        try:
            # Adjust performance thresholds based on current system performance
            current_avg_success = statistics.mean([
                metrics.success_rate for metrics in self.performance_tracker.model_metrics.values()
                if metrics.sample_size > 10
            ]) if self.performance_tracker.model_metrics else 0.8
            
            # Adjust success rate threshold
            new_threshold = max(0.7, min(0.95, current_avg_success - 0.05))
            self.performance_tracker.performance_thresholds[LearningMetric.SUCCESS_RATE] = new_threshold
            
            self.logger.info(f"Adjusted success rate threshold to {new_threshold}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adjusting thresholds: {e}")
            return False
    
    async def _optimize_model_selection(self, recommendation: AdaptationRecommendation) -> bool:
        """Optimize model selection strategies."""
        try:
            # This would implement model selection optimization
            # For now, we'll simulate the optimization
            
            self.logger.info("Optimized model selection strategies")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing model selection: {e}")
            return False
    
    async def run_adaptation_cycle(self) -> Dict[str, Any]:
        """Run a complete adaptation cycle."""
        try:
            if datetime.now() - self.last_adaptation < self.adaptation_interval:
                return {"status": "skipped", "reason": "too_soon"}
            
            # Analyze performance
            recommendations = await self.analyze_system_performance()
            
            if not recommendations:
                return {"status": "no_adaptations_needed", "recommendations": 0}
            
            # Implement top recommendations
            implemented = 0
            failed = 0
            
            for recommendation in recommendations[:3]:  # Implement top 3
                success = await self.implement_adaptation(recommendation)
                if success:
                    implemented += 1
                else:
                    failed += 1
            
            return {
                "status": "completed",
                "recommendations_analyzed": len(recommendations),
                "adaptations_implemented": implemented,
                "adaptations_failed": failed,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in adaptation cycle: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_adaptation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent adaptation history."""
        return self.adaptation_history[-limit:]
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score."""
        try:
            if not self.performance_tracker.model_metrics:
                return 0.5
            
            # Calculate weighted health score
            total_score = 0.0
            total_weight = 0.0
            
            for model_name, metrics in self.performance_tracker.model_metrics.items():
                if metrics.sample_size < 5:
                    continue
                
                # Model health score (0-1)
                model_score = (
                    metrics.success_rate * 0.4 +
                    min(1.0, 5000 / max(1, metrics.avg_response_time_ms)) * 0.3 +
                    min(1.0, metrics.user_satisfaction / 5.0) * 0.3
                )
                
                weight = min(1.0, metrics.sample_size / 100)  # Weight by sample size
                total_score += model_score * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.5
            
            health_score = total_score / total_weight
            
            # Adjust for routing accuracy
            routing_accuracy = self.routing_engine.get_routing_accuracy()
            health_score = health_score * 0.8 + routing_accuracy * 0.2
            
            return min(1.0, max(0.0, health_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 0.5


def main():
    """Example usage of the learning and adaptation systems."""
    import asyncio
    from .main.config_manager import EnhancedConfig
    from .main.supabase_learning_client import SupabaseLearningClient
    
    async def test_adaptation_systems():
        # Initialize components
        config = EnhancedConfig(
            openai_api_key="test-key",
            supabase_url="test-url",
            supabase_key="test-key"
        )
        
        supabase_client = SupabaseLearningClient(
            config.supabase_url,
            config.supabase_key,
            config.openai_api_key
        )
        
        # Initialize systems
        performance_tracker = PerformanceTracker(config)
        routing_engine = AdaptiveRoutingEngine(config, supabase_client)
        adaptation_engine = SystemAdaptationEngine(config, performance_tracker, routing_engine)
        
        # Simulate some interactions
        for i in range(10):
            performance_tracker.record_interaction(
                model_name="deepseek-coder-v2:16b-lite-instruct",
                response_time_ms=3000 + i * 100,
                success=i % 3 != 0,  # 67% success rate
                user_rating=4.0 if i % 3 != 0 else 2.0
            )
        
        # Test routing decision
        routing_decision = await routing_engine.get_routing_decision(
            "Write a Python function to implement quicksort",
            {"domain_hints": ["python", "algorithms"]}
        )
        print("Routing decision:", routing_decision)
        
        # Test adaptation cycle
        adaptation_result = await adaptation_engine.run_adaptation_cycle()
        print("Adaptation result:", adaptation_result)
        
        # Get system health
        health_score = adaptation_engine.get_system_health_score()
        print(f"System health score: {health_score:.3f}")
        
        # Get performance insights
        for model_name in ["deepseek-coder-v2:16b-lite-instruct"]:
            metrics = performance_tracker.get_model_performance(model_name)
            if metrics:
                print(f"{model_name} metrics:", asdict(metrics))
    
    asyncio.run(test_adaptation_systems())


if __name__ == "__main__":
    main()

