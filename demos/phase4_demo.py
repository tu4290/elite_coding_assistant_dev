"""Phase 4 Recursive Learning and Adaptation Demo

This demo showcases the complete Phase 4 implementation including:
- Recursive Learning Engine with self-improvement algorithms
- Enhanced Feedback Pipeline with multi-level processing
- Advanced Metrics System with real-time monitoring
- Integration Orchestrator coordinating all components

Run this demo to see the system in action and understand how
recursive learning and adaptation work in practice.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

# Import Phase 4 components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))

from recursive_learning_engine import (
    RecursiveLearningEngine, LearningPhase, MetaLearningMetric,
    LearningState, RecursiveLearningPattern, SelfImprovementAction
)
from enhanced_feedback_pipeline import (
    EnhancedFeedbackPipeline, FeedbackLevel, FeedbackType,
    FeedbackItem, FeedbackLoop, QualityAssessment
)
from advanced_metrics_system import (
    AdvancedMetricsSystem, MetricCategory, MetricType,
    PerformanceMetricCollector, LearningMetricCollector, AdaptationMetricCollector
)
from phase4_integration_orchestrator import (
    Phase4IntegrationOrchestrator, OrchestrationConfig, OrchestrationPhase,
    IntegrationStatus, OrchestrationState
)


class Phase4Demo:
    """Interactive demo for Phase 4 recursive learning and adaptation."""
    
    def __init__(self):
        """Initialize the demo."""
        self.orchestrator = None
        self.demo_data = {
            "interactions": [],
            "feedback_items": [],
            "adaptations": [],
            "insights": []
        }
        self.demo_running = False
    
    async def setup_demo(self):
        """Set up the demo environment."""
        print("🚀 Setting up Phase 4 Recursive Learning and Adaptation Demo...")
        print("=" * 70)
        
        # Create orchestrator with demo-friendly configuration
        config = OrchestrationConfig(
            orchestration_cycle_interval=timedelta(seconds=5),
            learning_cycle_interval=timedelta(seconds=2),
            feedback_processing_interval=timedelta(seconds=1),
            metrics_collection_interval=timedelta(seconds=1),
            enable_auto_adaptation=True,
            enable_recursive_optimization=True,
            min_confidence_threshold=0.7,
            max_adaptation_frequency=timedelta(minutes=1)
        )
        
        self.orchestrator = Phase4IntegrationOrchestrator(config)
        
        print("✅ Orchestrator configured")
        print(f"   - Auto-adaptation: {config.enable_auto_adaptation}")
        print(f"   - Recursive optimization: {config.enable_recursive_optimization}")
        print(f"   - Cycle interval: {config.orchestration_cycle_interval.total_seconds()}s")
        print()
    
    async def start_demo(self):
        """Start the demo system."""
        print("🔄 Starting Phase 4 system...")
        
        await self.orchestrator.start()
        self.demo_running = True
        
        state = self.orchestrator.get_orchestration_state()
        print(f"✅ System started - Status: {state.status.value}")
        print(f"   - Phase: {state.phase.value}")
        print(f"   - Health Score: {state.overall_health_score:.2f}")
        print()
    
    async def demonstrate_learning_engine(self):
        """Demonstrate the recursive learning engine."""
        print("🧠 Demonstrating Recursive Learning Engine")
        print("-" * 50)
        
        learning_engine = self.orchestrator.learning_engine
        
        # Show initial state
        initial_state = learning_engine.get_learning_state()
        print(f"Initial Learning Phase: {initial_state.current_phase.value}")
        print(f"Initial Confidence: {initial_state.confidence_level:.2f}")
        print(f"Initial Learning Rate: {initial_state.learning_rate:.2f}")
        print()
        
        # Simulate learning interactions
        print("📊 Simulating learning interactions...")
        
        interactions = [
            {"success": True, "response_time": 0.5, "user_satisfaction": 0.8, "context": "code_generation"},
            {"success": True, "response_time": 0.3, "user_satisfaction": 0.9, "context": "debugging"},
            {"success": False, "response_time": 1.2, "user_satisfaction": 0.4, "context": "optimization"},
            {"success": True, "response_time": 0.4, "user_satisfaction": 0.85, "context": "code_review"},
            {"success": True, "response_time": 0.6, "user_satisfaction": 0.75, "context": "refactoring"},
            {"success": False, "response_time": 0.9, "user_satisfaction": 0.5, "context": "architecture"},
            {"success": True, "response_time": 0.35, "user_satisfaction": 0.95, "context": "testing"},
            {"success": True, "response_time": 0.45, "user_satisfaction": 0.8, "context": "documentation"}
        ]
        
        for i, interaction in enumerate(interactions):
            print(f"   Processing interaction {i+1}: {interaction['context']} "
                  f"(Success: {interaction['success']}, Time: {interaction['response_time']}s)")
            
            await learning_engine.process_learning_cycle(interaction)
            self.demo_data["interactions"].append(interaction)
            
            await asyncio.sleep(0.5)  # Brief pause for demo effect
        
        print()
        
        # Show updated state
        updated_state = learning_engine.get_learning_state()
        print(f"Updated Learning Phase: {updated_state.current_phase.value}")
        print(f"Updated Confidence: {updated_state.confidence_level:.2f}")
        print(f"Updated Learning Rate: {updated_state.learning_rate:.2f}")
        print(f"Cycles Completed: {updated_state.cycle_count}")
        print()
        
        # Generate and execute improvement actions
        print("🔧 Generating self-improvement actions...")
        actions = await learning_engine.generate_improvement_actions()
        
        for i, action in enumerate(actions[:3]):  # Show first 3 actions
            print(f"   Action {i+1}: {action.action_type.value} - {action.description}")
            print(f"   Expected Impact: {action.expected_impact:.2f}")
            
            result = await learning_engine.execute_improvement_action(action)
            if result["success"]:
                print(f"   ✅ Executed successfully: {result['details']}")
            else:
                print(f"   ❌ Execution failed: {result['details']}")
            print()
        
        # Show learning insights
        print("💡 Learning Insights:")
        insights = await learning_engine.get_learning_insights()
        
        print(f"   Learning Effectiveness: {insights['learning_effectiveness']:.2f}")
        print(f"   Performance Trends: {len(insights['performance_trends'])} trends identified")
        print(f"   Optimization Opportunities: {len(insights['optimization_opportunities'])} found")
        print(f"   Component Health: {insights['component_health']['overall_score']:.2f}")
        
        self.demo_data["insights"].append(insights)
        print()
    
    async def demonstrate_feedback_pipeline(self):
        """Demonstrate the enhanced feedback pipeline."""
        print("💬 Demonstrating Enhanced Feedback Pipeline")
        print("-" * 50)
        
        feedback_pipeline = self.orchestrator.feedback_pipeline
        
        # Show initial pipeline status
        initial_status = feedback_pipeline.get_pipeline_status()
        print(f"Initial Pipeline Status:")
        print(f"   Total Feedback Items: {initial_status['total_feedback_items']}")
        print(f"   Active Loops: {initial_status['active_loops']}")
        print(f"   Processing Queue Size: {initial_status['processing_queue_size']}")
        print()
        
        # Add various types of feedback
        print("📝 Adding feedback items...")
        
        feedback_scenarios = [
            {
                "level": FeedbackLevel.IMMEDIATE,
                "type": FeedbackType.SYSTEM_PERFORMANCE,
                "content": "Response time for code generation is slower than expected",
                "source": "user",
                "metadata": {"response_time": 1.5, "expected_time": 0.8, "task_type": "code_generation"}
            },
            {
                "level": FeedbackLevel.TACTICAL,
                "type": FeedbackType.USER_EXPERIENCE,
                "content": "The debugging suggestions are very helpful but could be more specific",
                "source": "user",
                "metadata": {"satisfaction_score": 0.75, "specificity_rating": 0.6}
            },
            {
                "level": FeedbackLevel.STRATEGIC,
                "type": FeedbackType.SYSTEM_BEHAVIOR,
                "content": "System adaptation frequency seems too aggressive",
                "source": "system_monitor",
                "metadata": {"adaptation_frequency": 0.8, "stability_impact": 0.3}
            },
            {
                "level": FeedbackLevel.IMMEDIATE,
                "type": FeedbackType.ACCURACY,
                "content": "Code suggestions are accurate but miss edge cases",
                "source": "user",
                "metadata": {"accuracy_score": 0.85, "edge_case_coverage": 0.4}
            },
            {
                "level": FeedbackLevel.TACTICAL,
                "type": FeedbackType.LEARNING_EFFECTIVENESS,
                "content": "Learning from user corrections is improving over time",
                "source": "learning_monitor",
                "metadata": {"improvement_rate": 0.15, "correction_integration": 0.8}
            }
        ]
        
        for i, scenario in enumerate(feedback_scenarios):
            feedback_item = FeedbackItem(
                id=f"demo_feedback_{i+1}",
                level=scenario["level"],
                feedback_type=scenario["type"],
                content=scenario["content"],
                source=scenario["source"],
                timestamp=datetime.now(),
                metadata=scenario["metadata"]
            )
            
            print(f"   Adding {scenario['level'].value} feedback: {scenario['content'][:50]}...")
            await feedback_pipeline.add_feedback(feedback_item)
            self.demo_data["feedback_items"].append(scenario)
            
            await asyncio.sleep(0.3)
        
        print()
        
        # Process feedback loops
        print("🔄 Processing feedback loops...")
        loop_results = await feedback_pipeline.process_all_loops()
        
        for result in loop_results:
            print(f"   Loop {result['loop_id']}: {'✅ Converged' if result['converged'] else '🔄 Processing'} "
                  f"({result['iterations']} iterations, {len(result['actions'])} actions)")
        
        print()
        
        # Show pipeline insights
        print("📊 Pipeline Insights:")
        insights = feedback_pipeline.get_pipeline_insights()
        
        print(f"   Feedback Volume: {insights['feedback_volume']['total']} items")
        print(f"   Average Quality Score: {insights['quality_metrics']['average_quality']:.2f}")
        print(f"   Processing Efficiency: {insights['processing_efficiency']['average_processing_time']:.2f}s")
        print(f"   Convergence Rate: {insights['convergence_rates']['overall_rate']:.2f}")
        print()
    
    async def demonstrate_metrics_system(self):
        """Demonstrate the advanced metrics system."""
        print("📈 Demonstrating Advanced Metrics System")
        print("-" * 50)
        
        metrics_system = self.orchestrator.metrics_system
        
        # Show metrics summary
        summary = metrics_system.get_metrics_summary()
        print(f"Metrics System Status:")
        print(f"   Total Metrics Collected: {summary['total_metrics']}")
        print(f"   Active Collectors: {summary['active_collectors']}")
        print(f"   Collection Rate: {summary.get('collection_rate', 'N/A')} metrics/min")
        print()
        
        # Show recent metrics
        print("📊 Recent Metrics:")
        
        # Get metrics for different categories
        performance_metrics = metrics_system.get_metrics_by_category(MetricCategory.PERFORMANCE)
        learning_metrics = metrics_system.get_metrics_by_category(MetricCategory.LEARNING)
        adaptation_metrics = metrics_system.get_metrics_by_category(MetricCategory.ADAPTATION)
        
        if performance_metrics:
            latest_perf = performance_metrics[-1]
            print(f"   Performance: {latest_perf.name} = {latest_perf.value:.3f} "
                  f"(at {latest_perf.timestamp.strftime('%H:%M:%S')})")
        
        if learning_metrics:
            latest_learn = learning_metrics[-1]
            print(f"   Learning: {latest_learn.name} = {latest_learn.value:.3f} "
                  f"(at {latest_learn.timestamp.strftime('%H:%M:%S')})")
        
        if adaptation_metrics:
            latest_adapt = adaptation_metrics[-1]
            print(f"   Adaptation: {latest_adapt.name} = {latest_adapt.value:.3f} "
                  f"(at {latest_adapt.timestamp.strftime('%H:%M:%S')})")
        
        print()
        
        # Show KPIs
        print("🎯 Key Performance Indicators:")
        kpis = metrics_system.get_all_kpis()
        
        for kpi in kpis[-5:]:  # Show last 5 KPIs
            status = "🟢" if kpi.value >= kpi.target_value else "🟡" if kpi.value >= kpi.target_value * 0.8 else "🔴"
            print(f"   {status} {kpi.name}: {kpi.value:.3f} (target: {kpi.target_value:.3f})")
        
        print()
        
        # Show alerts if any
        alerts = metrics_system.get_active_alerts()
        if alerts:
            print("🚨 Active Alerts:")
            for alert in alerts[-3:]:  # Show last 3 alerts
                severity_icon = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴", "CRITICAL": "🚨"}
                icon = severity_icon.get(alert.severity.value, "⚠️")
                print(f"   {icon} {alert.message} (triggered at {alert.timestamp.strftime('%H:%M:%S')})")
        else:
            print("✅ No active alerts")
        
        print()
    
    async def demonstrate_adaptation_cycle(self):
        """Demonstrate a complete adaptation cycle."""
        print("🔄 Demonstrating Adaptation Cycle")
        print("-" * 50)
        
        # Show pre-adaptation state
        pre_state = self.orchestrator.get_orchestration_state()
        print(f"Pre-Adaptation State:")
        print(f"   Health Score: {pre_state.overall_health_score:.2f}")
        print(f"   Cycle Count: {pre_state.cycle_count}")
        print(f"   Last Adaptation: {pre_state.last_adaptation_time or 'Never'}")
        print()
        
        # Force an adaptation cycle
        print("🚀 Forcing adaptation cycle...")
        adaptation_result = await self.orchestrator.force_adaptation_cycle()
        
        if adaptation_result["success"]:
            print("✅ Adaptation cycle completed successfully")
            
            if "adaptation_results" in adaptation_result:
                results = adaptation_result["adaptation_results"]
                print(f"   Adaptations Applied: {len(results.get('adaptations_applied', []))}")
                print(f"   Performance Improvement: {results.get('performance_improvement', 0):.3f}")
                print(f"   System Health Change: {results.get('health_score_change', 0):.3f}")
                
                # Show specific adaptations
                for adaptation in results.get('adaptations_applied', [])[:3]:
                    print(f"   - {adaptation.get('type', 'Unknown')}: {adaptation.get('description', 'No description')}")
        else:
            print("❌ Adaptation cycle failed")
            print(f"   Reason: {adaptation_result.get('error', 'Unknown error')}")
        
        print()
        
        # Show post-adaptation state
        post_state = self.orchestrator.get_orchestration_state()
        print(f"Post-Adaptation State:")
        print(f"   Health Score: {post_state.overall_health_score:.2f} "
              f"(Δ {post_state.overall_health_score - pre_state.overall_health_score:+.3f})")
        print(f"   Cycle Count: {post_state.cycle_count}")
        print(f"   Last Adaptation: {post_state.last_adaptation_time}")
        
        self.demo_data["adaptations"].append({
            "timestamp": datetime.now(),
            "pre_health": pre_state.overall_health_score,
            "post_health": post_state.overall_health_score,
            "success": adaptation_result["success"]
        })
        
        print()
    
    async def demonstrate_system_health(self):
        """Demonstrate system health monitoring."""
        print("🏥 Demonstrating System Health Monitoring")
        print("-" * 50)
        
        health_summary = self.orchestrator.get_system_health_summary()
        
        print(f"Overall System Health:")
        print(f"   Health Score: {health_summary['overall_health_score']:.2f}/1.00")
        print(f"   Learning Effectiveness: {health_summary['learning_effectiveness']:.2f}")
        print(f"   Adaptation Success Rate: {health_summary['adaptation_success_rate']:.2f}")
        print(f"   Feedback Processing Rate: {health_summary['feedback_processing_rate']:.2f}")
        print(f"   System Stability: {health_summary['system_stability']:.2f}")
        print()
        
        # Component health breakdown
        print(f"Component Health Breakdown:")
        for component, health in health_summary.get('component_health', {}).items():
            status_icon = "🟢" if health >= 0.8 else "🟡" if health >= 0.6 else "🔴"
            print(f"   {status_icon} {component.replace('_', ' ').title()}: {health:.2f}")
        
        print()
        
        # Recent performance trends
        if 'performance_trends' in health_summary:
            print(f"Performance Trends:")
            for trend in health_summary['performance_trends'][-3:]:
                direction = "📈" if trend['direction'] == 'improving' else "📉" if trend['direction'] == 'declining' else "➡️"
                print(f"   {direction} {trend['metric']}: {trend['direction']} ({trend['change']:+.2f})")
        
        print()
    
    async def generate_final_report(self):
        """Generate and display a final demo report."""
        print("📋 Generating Final Demo Report")
        print("=" * 70)
        
        # Get latest integration report
        latest_report = self.orchestrator.get_latest_report()
        
        if latest_report:
            print(f"Integration Report (Generated: {latest_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            print()
            
            # Learning summary
            learning_summary = latest_report.learning_summary
            print(f"🧠 Learning Summary:")
            print(f"   Total Learning Cycles: {learning_summary.get('total_cycles', 0)}")
            print(f"   Current Learning Phase: {learning_summary.get('current_phase', 'Unknown')}")
            print(f"   Learning Effectiveness: {learning_summary.get('effectiveness_score', 0):.2f}")
            print(f"   Improvement Actions Executed: {learning_summary.get('actions_executed', 0)}")
            print()
            
            # Feedback summary
            feedback_summary = latest_report.feedback_summary
            print(f"💬 Feedback Summary:")
            print(f"   Total Feedback Items: {feedback_summary.get('total_items', 0)}")
            print(f"   Average Quality Score: {feedback_summary.get('average_quality', 0):.2f}")
            print(f"   Loops Processed: {feedback_summary.get('loops_processed', 0)}")
            print(f"   Convergence Rate: {feedback_summary.get('convergence_rate', 0):.2f}")
            print()
            
            # Metrics summary
            metrics_summary = latest_report.metrics_summary
            print(f"📈 Metrics Summary:")
            print(f"   Metrics Collected: {metrics_summary.get('total_metrics', 0)}")
            print(f"   KPIs Tracked: {metrics_summary.get('total_kpis', 0)}")
            print(f"   Active Alerts: {metrics_summary.get('active_alerts', 0)}")
            print(f"   Collection Efficiency: {metrics_summary.get('collection_efficiency', 0):.2f}")
            print()
            
            # Adaptation summary
            adaptation_summary = latest_report.adaptation_summary
            print(f"🔄 Adaptation Summary:")
            print(f"   Adaptations Applied: {adaptation_summary.get('total_adaptations', 0)}")
            print(f"   Success Rate: {adaptation_summary.get('success_rate', 0):.2f}")
            print(f"   Average Improvement: {adaptation_summary.get('average_improvement', 0):.3f}")
            print(f"   System Health Change: {adaptation_summary.get('health_change', 0):+.3f}")
            print()
            
            # Performance insights
            if latest_report.performance_insights:
                print(f"💡 Key Performance Insights:")
                for insight in latest_report.performance_insights[-5:]:
                    print(f"   • {insight}")
                print()
            
            # Recommendations
            if latest_report.recommendations:
                print(f"🎯 Recommendations:")
                for recommendation in latest_report.recommendations[-5:]:
                    print(f"   • {recommendation}")
                print()
        
        # Demo statistics
        print(f"📊 Demo Statistics:")
        print(f"   Interactions Processed: {len(self.demo_data['interactions'])}")
        print(f"   Feedback Items Added: {len(self.demo_data['feedback_items'])}")
        print(f"   Adaptations Performed: {len(self.demo_data['adaptations'])}")
        print(f"   Insights Generated: {len(self.demo_data['insights'])}")
        
        # Calculate demo metrics
        if self.demo_data['interactions']:
            success_rate = sum(1 for i in self.demo_data['interactions'] if i['success']) / len(self.demo_data['interactions'])
            avg_response_time = sum(i['response_time'] for i in self.demo_data['interactions']) / len(self.demo_data['interactions'])
            avg_satisfaction = sum(i['user_satisfaction'] for i in self.demo_data['interactions']) / len(self.demo_data['interactions'])
            
            print(f"   Success Rate: {success_rate:.2f}")
            print(f"   Average Response Time: {avg_response_time:.2f}s")
            print(f"   Average User Satisfaction: {avg_satisfaction:.2f}")
        
        print()
        print("✅ Demo completed successfully!")
        print("🎉 Phase 4 Recursive Learning and Adaptation system is fully operational.")
    
    async def cleanup_demo(self):
        """Clean up demo resources."""
        print("🧹 Cleaning up demo resources...")
        
        if self.orchestrator and self.demo_running:
            await self.orchestrator.stop()
            self.demo_running = False
        
        print("✅ Demo cleanup completed")
    
    async def run_interactive_demo(self):
        """Run the complete interactive demo."""
        try:
            await self.setup_demo()
            await self.start_demo()
            
            print("🎬 Starting Phase 4 Interactive Demo")
            print("=" * 70)
            print()
            
            # Run demo sections
            await self.demonstrate_learning_engine()
            await asyncio.sleep(2)
            
            await self.demonstrate_feedback_pipeline()
            await asyncio.sleep(2)
            
            await self.demonstrate_metrics_system()
            await asyncio.sleep(2)
            
            await self.demonstrate_adaptation_cycle()
            await asyncio.sleep(2)
            
            await self.demonstrate_system_health()
            await asyncio.sleep(2)
            
            # Let the system run for a bit to generate more data
            print("⏳ Letting system run to generate additional data...")
            await asyncio.sleep(10)
            
            await self.generate_final_report()
            
        except Exception as e:
            print(f"❌ Demo error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup_demo()
    
    async def run_quick_demo(self):
        """Run a quick demo for testing purposes."""
        try:
            await self.setup_demo()
            await self.start_demo()
            
            print("⚡ Running Quick Phase 4 Demo")
            print("=" * 40)
            
            # Quick learning demonstration
            learning_engine = self.orchestrator.learning_engine
            for i in range(3):
                await learning_engine.process_learning_cycle({
                    "success": True,
                    "response_time": 0.5,
                    "user_satisfaction": 0.8
                })
            
            # Quick feedback demonstration
            feedback_pipeline = self.orchestrator.feedback_pipeline
            feedback_item = FeedbackItem(
                id="quick_demo_feedback",
                level=FeedbackLevel.IMMEDIATE,
                feedback_type=FeedbackType.SYSTEM_PERFORMANCE,
                content="Quick demo feedback",
                source="demo",
                timestamp=datetime.now(),
                metadata={}
            )
            await feedback_pipeline.add_feedback(feedback_item)
            
            # Wait for processing
            await asyncio.sleep(5)
            
            # Show results
            state = self.orchestrator.get_orchestration_state()
            health = self.orchestrator.get_system_health_summary()
            
            print(f"✅ Quick demo completed")
            print(f"   System Status: {state.status.value}")
            print(f"   Health Score: {health['overall_health_score']:.2f}")
            print(f"   Cycles Completed: {state.cycle_count}")
            
        except Exception as e:
            print(f"❌ Quick demo error: {str(e)}")
        
        finally:
            await self.cleanup_demo()


async def main():
    """Main demo entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 4 Recursive Learning and Adaptation Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--interactive", action="store_true", default=True, help="Run interactive demo")
    
    args = parser.parse_args()
    
    demo = Phase4Demo()
    
    if args.quick:
        await demo.run_quick_demo()
    else:
        await demo.run_interactive_demo()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())