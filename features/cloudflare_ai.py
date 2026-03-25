"""
Cloudflare AI Integration Module
Phase 2 Feature: Real-time Market Intelligence

This module integrates with Cloudflare's AI Agent API to provide:
- Real-time market data scraping from NSE, BSE
- Financial news sentiment analysis
- Regulatory update monitoring
- Competitive intelligence gathering
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CloudflareAIAgent:
    """
    Cloudflare AI Agent for real-time market intelligence
    
    Features:
    - Market data scraping from multiple sources
    - Sentiment analysis of financial news
    - Regulatory monitoring (SEBI, RBI)
    - Competitive intelligence
    """
    
    def __init__(self):
        self.api_key = os.getenv('CLOUDFLARE_AI_API_KEY')
        self.base_url = "https://api.cloudflare.com/client/v4/ai/agents"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_market_data(self, symbols: List[str]) -> Dict:
        """
        Scrape real-time market data for given symbols
        
        Args:
            symbols: List of stock symbols (e.g., ['RELIANCE', 'TCS', 'INFY'])
            
        Returns:
            Dict containing market data, prices, and metadata
        """
        if not self.api_key:
            logger.warning("Cloudflare AI API key not configured, using mock data")
            return self._get_mock_market_data(symbols)
        
        scrape_config = {
            "targets": [
                f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
                for symbol in symbols
            ] + [
                "https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx",
                "https://www.moneycontrol.com/markets/indian-indices/",
                "https://economictimes.indiatimes.com/markets"
            ],
            "extract_fields": [
                "price", "change", "volume", "market_cap", 
                "pe_ratio", "news_headlines", "analyst_ratings"
            ],
            "analysis_type": "financial_data",
            "realtime": True,
            "timeout": 30
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json=scrape_config
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Cloudflare AI API error: {response.status}")
                    return self._get_mock_market_data(symbols)
        except Exception as e:
            logger.error(f"Error scraping market data: {e}")
            return self._get_mock_market_data(symbols)
    
    async def analyze_news_sentiment(self, news_articles: List[str]) -> Dict:
        """
        Analyze sentiment of financial news articles
        
        Args:
            news_articles: List of news article texts or URLs
            
        Returns:
            Dict containing sentiment scores and analysis
        """
        if not self.api_key:
            return self._get_mock_sentiment_data()
        
        sentiment_config = {
            "text_data": news_articles,
            "analysis_type": "financial_sentiment",
            "include_entities": True,
            "confidence_threshold": 0.7,
            "language": "en"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/analyze",
                headers=self.headers,
                json=sentiment_config
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return self._get_mock_sentiment_data()
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._get_mock_sentiment_data()
    
    async def monitor_regulatory_updates(self) -> Dict:
        """
        Monitor regulatory websites for new updates
        
        Returns:
            Dict containing latest regulatory updates
        """
        if not self.api_key:
            return self._get_mock_regulatory_data()
        
        regulatory_config = {
            "targets": [
                "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=1&smid=1",
                "https://www.rbi.org.in/Scripts/NotificationUser.aspx",
                "https://www.incometaxindia.gov.in/Pages/communications/notifications.aspx"
            ],
            "extract_fields": ["title", "date", "content", "impact_level"],
            "change_detection": True,
            "notification_webhook": os.getenv('REGULATORY_WEBHOOK_URL')
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/monitor",
                headers=self.headers,
                json=regulatory_config
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return self._get_mock_regulatory_data()
        except Exception as e:
            logger.error(f"Error monitoring regulatory updates: {e}")
            return self._get_mock_regulatory_data()
    
    def _get_mock_market_data(self, symbols: List[str]) -> Dict:
        """Mock market data for development/demo purposes"""
        import random
        
        mock_data = {
            "timestamp": datetime.now().isoformat(),
            "market_status": "open",
            "indices": {
                "NIFTY": {
                    "price": 19500 + random.uniform(-200, 200),
                    "change": random.uniform(-1.5, 1.5),
                    "volume": random.randint(100000, 500000)
                },
                "SENSEX": {
                    "price": 65000 + random.uniform(-500, 500),
                    "change": random.uniform(-1.2, 1.2),
                    "volume": random.randint(80000, 300000)
                }
            },
            "stocks": {},
            "news_headlines": [
                "Market opens higher on positive global cues",
                "IT stocks rally on strong Q3 results",
                "Banking sector shows mixed performance"
            ],
            "volatility": random.uniform(0.15, 0.25)
        }
        
        for symbol in symbols:
            mock_data["stocks"][symbol] = {
                "price": random.uniform(100, 3000),
                "change": random.uniform(-5, 5),
                "volume": random.randint(10000, 100000),
                "pe_ratio": random.uniform(15, 35)
            }
        
        return mock_data
    
    def _get_mock_sentiment_data(self) -> Dict:
        """Mock sentiment data for development/demo purposes"""
        import random
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_sentiment": random.choice(["positive", "neutral", "negative"]),
            "compound_score": random.uniform(-0.5, 0.5),
            "confidence": random.uniform(0.7, 0.95),
            "key_entities": ["market", "stocks", "investment", "economy"],
            "sentiment_breakdown": {
                "positive": random.uniform(0.2, 0.6),
                "neutral": random.uniform(0.2, 0.4),
                "negative": random.uniform(0.1, 0.3)
            }
        }
    
    def _get_mock_regulatory_data(self) -> Dict:
        """Mock regulatory data for development/demo purposes"""
        return {
            "timestamp": datetime.now().isoformat(),
            "updates": [
                {
                    "source": "SEBI",
                    "title": "New guidelines for mutual fund investments",
                    "date": (datetime.now() - timedelta(days=1)).isoformat(),
                    "impact_level": "medium",
                    "summary": "Updated KYC requirements for MF investments"
                },
                {
                    "source": "RBI",
                    "title": "Monetary policy committee meeting minutes",
                    "date": (datetime.now() - timedelta(days=3)).isoformat(),
                    "impact_level": "high",
                    "summary": "Interest rate decisions and economic outlook"
                }
            ],
            "total_updates": 2,
            "high_impact_count": 1
        }


class MarketIntelligenceEngine:
    """
    Enhanced market intelligence engine using Cloudflare AI
    
    Combines multiple data sources for comprehensive market analysis
    """
    
    def __init__(self):
        self.cloudflare_agent = CloudflareAIAgent()
    
    async def get_comprehensive_market_intelligence(self, 
                                                 user_interests: List[str] = None) -> Dict:
        """
        Get comprehensive market intelligence for user recommendations
        
        Args:
            user_interests: List of user's investment interests/sectors
            
        Returns:
            Dict containing comprehensive market analysis
        """
        async with self.cloudflare_agent as agent:
            # Get market data
            symbols = user_interests or ['NIFTY', 'SENSEX', 'RELIANCE', 'TCS']
            market_data = await agent.scrape_market_data(symbols)
            
            # Analyze news sentiment
            news_articles = market_data.get('news_headlines', [])
            sentiment_data = await agent.analyze_news_sentiment(news_articles)
            
            # Get regulatory updates
            regulatory_data = await agent.monitor_regulatory_updates()
            
            # Combine and analyze
            intelligence = {
                "market_overview": {
                    "status": market_data.get("market_status", "unknown"),
                    "volatility": market_data.get("volatility", 0.2),
                    "trend": self._determine_market_trend(market_data),
                    "recommendation": self._generate_market_recommendation(
                        market_data, sentiment_data
                    )
                },
                "sentiment_analysis": {
                    "overall_sentiment": sentiment_data.get("overall_sentiment", "neutral"),
                    "confidence": sentiment_data.get("confidence", 0.7),
                    "key_themes": sentiment_data.get("key_entities", [])
                },
                "regulatory_environment": {
                    "recent_updates": regulatory_data.get("updates", []),
                    "impact_assessment": self._assess_regulatory_impact(regulatory_data)
                },
                "investment_climate": self._assess_investment_climate(
                    market_data, sentiment_data, regulatory_data
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            return intelligence
    
    def _determine_market_trend(self, market_data: Dict) -> str:
        """Determine overall market trend from data"""
        nifty_change = market_data.get("indices", {}).get("NIFTY", {}).get("change", 0)
        sensex_change = market_data.get("indices", {}).get("SENSEX", {}).get("change", 0)
        
        avg_change = (nifty_change + sensex_change) / 2
        
        if avg_change > 1:
            return "bullish"
        elif avg_change < -1:
            return "bearish"
        else:
            return "sideways"
    
    def _generate_market_recommendation(self, market_data: Dict, sentiment_data: Dict) -> str:
        """Generate market-based recommendation"""
        volatility = market_data.get("volatility", 0.2)
        sentiment = sentiment_data.get("compound_score", 0)
        
        if volatility > 0.25:
            return "Consider SIP investments due to high volatility"
        elif sentiment < -0.3:
            return "Market sentiment negative, focus on defensive stocks"
        elif sentiment > 0.3 and volatility < 0.15:
            return "Positive sentiment with low volatility, good for equity exposure"
        else:
            return "Balanced approach recommended with diversified portfolio"
    
    def _assess_regulatory_impact(self, regulatory_data: Dict) -> str:
        """Assess impact of recent regulatory changes"""
        updates = regulatory_data.get("updates", [])
        high_impact_count = sum(1 for update in updates if update.get("impact_level") == "high")
        
        if high_impact_count > 0:
            return "High impact regulatory changes detected"
        elif len(updates) > 2:
            return "Multiple regulatory updates, monitor closely"
        else:
            return "Stable regulatory environment"
    
    def _assess_investment_climate(self, market_data: Dict, 
                                 sentiment_data: Dict, 
                                 regulatory_data: Dict) -> str:
        """Overall investment climate assessment"""
        volatility = market_data.get("volatility", 0.2)
        sentiment = sentiment_data.get("compound_score", 0)
        regulatory_impact = len(regulatory_data.get("updates", []))
        
        score = 0
        if volatility < 0.2:
            score += 1
        if sentiment > 0:
            score += 1
        if regulatory_impact < 2:
            score += 1
        
        if score >= 2:
            return "favorable"
        elif score == 1:
            return "neutral"
        else:
            return "cautious"


# Usage example for integration with existing agents
async def enhance_agent_with_market_intelligence():
    """
    Example of how to enhance existing agents with market intelligence
    """
    engine = MarketIntelligenceEngine()
    
    # Get market intelligence
    intelligence = await engine.get_comprehensive_market_intelligence(
        user_interests=['RELIANCE', 'TCS', 'HDFC']
    )
    
    # Use intelligence to enhance agent decisions
    if intelligence["investment_climate"] == "cautious":
        # Adjust recommendations to be more conservative
        pass
    elif intelligence["market_overview"]["volatility"] > 0.25:
        # Recommend SIP over lump-sum
        pass
    
    return intelligence


if __name__ == "__main__":
    # Test the Cloudflare AI integration
    async def test_cloudflare_ai():
        engine = MarketIntelligenceEngine()
        intelligence = await engine.get_comprehensive_market_intelligence()
        print(json.dumps(intelligence, indent=2))
    
    asyncio.run(test_cloudflare_ai())