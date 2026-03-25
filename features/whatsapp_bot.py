"""
WhatsApp Business Integration Module
Phase 3 Feature: Mobile-First Customer Engagement

This module provides WhatsApp Business API integration:
- Automated customer support
- Investment guidance via WhatsApp
- Portfolio updates and alerts
- Multi-language support
"""

import asyncio
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

# Note: These imports will be available when Phase 3 is implemented
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
    WHATSAPP_DEPENDENCIES_AVAILABLE = True
except ImportError:
    WHATSAPP_DEPENDENCIES_AVAILABLE = False
    logging.warning("WhatsApp dependencies not installed. Install with: pip install twilio")

logger = logging.getLogger(__name__)

class WhatsAppBot:
    """
    WhatsApp Business Bot for ET AI Concierge
    
    Features:
    - Automated customer support
    - Investment guidance and recommendations
    - Portfolio alerts and updates
    - Multi-language conversation support
    - Integration with existing agent pipeline
    """
    
    def __init__(self):
        # Twilio WhatsApp configuration
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('WHATSAPP_BUSINESS_NUMBER', 'whatsapp:+14155238886')
        
        if WHATSAPP_DEPENDENCIES_AVAILABLE and self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("WhatsApp client initialized in mock mode")
        
        # User session management
        self.user_sessions = {}
        
        # Conversation flow states
        self.conversation_states = {
            'WELCOME': 'welcome',
            'PROFILE_SETUP': 'profile_setup',
            'INVESTMENT_GUIDANCE': 'investment_guidance',
            'PORTFOLIO_REVIEW': 'portfolio_review',
            'EDUCATION': 'education',
            'SUPPORT': 'support'
        }
        
        # Quick reply templates
        self.quick_replies = {
            'main_menu': [
                '📊 Investment Guidance',
                '📚 Learn About Investing',
                '💼 Portfolio Review',
                '🧮 Calculators',
                '📞 Talk to Expert'
            ],
            'investment_types': [
                '🏦 Mutual Funds',
                '📈 Stocks',
                '🏛️ Fixed Deposits',
                '💰 SIP Planning',
                '🎯 Goal-based Investing'
            ],
            'languages': [
                '🇮🇳 English',
                '🇮🇳 हिंदी (Hindi)',
                '🇮🇳 தமிழ் (Tamil)',
                '🇮🇳 తెలుగు (Telugu)',
                '🇮🇳 ગુજરાતી (Gujarati)'
            ]
        }
    
    async def handle_incoming_message(self, message_data: Dict) -> Dict:
        """
        Handle incoming WhatsApp message
        
        Args:
            message_data: Dict containing message details from webhook
            
        Returns:
            Dict with response status and details
        """
        try:
            user_phone = message_data.get('From', '').replace('whatsapp:', '')
            message_body = message_data.get('Body', '').strip()
            message_type = message_data.get('MessageType', 'text')
            
            logger.info(f"Received WhatsApp message from {user_phone}: {message_body}")
            
            # Get or create user session
            user_session = await self._get_user_session(user_phone)
            
            # Process message based on type and current state
            if message_type == 'text':
                response = await self._process_text_message(
                    user_phone, message_body, user_session
                )
            elif message_type == 'interactive':
                response = await self._process_interactive_message(
                    user_phone, message_data, user_session
                )
            else:
                response = await self._handle_unsupported_message_type(user_phone)
            
            # Send response
            if response:
                await self._send_whatsapp_message(user_phone, response)
            
            return {
                'status': 'success',
                'user_phone': user_phone,
                'response_sent': bool(response)
            }
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp message: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_user_session(self, phone_number: str) -> Dict:
        """Get or create user session"""
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                'phone': phone_number,
                'state': self.conversation_states['WELCOME'],
                'language': 'english',
                'profile': {},
                'conversation_history': [],
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
        else:
            self.user_sessions[phone_number]['last_activity'] = datetime.now().isoformat()
        
        return self.user_sessions[phone_number]
    
    async def _process_text_message(self, phone: str, message: str, session: Dict) -> Dict:
        """Process text message based on current conversation state"""
        
        current_state = session['state']
        message_lower = message.lower().strip()
        
        # Handle common commands at any state
        if message_lower in ['hi', 'hello', 'hey', 'start', 'menu']:
            return await self._send_welcome_message(session)
        elif message_lower in ['help', 'support']:
            return await self._send_help_message(session)
        elif message_lower == 'stop':
            return await self._handle_stop_command(session)
        
        # State-specific processing
        if current_state == self.conversation_states['WELCOME']:
            return await self._handle_welcome_state(message, session)
        elif current_state == self.conversation_states['PROFILE_SETUP']:
            return await self._handle_profile_setup(message, session)
        elif current_state == self.conversation_states['INVESTMENT_GUIDANCE']:
            return await self._handle_investment_guidance(message, session)
        elif current_state == self.conversation_states['PORTFOLIO_REVIEW']:
            return await self._handle_portfolio_review(message, session)
        elif current_state == self.conversation_states['EDUCATION']:
            return await self._handle_education_request(message, session)
        else:
            return await self._handle_general_query(message, session)
    
    async def _send_welcome_message(self, session: Dict) -> Dict:
        """Send welcome message with main menu"""
        welcome_text = """🙏 Welcome to ET AI Concierge!
        
I'm your personal financial assistant, here to help you with:

📊 *Investment Guidance* - Get personalized recommendations
📚 *Financial Education* - Learn investing basics
💼 *Portfolio Review* - Analyze your investments
🧮 *Financial Calculators* - SIP, EMI, Tax planning
📞 *Expert Consultation* - Connect with advisors

*Choose an option or type your question:*"""
        
        session['state'] = self.conversation_states['WELCOME']
        
        return {
            'type': 'text',
            'text': welcome_text,
            'quick_replies': self.quick_replies['main_menu']
        }
    
    async def _handle_welcome_state(self, message: str, session: Dict) -> Dict:
        """Handle user selection from welcome menu"""
        message_lower = message.lower()
        
        if 'investment' in message_lower or 'guidance' in message_lower:
            session['state'] = self.conversation_states['INVESTMENT_GUIDANCE']
            return await self._start_investment_guidance(session)
        elif 'learn' in message_lower or 'education' in message_lower:
            session['state'] = self.conversation_states['EDUCATION']
            return await self._start_education_flow(session)
        elif 'portfolio' in message_lower or 'review' in message_lower:
            session['state'] = self.conversation_states['PORTFOLIO_REVIEW']
            return await self._start_portfolio_review(session)
        elif 'calculator' in message_lower:
            return await self._send_calculator_options(session)
        elif 'expert' in message_lower or 'consultation' in message_lower:
            return await self._handle_expert_consultation(session)
        else:
            # Treat as general query
            return await self._handle_general_query(message, session)
    
    async def _start_investment_guidance(self, session: Dict) -> Dict:
        """Start investment guidance flow"""
        if not session['profile'].get('basic_info_collected'):
            return await self._request_basic_profile(session)
        
        text = """📊 *Investment Guidance*

Let me help you find the right investment options. What are you interested in?"""
        
        return {
            'type': 'text',
            'text': text,
            'quick_replies': self.quick_replies['investment_types']
        }
    
    async def _request_basic_profile(self, session: Dict) -> Dict:
        """Request basic profile information"""
        session['state'] = self.conversation_states['PROFILE_SETUP']
        
        text = """To provide personalized recommendations, I need some basic information:

*What's your age?* (e.g., 28)"""
        
        session['profile']['setup_step'] = 'age'
        
        return {
            'type': 'text',
            'text': text
        }
    
    async def _handle_profile_setup(self, message: str, session: Dict) -> Dict:
        """Handle profile setup process"""
        setup_step = session['profile'].get('setup_step')
        
        if setup_step == 'age':
            # Validate and store age
            try:
                age = int(re.findall(r'\d+', message)[0])
                if 18 <= age <= 80:
                    session['profile']['age'] = age
                    session['profile']['setup_step'] = 'experience'
                    
                    text = """Great! Now, what's your investment experience?

1️⃣ *Beginner* - New to investing
2️⃣ *Intermediate* - Some experience
3️⃣ *Advanced* - Experienced investor

*Type 1, 2, or 3:*"""
                    
                    return {'type': 'text', 'text': text}
                else:
                    return {'type': 'text', 'text': 'Please enter a valid age between 18 and 80.'}
            except:
                return {'type': 'text', 'text': 'Please enter your age as a number (e.g., 28).'}
        
        elif setup_step == 'experience':
            experience_map = {
                '1': 'beginner',
                '2': 'intermediate', 
                '3': 'advanced'
            }
            
            if message.strip() in experience_map:
                session['profile']['experience'] = experience_map[message.strip()]
                session['profile']['setup_step'] = 'income'
                
                text = """Perfect! What's your approximate monthly income?

1️⃣ *Below ₹50,000*
2️⃣ *₹50,000 - ₹1,00,000*
3️⃣ *₹1,00,000 - ₹2,00,000*
4️⃣ *Above ₹2,00,000*

*Type 1, 2, 3, or 4:*"""
                
                return {'type': 'text', 'text': text}
            else:
                return {'type': 'text', 'text': 'Please choose 1, 2, or 3 for your experience level.'}
        
        elif setup_step == 'income':
            income_map = {
                '1': 'below_50k',
                '2': '50k_to_1l',
                '3': '1l_to_2l',
                '4': 'above_2l'
            }
            
            if message.strip() in income_map:
                session['profile']['income_bracket'] = income_map[message.strip()]
                session['profile']['basic_info_collected'] = True
                session['state'] = self.conversation_states['INVESTMENT_GUIDANCE']
                
                # Generate personalized recommendations
                recommendations = await self._generate_recommendations(session)
                
                return recommendations
            else:
                return {'type': 'text', 'text': 'Please choose 1, 2, 3, or 4 for your income bracket.'}
        
        return {'type': 'text', 'text': 'I didn\'t understand. Let\'s start over with your profile setup.'}
    
    async def _generate_recommendations(self, session: Dict) -> Dict:
        """Generate personalized investment recommendations"""
        profile = session['profile']
        age = profile.get('age', 30)
        experience = profile.get('experience', 'beginner')
        income = profile.get('income_bracket', '50k_to_1l')
        
        # Simple recommendation logic (would integrate with agent pipeline)
        recommendations = []
        
        if experience == 'beginner':
            recommendations.extend([
                {
                    'title': '🎓 ET Masterclass: Investment Basics',
                    'description': 'Learn the fundamentals of investing',
                    'url': 'https://economictimes.indiatimes.com/et-masterclass/investment-basics',
                    'type': 'education'
                },
                {
                    'title': '💰 SIP in Diversified Equity Funds',
                    'description': 'Start with ₹1,000/month SIP',
                    'url': 'https://etmoney.com/mutual-funds/sip',
                    'type': 'investment'
                }
            ])
        
        if age < 35:
            recommendations.append({
                'title': '📈 Growth-oriented Mutual Funds',
                'description': 'Higher equity allocation for long-term growth',
                'url': 'https://etmoney.com/mutual-funds/equity-funds',
                'type': 'investment'
            })
        
        # Format response
        text = f"""🎯 *Personalized Recommendations for You*

Based on your profile (Age: {age}, Experience: {experience.title()}):

"""
        
        for i, rec in enumerate(recommendations[:3], 1):
            text += f"{i}. *{rec['title']}*\n   {rec['description']}\n   🔗 {rec['url']}\n\n"
        
        text += """💡 *Next Steps:*
• Start with educational content
• Begin with small SIP amounts
• Review and adjust monthly

*Type 'menu' for more options or ask me anything!*"""
        
        return {
            'type': 'text',
            'text': text
        }
    
    async def _send_calculator_options(self, session: Dict) -> Dict:
        """Send calculator options"""
        text = """🧮 *Financial Calculators*

Choose a calculator to help with your planning:

1️⃣ *SIP Calculator* - Plan your systematic investments
2️⃣ *EMI Calculator* - Calculate loan EMIs
3️⃣ *Tax Calculator* - Estimate tax savings
4️⃣ *Retirement Calculator* - Plan for retirement
5️⃣ *Goal Calculator* - Plan for specific goals

*Type the number or calculator name:*"""
        
        return {
            'type': 'text',
            'text': text
        }
    
    async def _handle_general_query(self, message: str, session: Dict) -> Dict:
        """Handle general investment queries"""
        # This would integrate with the existing agent pipeline
        # For now, provide a helpful response
        
        query_lower = message.lower()
        
        if any(word in query_lower for word in ['sip', 'systematic', 'monthly']):
            response = """💰 *SIP (Systematic Investment Plan)*

SIP is a great way to invest regularly:
• Start with as little as ₹500/month
• Rupee cost averaging benefits
• Disciplined investing approach

🔗 *ET Money SIP Calculator:*
https://etmoney.com/sip-calculator

*Would you like me to help you start a SIP?*"""
        
        elif any(word in query_lower for word in ['mutual fund', 'mf', 'fund']):
            response = """📊 *Mutual Funds*

Mutual funds pool money from many investors:
• Professional fund management
• Diversification across stocks/bonds
• Different categories for different goals

🎓 *Learn more:*
https://economictimes.indiatimes.com/mf

*What type of mutual fund interests you?*"""
        
        elif any(word in query_lower for word in ['stock', 'share', 'equity']):
            response = """📈 *Stock Market Investing*

Direct stock investing requires research:
• Higher potential returns
• Higher risk than mutual funds
• Need market knowledge

📚 *ET Markets for research:*
https://economictimes.indiatimes.com/markets

*Are you new to stock investing?*"""
        
        else:
            response = f"""I understand you're asking about: "{message}"

Let me connect you with our AI agents for detailed guidance.

Meanwhile, here are some helpful resources:
📚 ET Masterclass: https://economictimes.indiatimes.com/et-masterclass
💰 ET Money Tools: https://etmoney.com
📊 Market Data: https://economictimes.indiatimes.com/markets

*Type 'menu' for main options or ask me anything specific!*"""
        
        return {
            'type': 'text',
            'text': response
        }
    
    async def _send_whatsapp_message(self, to_phone: str, message_data: Dict) -> bool:
        """Send WhatsApp message using Twilio"""
        if not self.client:
            logger.info(f"Mock WhatsApp message to {to_phone}: {message_data}")
            return True
        
        try:
            to_number = f"whatsapp:+{to_phone.lstrip('+')}"
            
            if message_data['type'] == 'text':
                message = self.client.messages.create(
                    body=message_data['text'],
                    from_=self.whatsapp_number,
                    to=to_number
                )
                
                logger.info(f"WhatsApp message sent: {message.sid}")
                return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending WhatsApp message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_portfolio_alert(self, phone: str, alert_data: Dict) -> bool:
        """Send portfolio alert to user"""
        alert_text = f"""🚨 *Portfolio Alert*

{alert_data.get('title', 'Portfolio Update')}

{alert_data.get('message', 'Your portfolio has important updates.')}

💼 *View Details:* {alert_data.get('url', 'https://etmoney.com/portfolio')}

*Reply 'STOP' to unsubscribe from alerts*"""
        
        return await self._send_whatsapp_message(phone, {
            'type': 'text',
            'text': alert_text
        })
    
    async def send_market_update(self, phone: str, market_data: Dict) -> bool:
        """Send market update to user"""
        nifty_change = market_data.get('nifty_change', 0)
        sensex_change = market_data.get('sensex_change', 0)
        
        trend_emoji = "📈" if nifty_change > 0 else "📉" if nifty_change < 0 else "➡️"
        
        update_text = f"""{trend_emoji} *Market Update*

*NIFTY*: {market_data.get('nifty', 'N/A')} ({nifty_change:+.2f}%)
*SENSEX*: {market_data.get('sensex', 'N/A')} ({sensex_change:+.2f}%)

📊 *View detailed analysis:*
https://economictimes.indiatimes.com/markets

*Reply 'STOP MARKET' to unsubscribe*"""
        
        return await self._send_whatsapp_message(phone, {
            'type': 'text',
            'text': update_text
        })
    
    def get_user_session_stats(self) -> Dict:
        """Get statistics about user sessions"""
        total_users = len(self.user_sessions)
        active_users = sum(
            1 for session in self.user_sessions.values()
            if datetime.fromisoformat(session['last_activity']) > 
               datetime.now() - timedelta(hours=24)
        )
        
        states_count = {}
        for session in self.user_sessions.values():
            state = session['state']
            states_count[state] = states_count.get(state, 0) + 1
        
        return {
            'total_users': total_users,
            'active_users_24h': active_users,
            'conversation_states': states_count,
            'timestamp': datetime.now().isoformat()
        }


class WhatsAppWebhookHandler:
    """Handle WhatsApp webhook events"""
    
    def __init__(self):
        self.bot = WhatsAppBot()
    
    async def handle_webhook(self, webhook_data: Dict) -> Dict:
        """Handle incoming webhook from Twilio"""
        try:
            # Extract message data from webhook
            message_data = {
                'From': webhook_data.get('From', ''),
                'To': webhook_data.get('To', ''),
                'Body': webhook_data.get('Body', ''),
                'MessageType': webhook_data.get('MessageType', 'text'),
                'Timestamp': webhook_data.get('Timestamp', datetime.now().isoformat())
            }
            
            # Process the message
            result = await self.bot.handle_incoming_message(message_data)
            
            return {
                'status': 'success',
                'processed': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Usage example and testing
async def demo_whatsapp_bot():
    """Demo the WhatsApp bot functionality"""
    bot = WhatsAppBot()
    
    # Simulate incoming messages
    test_messages = [
        {'From': 'whatsapp:+919876543210', 'Body': 'Hi', 'MessageType': 'text'},
        {'From': 'whatsapp:+919876543210', 'Body': 'Investment Guidance', 'MessageType': 'text'},
        {'From': 'whatsapp:+919876543210', 'Body': '28', 'MessageType': 'text'},
        {'From': 'whatsapp:+919876543210', 'Body': '1', 'MessageType': 'text'},
        {'From': 'whatsapp:+919876543210', 'Body': '2', 'MessageType': 'text'},
    ]
    
    for message in test_messages:
        print(f"\n--- Processing: {message['Body']} ---")
        result = await bot.handle_incoming_message(message)
        print(f"Result: {result}")
    
    # Show session stats
    stats = bot.get_user_session_stats()
    print(f"\nSession Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    asyncio.run(demo_whatsapp_bot())