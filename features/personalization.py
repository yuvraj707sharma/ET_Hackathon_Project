from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import numpy as np

@dataclass
class UserProfile:
    user_id: str
    reading_history: List[str]  # article IDs
    time_spent: Dict[str, float]  # article_id -> minutes
    interaction_patterns: Dict[str, Any]
    investment_stage: str  # beginner, intermediate, advanced
    preferred_content_types: List[str]  # article, video, tool, masterclass
    risk_tolerance: str  # low, medium, high
    financial_goals: List[str]
    last_active: datetime

class PersonalizationEngine:
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_embeddings = {}  # For semantic similarity
        
    def track_user_interaction(self, user_id: str, article_id: str, 
                             interaction_type: str, duration: float = None):
        """Track user interactions for learning"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                reading_history=[],
                time_spent={},
                interaction_patterns={},
                investment_stage="beginner",
                preferred_content_types=[],
                risk_tolerance="medium",
                financial_goals=[],
                last_active=datetime.now()
            )
        
        profile = self.user_profiles[user_id]
        profile.reading_history.append(article_id)
        
        if duration:
            profile.time_spent[article_id] = duration
            
        # Update interaction patterns
        if interaction_type not in profile.interaction_patterns:
            profile.interaction_patterns[interaction_type] = 0
        profile.interaction_patterns[interaction_type] += 1
        
        profile.last_active = datetime.now()
    
    def get_personalized_recommendations(self, user_id: str, 
                                       available_content: List[Dict]) -> List[Dict]:
        """Generate personalized content recommendations"""
        if user_id not in self.user_profiles:
            return self._cold_start_recommendations(available_content)
        
        profile = self.user_profiles[user_id]
        
        # Score content based on user preferences
        scored_content = []
        for content in available_content:
            score = self._calculate_content_score(profile, content)
            scored_content.append((content, score))
        
        # Sort by score and return top recommendations
        scored_content.sort(key=lambda x: x[1], reverse=True)
        return [content for content, score in scored_content[:5]]
    
    def _calculate_content_score(self, profile: UserProfile, content: Dict) -> float:
        """Calculate relevance score for content"""
        score = 0.0
        
        # Content type preference
        if content.get('productType') in profile.preferred_content_types:
            score += 0.3
        
        # Investment stage matching
        content_tags = content.get('categoryTags', [])
        if profile.investment_stage in content_tags:
            score += 0.4
        
        # Risk tolerance alignment
        risk_keywords = {
            'low': ['safe', 'conservative', 'stable'],
            'medium': ['balanced', 'moderate', 'diversified'],
            'high': ['growth', 'aggressive', 'volatile']
        }
        
        content_text = (content.get('title', '') + ' ' + 
                       ' '.join(content_tags)).lower()
        
        for keyword in risk_keywords.get(profile.risk_tolerance, []):
            if keyword in content_text:
                score += 0.2
                break
        
        # Recency boost for new content
        if content.get('lastUpdatedISO'):
            try:
                updated = datetime.fromisoformat(content['lastUpdatedISO'])
                days_old = (datetime.now() - updated).days
                if days_old < 7:
                    score += 0.1
            except:
                pass
        
        return score
    
    def _cold_start_recommendations(self, available_content: List[Dict]) -> List[Dict]:
        """Recommendations for new users"""
        # Prioritize beginner content
        beginner_content = [
            c for c in available_content 
            if 'beginner' in c.get('categoryTags', [])
        ]
        return beginner_content[:5] if beginner_content else available_content[:5]