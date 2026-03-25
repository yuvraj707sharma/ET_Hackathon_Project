from __future__ import annotations

import requests
from datetime import datetime
from typing import Dict, List, Optional
import json

class MarketDataIntegrator:
    """Integrates real-time market data to enhance recommendations"""
    
    def __init__(self):
        self.market_conditions = {}
        self.sector_performance = {}
        self.trending_stocks = []
    
    def get_market_context(self) -> Dict:
        """Get current market conditions for contextual recommendations"""
        # Simulated market data (in production, use real APIs like NSE/BSE)
        return {
            "market_sentiment": "bullish",  # bullish, bearish, neutral
            "volatility_index": 18.5,  # VIX equivalent
            "top_performing_sectors": ["IT", "Pharma", "Banking"],
            "trending_themes": ["ESG investing", "Small-cap rally", "Digital payments"],
            "market_alerts": [
                "Nifty hits new high - good time for SIP top-ups",
                "Banking sector correction - opportunity for value investors"
            ]
        }
    
    def enhance_recommendations_with_market_data(self, base_recommendations: List[Dict], 
                                               user_persona: str) -> List[Dict]:
        """Add market-aware context to recommendations"""
        market_context = self.get_market_context()
        enhanced_recs = []
        
        for rec in base_recommendations:
            enhanced_rec = rec.copy()
            
            # Add market timing insights
            if "SIP" in rec.get('categoryTags', []):
                if market_context["market_sentiment"] == "bearish":
                    enhanced_rec["market_insight"] = "💡 Market correction = Great SIP opportunity (lower NAVs)"
                elif market_context["volatility_index"] > 20:
                    enhanced_rec["market_insight"] = "⚠️ High volatility - Consider systematic investing"
            
            # Add sector-specific insights
            content_title = rec.get('title', '').lower()
            for sector in market_context["top_performing_sectors"]:
                if sector.lower() in content_title:
                    enhanced_rec["market_insight"] = f"🚀 {sector} sector outperforming - Timely read"
            
            # Add trending theme relevance
            for theme in market_context["trending_themes"]:
                if any(word in content_title for word in theme.lower().split()):
                    enhanced_rec["trending_badge"] = "🔥 Trending Now"
            
            enhanced_recs.append(enhanced_rec)
        
        return enhanced_recs
    
    def get_contextual_alerts(self, user_portfolio: Optional[Dict] = None) -> List[str]:
        """Generate personalized market alerts"""
        market_context = self.get_market_context()
        alerts = []
        
        # General market alerts
        alerts.extend(market_context["market_alerts"])
        
        # Portfolio-specific alerts (if user has portfolio data)
        if user_portfolio:
            for holding in user_portfolio.get('holdings', []):
                if holding['sector'] in market_context["top_performing_sectors"]:
                    alerts.append(f"📈 Your {holding['name']} sector is outperforming")
        
        return alerts

class NewsIntegrator:
    """Integrates ET news to surface relevant content"""
    
    def get_breaking_financial_news(self) -> List[Dict]:
        """Get latest financial news for contextual recommendations"""
        # Simulated news data (integrate with ET's news API)
        return [
            {
                "headline": "RBI keeps repo rate unchanged at 6.5%",
                "impact": "Positive for debt funds, neutral for equity",
                "related_content_tags": ["debt-funds", "interest-rates"],
                "urgency": "high"
            },
            {
                "headline": "Budget 2024: New tax benefits for ELSS investments",
                "impact": "Boost for tax-saving mutual funds",
                "related_content_tags": ["ELSS", "tax-saving", "budget"],
                "urgency": "medium"
            }
        ]
    
    def match_news_to_user_intent(self, user_query: str, news_items: List[Dict]) -> List[Dict]:
        """Match breaking news to user's current interest"""
        relevant_news = []
        
        query_lower = user_query.lower()
        
        for news in news_items:
            # Simple keyword matching (can be enhanced with NLP)
            headline_words = news['headline'].lower().split()
            if any(word in query_lower for word in headline_words):
                relevant_news.append(news)
        
        return relevant_news

# Integration with existing concierge system
def enhance_concierge_with_market_data(base_result: Dict) -> Dict:
    """Enhance concierge results with market context"""
    market_integrator = MarketDataIntegrator()
    news_integrator = NewsIntegrator()
    
    enhanced_result = base_result.copy()
    
    # Enhance product recommendations
    enhanced_result["selectedProducts"] = market_integrator.enhance_recommendations_with_market_data(
        base_result["selectedProducts"], 
        base_result["persona"]["userPersona"]
    )
    
    # Add market alerts
    enhanced_result["market_alerts"] = market_integrator.get_contextual_alerts()
    
    # Add relevant breaking news
    user_message = base_result.get("chatTranscript", [{}])[0].get("content", "")
    relevant_news = news_integrator.match_news_to_user_intent(
        user_message, 
        news_integrator.get_breaking_financial_news()
    )
    enhanced_result["breaking_news"] = relevant_news
    
    return enhanced_result