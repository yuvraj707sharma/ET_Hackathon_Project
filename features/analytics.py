from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"

@dataclass
class ABTestConfig:
    experiment_id: str
    name: str
    description: str
    variants: Dict[str, Dict]  # variant_name -> config
    traffic_split: Dict[str, float]  # variant_name -> percentage
    start_date: datetime
    end_date: datetime
    status: ExperimentStatus
    success_metrics: List[str]

@dataclass
class UserEvent:
    user_id: str
    event_type: str  # view, click, complete_journey, convert
    timestamp: datetime
    properties: Dict[str, Any]
    experiment_variant: Optional[str] = None

class AdvancedAnalytics:
    """Advanced analytics for ET AI Concierge"""
    
    def __init__(self):
        self.events: List[UserEvent] = []
        self.experiments: Dict[str, ABTestConfig] = {}
        self.user_segments = {}
    
    def track_event(self, user_id: str, event_type: str, properties: Dict[str, Any]):
        """Track user events for analytics"""
        event = UserEvent(
            user_id=user_id,
            event_type=event_type,
            timestamp=datetime.now(),
            properties=properties
        )
        
        # Check if user is in any active experiments
        active_variant = self.get_user_experiment_variant(user_id)
        if active_variant:
            event.experiment_variant = active_variant
        
        self.events.append(event)
    
    def create_ab_test(self, config: ABTestConfig):
        """Create a new A/B test experiment"""
        self.experiments[config.experiment_id] = config
    
    def get_user_experiment_variant(self, user_id: str) -> Optional[str]:
        """Determine which experiment variant a user should see"""
        for exp_id, config in self.experiments.items():
            if config.status != ExperimentStatus.RUNNING:
                continue
            
            # Simple hash-based assignment for consistent user experience
            user_hash = hash(f"{user_id}_{exp_id}") % 100
            
            cumulative_percentage = 0
            for variant, percentage in config.traffic_split.items():
                cumulative_percentage += percentage * 100
                if user_hash < cumulative_percentage:
                    return f"{exp_id}_{variant}"
        
        return None
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get results for a specific experiment"""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        config = self.experiments[experiment_id]
        
        # Filter events for this experiment
        exp_events = [
            e for e in self.events 
            if e.experiment_variant and e.experiment_variant.startswith(experiment_id)
        ]
        
        # Calculate metrics by variant
        results = {}
        for variant in config.variants.keys():
            variant_key = f"{experiment_id}_{variant}"
            variant_events = [e for e in exp_events if e.experiment_variant == variant_key]
            
            results[variant] = {
                "total_users": len(set(e.user_id for e in variant_events)),
                "total_events": len(variant_events),
                "conversion_rate": self._calculate_conversion_rate(variant_events),
                "avg_session_duration": self._calculate_avg_session_duration(variant_events),
                "journey_completion_rate": self._calculate_journey_completion_rate(variant_events)
            }
        
        return {
            "experiment_id": experiment_id,
            "status": config.status.value,
            "results": results,
            "statistical_significance": self._calculate_statistical_significance(results)
        }
    
    def _calculate_conversion_rate(self, events: List[UserEvent]) -> float:
        """Calculate conversion rate from events"""
        total_users = len(set(e.user_id for e in events))
        converted_users = len(set(
            e.user_id for e in events 
            if e.event_type == "convert"
        ))
        
        return (converted_users / total_users * 100) if total_users > 0 else 0
    
    def _calculate_avg_session_duration(self, events: List[UserEvent]) -> float:
        """Calculate average session duration"""
        user_sessions = {}
        
        for event in events:
            if event.user_id not in user_sessions:
                user_sessions[event.user_id] = []
            user_sessions[event.user_id].append(event.timestamp)
        
        durations = []
        for user_id, timestamps in user_sessions.items():
            if len(timestamps) > 1:
                duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
                durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 0
    
    def _calculate_journey_completion_rate(self, events: List[UserEvent]) -> float:
        """Calculate journey completion rate"""
        total_users = len(set(e.user_id for e in events))
        completed_users = len(set(
            e.user_id for e in events 
            if e.event_type == "complete_journey"
        ))
        
        return (completed_users / total_users * 100) if total_users > 0 else 0
    
    def _calculate_statistical_significance(self, results: Dict) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        # Simplified significance calculation
        variants = list(results.keys())
        if len(variants) < 2:
            return {"significant": False, "confidence": 0}
        
        # Compare first two variants (in real implementation, use proper statistical tests)
        variant_a = results[variants[0]]
        variant_b = results[variants[1]]
        
        diff = abs(variant_a["conversion_rate"] - variant_b["conversion_rate"])
        
        # Simplified significance check (use proper statistical tests in production)
        significant = diff > 2.0 and min(variant_a["total_users"], variant_b["total_users"]) > 100
        
        return {
            "significant": significant,
            "confidence": 95 if significant else 0,
            "difference": diff
        }
    
    def get_user_segments(self) -> Dict[str, Any]:
        """Analyze user segments based on behavior"""
        segments = {
            "high_engagement": [],
            "conversion_ready": [],
            "at_risk": [],
            "new_users": []
        }
        
        user_stats = {}
        
        # Calculate user statistics
        for event in self.events:
            if event.user_id not in user_stats:
                user_stats[event.user_id] = {
                    "total_events": 0,
                    "last_activity": event.timestamp,
                    "first_activity": event.timestamp,
                    "converted": False
                }
            
            stats = user_stats[event.user_id]
            stats["total_events"] += 1
            stats["last_activity"] = max(stats["last_activity"], event.timestamp)
            stats["first_activity"] = min(stats["first_activity"], event.timestamp)
            
            if event.event_type == "convert":
                stats["converted"] = True
        
        # Segment users
        now = datetime.now()
        for user_id, stats in user_stats.items():
            days_since_last_activity = (now - stats["last_activity"]).days
            days_since_first_activity = (now - stats["first_activity"]).days
            
            if stats["total_events"] > 10 and days_since_last_activity < 7:
                segments["high_engagement"].append(user_id)
            elif stats["total_events"] > 5 and not stats["converted"]:
                segments["conversion_ready"].append(user_id)
            elif days_since_last_activity > 14:
                segments["at_risk"].append(user_id)
            elif days_since_first_activity < 7:
                segments["new_users"].append(user_id)
        
        return {
            "segments": {k: len(v) for k, v in segments.items()},
            "total_users": len(user_stats),
            "segment_details": segments
        }

# Example A/B test configurations
def create_sample_experiments():
    """Create sample A/B tests for the concierge system"""
    analytics = AdvancedAnalytics()
    
    # Test 1: Different onboarding flows
    onboarding_test = ABTestConfig(
        experiment_id="onboarding_flow_v1",
        name="Onboarding Flow Optimization",
        description="Test different onboarding approaches for new users",
        variants={
            "control": {"flow_type": "standard", "questions": 1},
            "detailed": {"flow_type": "detailed", "questions": 3},
            "minimal": {"flow_type": "minimal", "questions": 0}
        },
        traffic_split={"control": 0.4, "detailed": 0.3, "minimal": 0.3},
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ExperimentStatus.RUNNING,
        success_metrics=["conversion_rate", "journey_completion_rate"]
    )
    
    # Test 2: Different recommendation display styles
    ui_test = ABTestConfig(
        experiment_id="recommendation_ui_v1",
        name="Recommendation Display Style",
        description="Test different ways to display product recommendations",
        variants={
            "cards": {"display": "card_layout", "show_images": True},
            "list": {"display": "list_layout", "show_images": False}
        },
        traffic_split={"cards": 0.5, "list": 0.5},
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=21),
        status=ExperimentStatus.RUNNING,
        success_metrics=["click_through_rate", "time_on_page"]
    )
    
    analytics.create_ab_test(onboarding_test)
    analytics.create_ab_test(ui_test)
    
    return analytics