"""Advanced Metrics and KPI System for Recursive Learning.

This module implements comprehensive metrics collection, analysis, and KPI tracking
for the Elite Coding Assistant's recursive learning and adaptation system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import json
import math
from abc import ABC, abstractmethod


class MetricCategory(Enum):
    """Categories of metrics."""
    PERFORMANCE = "performance"
    LEARNING = "learning"
    ADAPTATION = "adaptation"
    USER_EXPERIENCE = "user_experience"
    SYSTEM_HEALTH = "system_health"
    BUSINESS = "business"


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"  # Cumulative count
    GAUGE = "gauge"  # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    RATE = "rate"  # Rate of change
    RATIO = "ratio"  # Ratio between two values
    TREND = "trend"  # Trend analysis


class AggregationMethod(Enum):
    """Methods for aggregating metric values."""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    COUNT = "count"
    RATE = "rate"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    category: MetricCategory
    metric_type: MetricType
    description: str
    unit: str
    aggregation_method: AggregationMethod
    tags: Dict[str, str] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    retention_period: timedelta = field(default_factory=lambda: timedelta(days=30))


@dataclass
class MetricValue:
    """A single metric value."""
    metric_name: str
    value: Union[float, int]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPIDefinition:
    """Definition of a Key Performance Indicator."""
    name: str
    description: str
    target_value: float
    metric_dependencies: List[str]
    calculation_formula: str
    weight: float = 1.0
    category: MetricCategory = MetricCategory.PERFORMANCE
    update_frequency: timedelta = field(default_factory=lambda: timedelta(minutes=5))


@dataclass
class KPIValue:
    """A KPI value with context."""
    kpi_name: str
    value: float
    target_value: float
    achievement_percentage: float
    timestamp: datetime
    contributing_metrics: Dict[str, float] = field(default_factory=dict)
    trend: str = "stable"  # improving, declining, stable


@dataclass
class Alert:
    """System alert based on metrics."""
    id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False


class MetricCollector(ABC):
    """Abstract base class for metric collectors."""
    
    @abstractmethod
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect metrics from the source."""
        pass


class PerformanceMetricCollector(MetricCollector):
    """Collector for performance metrics."""
    
    def __init__(self, performance_tracker):
        self.performance_tracker = performance_tracker
    
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect performance metrics."""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # Collect model performance metrics
            for model_name, model_metrics in self.performance_tracker.model_metrics.items():
                metrics.extend([
                    MetricValue(
                        metric_name="model_success_rate",
                        value=model_metrics.success_rate,
                        timestamp=timestamp,
                        tags={"model": model_name}
                    ),
                    MetricValue(
                        metric_name="model_response_time",
                        value=model_metrics.avg_response_time_ms,
                        timestamp=timestamp,
                        tags={"model": model_name}
                    ),
                    MetricValue(
                        metric_name="model_user_satisfaction",
                        value=model_metrics.user_satisfaction,
                        timestamp=timestamp,
                        tags={"model": model_name}
                    ),
                    MetricValue(
                        metric_name="model_sample_size",
                        value=model_metrics.sample_size,
                        timestamp=timestamp,
                        tags={"model": model_name}
                    )
                ])
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error collecting performance metrics: {e}")
            return []


class LearningMetricCollector(MetricCollector):
    """Collector for learning metrics."""
    
    def __init__(self, learning_engine):
        self.learning_engine = learning_engine
    
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect learning metrics."""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # Collect learning state metrics
            learning_state = self.learning_engine.learning_state
            metrics.extend([
                MetricValue(
                    metric_name="learning_rate",
                    value=learning_state.learning_rate,
                    timestamp=timestamp
                ),
                MetricValue(
                    metric_name="confidence_level",
                    value=learning_state.confidence_level,
                    timestamp=timestamp
                ),
                MetricValue(
                    metric_name="meta_learning_score",
                    value=learning_state.meta_learning_score,
                    timestamp=timestamp
                ),
                MetricValue(
                    metric_name="adaptation_cycles",
                    value=learning_state.adaptation_cycles,
                    timestamp=timestamp
                )
            ])
            
            # Collect pattern metrics
            total_patterns = len(self.learning_engine.learning_patterns)
            active_patterns = len([p for p in self.learning_engine.learning_patterns.values() if p.effectiveness_score > 0.5])
            
            metrics.extend([
                MetricValue(
                    metric_name="total_learning_patterns",
                    value=total_patterns,
                    timestamp=timestamp
                ),
                MetricValue(
                    metric_name="active_learning_patterns",
                    value=active_patterns,
                    timestamp=timestamp
                ),
                MetricValue(
                    metric_name="pattern_effectiveness_ratio",
                    value=active_patterns / max(1, total_patterns),
                    timestamp=timestamp
                )
            ])
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error collecting learning metrics: {e}")
            return []


class AdaptationMetricCollector(MetricCollector):
    """Collector for adaptation metrics."""
    
    def __init__(self, adaptation_engine):
        self.adaptation_engine = adaptation_engine
    
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect adaptation metrics."""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # Collect system health score
            health_score = self.adaptation_engine.get_system_health_score()
            metrics.append(MetricValue(
                metric_name="system_health_score",
                value=health_score,
                timestamp=timestamp
            ))
            
            # Collect adaptation history metrics
            adaptation_history = self.adaptation_engine.get_adaptation_history()
            if adaptation_history:
                recent_adaptations = len([a for a in adaptation_history if datetime.now() - a.get('timestamp', datetime.min) < timedelta(hours=24)])
                metrics.append(MetricValue(
                    metric_name="daily_adaptations",
                    value=recent_adaptations,
                    timestamp=timestamp
                ))
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error collecting adaptation metrics: {e}")
            return []


class AdvancedMetricsSystem:
    """Advanced metrics and KPI tracking system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the advanced metrics system."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Metric storage
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_values: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # KPI storage
        self.kpi_definitions: Dict[str, KPIDefinition] = {}
        self.kpi_values: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Alert system
        self.alerts: deque = deque(maxlen=1000)
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Metric collectors
        self.collectors: List[MetricCollector] = []
        
        # Background tasks
        self.collection_task: Optional[asyncio.Task] = None
        self.aggregation_task: Optional[asyncio.Task] = None
        self.kpi_calculation_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Initialize default metrics and KPIs
        self._initialize_default_metrics()
        self._initialize_default_kpis()
        self._initialize_default_alerts()
    
    def _initialize_default_metrics(self):
        """Initialize default metric definitions."""
        # Performance metrics
        self.metric_definitions.update({
            "model_success_rate": MetricDefinition(
                name="model_success_rate",
                category=MetricCategory.PERFORMANCE,
                metric_type=MetricType.GAUGE,
                description="Success rate of model responses",
                unit="percentage",
                aggregation_method=AggregationMethod.AVERAGE,
                thresholds={"warning": 0.8, "critical": 0.7}
            ),
            "model_response_time": MetricDefinition(
                name="model_response_time",
                category=MetricCategory.PERFORMANCE,
                metric_type=MetricType.HISTOGRAM,
                description="Model response time",
                unit="milliseconds",
                aggregation_method=AggregationMethod.PERCENTILE_95,
                thresholds={"warning": 2000, "critical": 5000}
            ),
            "model_user_satisfaction": MetricDefinition(
                name="model_user_satisfaction",
                category=MetricCategory.USER_EXPERIENCE,
                metric_type=MetricType.GAUGE,
                description="User satisfaction score",
                unit="score",
                aggregation_method=AggregationMethod.AVERAGE,
                thresholds={"warning": 0.7, "critical": 0.6}
            ),
            "learning_rate": MetricDefinition(
                name="learning_rate",
                category=MetricCategory.LEARNING,
                metric_type=MetricType.GAUGE,
                description="Current learning rate",
                unit="rate",
                aggregation_method=AggregationMethod.AVERAGE
            ),
            "confidence_level": MetricDefinition(
                name="confidence_level",
                category=MetricCategory.LEARNING,
                metric_type=MetricType.GAUGE,
                description="System confidence level",
                unit="score",
                aggregation_method=AggregationMethod.AVERAGE,
                thresholds={"warning": 0.6, "critical": 0.4}
            ),
            "system_health_score": MetricDefinition(
                name="system_health_score",
                category=MetricCategory.SYSTEM_HEALTH,
                metric_type=MetricType.GAUGE,
                description="Overall system health score",
                unit="score",
                aggregation_method=AggregationMethod.AVERAGE,
                thresholds={"warning": 0.7, "critical": 0.5}
            ),
            "total_learning_patterns": MetricDefinition(
                name="total_learning_patterns",
                category=MetricCategory.LEARNING,
                metric_type=MetricType.GAUGE,
                description="Total number of learning patterns",
                unit="count",
                aggregation_method=AggregationMethod.MAX
            ),
            "active_learning_patterns": MetricDefinition(
                name="active_learning_patterns",
                category=MetricCategory.LEARNING,
                metric_type=MetricType.GAUGE,
                description="Number of active learning patterns",
                unit="count",
                aggregation_method=AggregationMethod.MAX
            ),
            "daily_adaptations": MetricDefinition(
                name="daily_adaptations",
                category=MetricCategory.ADAPTATION,
                metric_type=MetricType.COUNTER,
                description="Number of adaptations in the last 24 hours",
                unit="count",
                aggregation_method=AggregationMethod.SUM
            )
        })
    
    def _initialize_default_kpis(self):
        """Initialize default KPI definitions."""
        self.kpi_definitions.update({
            "overall_system_performance": KPIDefinition(
                name="overall_system_performance",
                description="Overall system performance score",
                target_value=0.9,
                metric_dependencies=["model_success_rate", "model_response_time", "model_user_satisfaction"],
                calculation_formula="weighted_average",
                weight=1.0,
                category=MetricCategory.PERFORMANCE
            ),
            "learning_effectiveness": KPIDefinition(
                name="learning_effectiveness",
                description="Effectiveness of learning and adaptation",
                target_value=0.8,
                metric_dependencies=["confidence_level", "pattern_effectiveness_ratio", "meta_learning_score"],
                calculation_formula="weighted_average",
                weight=0.8,
                category=MetricCategory.LEARNING
            ),
            "system_stability": KPIDefinition(
                name="system_stability",
                description="System stability and health",
                target_value=0.95,
                metric_dependencies=["system_health_score", "model_success_rate"],
                calculation_formula="minimum",
                weight=1.0,
                category=MetricCategory.SYSTEM_HEALTH
            ),
            "adaptation_agility": KPIDefinition(
                name="adaptation_agility",
                description="System's ability to adapt quickly",
                target_value=0.7,
                metric_dependencies=["daily_adaptations", "learning_rate"],
                calculation_formula="normalized_sum",
                weight=0.6,
                category=MetricCategory.ADAPTATION
            )
        })
    
    def _initialize_default_alerts(self):
        """Initialize default alert rules."""
        self.alert_rules.update({
            "low_success_rate": {
                "metric": "model_success_rate",
                "condition": "below",
                "threshold": 0.7,
                "severity": AlertSeverity.CRITICAL,
                "message": "Model success rate has dropped below 70%"
            },
            "high_response_time": {
                "metric": "model_response_time",
                "condition": "above",
                "threshold": 5000,
                "severity": AlertSeverity.WARNING,
                "message": "Model response time exceeds 5 seconds"
            },
            "low_confidence": {
                "metric": "confidence_level",
                "condition": "below",
                "threshold": 0.4,
                "severity": AlertSeverity.CRITICAL,
                "message": "System confidence level is critically low"
            },
            "poor_system_health": {
                "metric": "system_health_score",
                "condition": "below",
                "threshold": 0.5,
                "severity": AlertSeverity.EMERGENCY,
                "message": "System health score is critically low"
            }
        })
    
    def add_collector(self, collector: MetricCollector):
        """Add a metric collector."""
        self.collectors.append(collector)
        self.logger.info(f"Added metric collector: {type(collector).__name__}")
    
    async def start(self):
        """Start the metrics system."""
        if not self.running:
            self.running = True
            
            # Start background tasks
            self.collection_task = asyncio.create_task(self._collection_loop())
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
            self.kpi_calculation_task = asyncio.create_task(self._kpi_calculation_loop())
            
            self.logger.info("Advanced metrics system started")
    
    async def stop(self):
        """Stop the metrics system."""
        self.running = False
        
        # Cancel background tasks
        for task in [self.collection_task, self.aggregation_task, self.kpi_calculation_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("Advanced metrics system stopped")
    
    async def _collection_loop(self):
        """Background loop for collecting metrics."""
        while self.running:
            try:
                # Collect metrics from all collectors
                for collector in self.collectors:
                    metrics = await collector.collect_metrics()
                    for metric in metrics:
                        await self._store_metric(metric)
                
                # Sleep before next collection
                await asyncio.sleep(self.config.get("collection_interval", 30))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _aggregation_loop(self):
        """Background loop for aggregating metrics."""
        while self.running:
            try:
                await self._aggregate_metrics()
                await self._check_alerts()
                
                # Sleep before next aggregation
                await asyncio.sleep(self.config.get("aggregation_interval", 60))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(120)
    
    async def _kpi_calculation_loop(self):
        """Background loop for calculating KPIs."""
        while self.running:
            try:
                await self._calculate_kpis()
                
                # Sleep before next calculation
                await asyncio.sleep(self.config.get("kpi_calculation_interval", 300))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in KPI calculation loop: {e}")
                await asyncio.sleep(300)
    
    async def _store_metric(self, metric: MetricValue):
        """Store a metric value."""
        try:
            self.metric_values[metric.metric_name].append(metric)
            
            # Clean up old metrics based on retention period
            if metric.metric_name in self.metric_definitions:
                retention_period = self.metric_definitions[metric.metric_name].retention_period
                cutoff_time = datetime.now() - retention_period
                
                # Remove old metrics
                while (self.metric_values[metric.metric_name] and 
                       self.metric_values[metric.metric_name][0].timestamp < cutoff_time):
                    self.metric_values[metric.metric_name].popleft()
            
        except Exception as e:
            self.logger.error(f"Error storing metric {metric.metric_name}: {e}")
    
    async def _aggregate_metrics(self):
        """Aggregate metrics according to their definitions."""
        try:
            for metric_name, definition in self.metric_definitions.items():
                if metric_name in self.metric_values and self.metric_values[metric_name]:
                    values = [m.value for m in self.metric_values[metric_name]]
                    
                    # Calculate aggregated value
                    aggregated_value = self._calculate_aggregation(values, definition.aggregation_method)
                    
                    # Store aggregated value
                    self.aggregated_metrics[metric_name] = {
                        "value": aggregated_value,
                        "timestamp": datetime.now().isoformat(),
                        "sample_count": len(values)
                    }
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {e}")
    
    def _calculate_aggregation(self, values: List[float], method: AggregationMethod) -> float:
        """Calculate aggregated value using specified method."""
        if not values:
            return 0.0
        
        if method == AggregationMethod.SUM:
            return sum(values)
        elif method == AggregationMethod.AVERAGE:
            return statistics.mean(values)
        elif method == AggregationMethod.MEDIAN:
            return statistics.median(values)
        elif method == AggregationMethod.MIN:
            return min(values)
        elif method == AggregationMethod.MAX:
            return max(values)
        elif method == AggregationMethod.PERCENTILE_95:
            return self._percentile(values, 95)
        elif method == AggregationMethod.PERCENTILE_99:
            return self._percentile(values, 99)
        elif method == AggregationMethod.COUNT:
            return len(values)
        elif method == AggregationMethod.RATE:
            # Calculate rate per minute
            if len(values) >= 2:
                time_span = (datetime.now() - datetime.now().replace(minute=0, second=0, microsecond=0)).total_seconds() / 60
                return len(values) / max(1, time_span)
            return 0.0
        else:
            return statistics.mean(values)
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(math.floor(index))
            upper_index = int(math.ceil(index))
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def _calculate_kpis(self):
        """Calculate KPI values."""
        try:
            for kpi_name, definition in self.kpi_definitions.items():
                kpi_value = await self._calculate_single_kpi(definition)
                if kpi_value is not None:
                    self.kpi_values[kpi_name].append(kpi_value)
            
        except Exception as e:
            self.logger.error(f"Error calculating KPIs: {e}")
    
    async def _calculate_single_kpi(self, definition: KPIDefinition) -> Optional[KPIValue]:
        """Calculate a single KPI value."""
        try:
            # Get dependent metric values
            metric_values = {}
            for metric_name in definition.metric_dependencies:
                if metric_name in self.aggregated_metrics:
                    metric_values[metric_name] = self.aggregated_metrics[metric_name]["value"]
                else:
                    # If any dependency is missing, skip KPI calculation
                    return None
            
            # Calculate KPI based on formula
            kpi_value = self._apply_kpi_formula(definition.calculation_formula, metric_values)
            
            # Calculate achievement percentage
            achievement_percentage = (kpi_value / definition.target_value) * 100
            
            # Determine trend
            trend = self._calculate_kpi_trend(definition.name, kpi_value)
            
            return KPIValue(
                kpi_name=definition.name,
                value=kpi_value,
                target_value=definition.target_value,
                achievement_percentage=achievement_percentage,
                timestamp=datetime.now(),
                contributing_metrics=metric_values,
                trend=trend
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating KPI {definition.name}: {e}")
            return None
    
    def _apply_kpi_formula(self, formula: str, metric_values: Dict[str, float]) -> float:
        """Apply KPI calculation formula."""
        if formula == "weighted_average":
            # Simple average for now, could be enhanced with weights
            return statistics.mean(metric_values.values())
        
        elif formula == "minimum":
            return min(metric_values.values())
        
        elif formula == "maximum":
            return max(metric_values.values())
        
        elif formula == "normalized_sum":
            # Normalize values to 0-1 range and sum
            normalized_values = [min(1.0, max(0.0, value)) for value in metric_values.values()]
            return sum(normalized_values) / len(normalized_values)
        
        else:
            # Default to average
            return statistics.mean(metric_values.values())
    
    def _calculate_kpi_trend(self, kpi_name: str, current_value: float) -> str:
        """Calculate KPI trend based on historical values."""
        if kpi_name not in self.kpi_values or len(self.kpi_values[kpi_name]) < 2:
            return "stable"
        
        recent_values = [kpi.value for kpi in list(self.kpi_values[kpi_name])[-5:]]
        
        if len(recent_values) < 2:
            return "stable"
        
        # Simple trend calculation
        recent_avg = statistics.mean(recent_values[:-1])
        
        if current_value > recent_avg * 1.05:  # 5% improvement threshold
            return "improving"
        elif current_value < recent_avg * 0.95:  # 5% decline threshold
            return "declining"
        else:
            return "stable"
    
    async def _check_alerts(self):
        """Check for alert conditions."""
        try:
            for alert_name, rule in self.alert_rules.items():
                metric_name = rule["metric"]
                
                if metric_name in self.aggregated_metrics:
                    current_value = self.aggregated_metrics[metric_name]["value"]
                    threshold = rule["threshold"]
                    condition = rule["condition"]
                    
                    alert_triggered = False
                    
                    if condition == "above" and current_value > threshold:
                        alert_triggered = True
                    elif condition == "below" and current_value < threshold:
                        alert_triggered = True
                    elif condition == "equals" and abs(current_value - threshold) < 0.001:
                        alert_triggered = True
                    
                    if alert_triggered:
                        alert = Alert(
                            id=f"{alert_name}_{datetime.now().isoformat()}",
                            metric_name=metric_name,
                            severity=rule["severity"],
                            message=rule["message"],
                            value=current_value,
                            threshold=threshold,
                            timestamp=datetime.now()
                        )
                        
                        self.alerts.append(alert)
                        self.logger.warning(f"Alert triggered: {alert.message} (Value: {current_value}, Threshold: {threshold})")
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def get_metric_value(self, metric_name: str, aggregated: bool = True) -> Optional[Union[float, List[MetricValue]]]:
        """Get metric value(s)."""
        if aggregated and metric_name in self.aggregated_metrics:
            return self.aggregated_metrics[metric_name]["value"]
        elif not aggregated and metric_name in self.metric_values:
            return list(self.metric_values[metric_name])
        else:
            return None
    
    def get_kpi_value(self, kpi_name: str) -> Optional[KPIValue]:
        """Get latest KPI value."""
        if kpi_name in self.kpi_values and self.kpi_values[kpi_name]:
            return self.kpi_values[kpi_name][-1]
        return None
    
    def get_all_kpis(self) -> Dict[str, KPIValue]:
        """Get all current KPI values."""
        kpis = {}
        for kpi_name in self.kpi_definitions.keys():
            kpi_value = self.get_kpi_value(kpi_name)
            if kpi_value:
                kpis[kpi_name] = kpi_value
        return kpis
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "total_defined": len(self.metric_definitions),
                    "total_collected": sum(len(values) for values in self.metric_values.values()),
                    "categories": {}
                },
                "kpis": {
                    "total_defined": len(self.kpi_definitions),
                    "current_values": {},
                    "achievement_summary": {}
                },
                "alerts": {
                    "total": len(self.alerts),
                    "active": len(self.get_active_alerts()),
                    "by_severity": {}
                },
                "system_health": self._calculate_overall_health()
            }
            
            # Categorize metrics
            for category in MetricCategory:
                category_metrics = [name for name, defn in self.metric_definitions.items() if defn.category == category]
                summary["metrics"]["categories"][category.value] = {
                    "count": len(category_metrics),
                    "metrics": category_metrics
                }
            
            # KPI summary
            all_kpis = self.get_all_kpis()
            for kpi_name, kpi_value in all_kpis.items():
                summary["kpis"]["current_values"][kpi_name] = {
                    "value": kpi_value.value,
                    "target": kpi_value.target_value,
                    "achievement": kpi_value.achievement_percentage,
                    "trend": kpi_value.trend
                }
            
            # Achievement summary
            if all_kpis:
                achievements = [kpi.achievement_percentage for kpi in all_kpis.values()]
                summary["kpis"]["achievement_summary"] = {
                    "average": statistics.mean(achievements),
                    "min": min(achievements),
                    "max": max(achievements),
                    "above_target": len([a for a in achievements if a >= 100])
                }
            
            # Alert summary by severity
            for severity in AlertSeverity:
                count = len([alert for alert in self.get_active_alerts() if alert.severity == severity])
                summary["alerts"]["by_severity"][severity.value] = count
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating metrics summary: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health score."""
        try:
            health_metrics = [
                "system_health_score",
                "model_success_rate",
                "confidence_level"
            ]
            
            health_values = []
            for metric in health_metrics:
                value = self.get_metric_value(metric)
                if value is not None:
                    health_values.append(value)
            
            if health_values:
                overall_score = statistics.mean(health_values)
                
                if overall_score >= 0.8:
                    status = "excellent"
                elif overall_score >= 0.7:
                    status = "good"
                elif overall_score >= 0.6:
                    status = "fair"
                elif overall_score >= 0.4:
                    status = "poor"
                else:
                    status = "critical"
                
                return {
                    "overall_score": overall_score,
                    "status": status,
                    "contributing_metrics": len(health_values),
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {
                    "overall_score": 0.0,
                    "status": "unknown",
                    "contributing_metrics": 0,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error calculating overall health: {e}")
            return {"error": str(e)}
    
    def export_metrics(self, format: str = "json", time_range: Optional[Tuple[datetime, datetime]] = None) -> str:
        """Export metrics in specified format."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "time_range": {
                    "start": time_range[0].isoformat() if time_range else None,
                    "end": time_range[1].isoformat() if time_range else None
                },
                "metrics": {},
                "kpis": {},
                "alerts": []
            }
            
            # Export metrics
            for metric_name, values in self.metric_values.items():
                filtered_values = values
                if time_range:
                    filtered_values = [v for v in values if time_range[0] <= v.timestamp <= time_range[1]]
                
                export_data["metrics"][metric_name] = [
                    {
                        "value": v.value,
                        "timestamp": v.timestamp.isoformat(),
                        "tags": v.tags,
                        "metadata": v.metadata
                    }
                    for v in filtered_values
                ]
            
            # Export KPIs
            for kpi_name, values in self.kpi_values.items():
                filtered_values = values
                if time_range:
                    filtered_values = [v for v in values if time_range[0] <= v.timestamp <= time_range[1]]
                
                export_data["kpis"][kpi_name] = [
                    {
                        "value": v.value,
                        "target_value": v.target_value,
                        "achievement_percentage": v.achievement_percentage,
                        "timestamp": v.timestamp.isoformat(),
                        "trend": v.trend,
                        "contributing_metrics": v.contributing_metrics
                    }
                    for v in filtered_values
                ]
            
            # Export alerts
            filtered_alerts = self.alerts
            if time_range:
                filtered_alerts = [a for a in self.alerts if time_range[0] <= a.timestamp <= time_range[1]]
            
            export_data["alerts"] = [
                {
                    "id": a.id,
                    "metric_name": a.metric_name,
                    "severity": a.severity.value,
                    "message": a.message,
                    "value": a.value,
                    "threshold": a.threshold,
                    "timestamp": a.timestamp.isoformat(),
                    "acknowledged": a.acknowledged,
                    "resolved": a.resolved
                }
                for a in filtered_alerts
            ]
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                return str(export_data)
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return json.dumps({"error": str(e)})


# Example usage and testing
if __name__ == "__main__":
    async def main():
        """Example usage of the advanced metrics system."""
        # Initialize metrics system
        metrics_system = AdvancedMetricsSystem()
        
        # Start the system
        await metrics_system.start()
        
        # Simulate some metric collection
        test_metrics = [
            MetricValue(
                metric_name="model_success_rate",
                value=0.85,
                timestamp=datetime.now(),
                tags={"model": "gpt-4"}
            ),
            MetricValue(
                metric_name="model_response_time",
                value=1500,
                timestamp=datetime.now(),
                tags={"model": "gpt-4"}
            ),
            MetricValue(
                metric_name="confidence_level",
                value=0.75,
                timestamp=datetime.now()
            )
        ]
        
        # Store test metrics
        for metric in test_metrics:
            await metrics_system._store_metric(metric)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get summary
        summary = metrics_system.get_metrics_summary()
        print("Metrics Summary:")
        print(json.dumps(summary, indent=2, default=str))
        
        # Get KPIs
        kpis = metrics_system.get_all_kpis()
        print("\nCurrent KPIs:")
        for kpi_name, kpi_value in kpis.items():
            print(f"{kpi_name}: {kpi_value.value:.3f} (Target: {kpi_value.target_value}, Achievement: {kpi_value.achievement_percentage:.1f}%)")
        
        # Stop the system
        await metrics_system.stop()
    
    # Run example
    asyncio.run(main())