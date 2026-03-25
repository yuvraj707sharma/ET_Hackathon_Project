from __future__ import annotations

import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LanguageConfig:
    code: str  # 'en', 'hi', 'ta', etc.
    name: str
    native_name: str
    rtl: bool = False  # Right-to-left languages

class MultiLanguageSupport:
    """Multi-language support for ET AI Concierge"""
    
    def __init__(self):
        self.supported_languages = {
            'en': LanguageConfig('en', 'English', 'English'),
            'hi': LanguageConfig('hi', 'Hindi', 'हिंदी'),
            'ta': LanguageConfig('ta', 'Tamil', 'தமிழ்'),
            'te': LanguageConfig('te', 'Telugu', 'తెలుగు'),
            'bn': LanguageConfig('bn', 'Bengali', 'বাংলা'),
            'gu': LanguageConfig('gu', 'Gujarati', 'ગુજરાતી'),
            'mr': LanguageConfig('mr', 'Marathi', 'मराठी'),
            'kn': LanguageConfig('kn', 'Kannada', 'ಕನ್ನಡ')
        }
        
        self.translations = self._load_translations()
        self.regional_content_mapping = self._load_regional_content()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load UI translations for different languages"""
        return {
            'en': {
                'welcome_message': 'Welcome to ET AI Concierge',
                'choose_scenario': 'Choose a scenario',
                'run_journey': 'Run Journey',
                'recommendations': 'Recommendations',
                'next_steps': 'Next Steps',
                'audit_trail': 'Audit Trail',
                'cold_start_title': 'New Investor Onboarding',
                'reengagement_title': 'Welcome Back',
                'cross_sell_title': 'Home Loan Guidance',
                'disclaimer': 'This is general guidance, not licensed financial advice.',
                'loading': 'AI agents working...',
                'error_message': 'Something went wrong. Please try again.',
                'feedback_prompt': 'How helpful was this recommendation?'
            },
            'hi': {
                'welcome_message': 'ET AI सहायक में आपका स्वागत है',
                'choose_scenario': 'एक परिदृश्य चुनें',
                'run_journey': 'यात्रा शुरू करें',
                'recommendations': 'सिफारिशें',
                'next_steps': 'अगले कदम',
                'audit_trail': 'ऑडिट ट्रेल',
                'cold_start_title': 'नए निवेशक का स्वागत',
                'reengagement_title': 'वापस स्वागत है',
                'cross_sell_title': 'होम लोन मार्गदर्शन',
                'disclaimer': 'यह सामान्य मार्गदर्शन है, लाइसेंसशुदा वित्तीय सलाह नहीं।',
                'loading': 'AI एजेंट काम कर रहे हैं...',
                'error_message': 'कुछ गलत हुआ। कृपया पुनः प्रयास करें।',
                'feedback_prompt': 'यह सिफारिश कितनी उपयोगी थी?'
            },
            'ta': {
                'welcome_message': 'ET AI உதவியாளரில் வரவேற்கிறோம்',
                'choose_scenario': 'ஒரு காட்சியைத் தேர்ந்தெடுக்கவும்',
                'run_journey': 'பயணத்தைத் தொடங்கவும்',
                'recommendations': 'பரிந்துரைகள்',
                'next_steps': 'அடுத்த படிகள்',
                'audit_trail': 'ஆடிட் டிரெயில்',
                'cold_start_title': 'புதிய முதலீட்டாளர் வரவேற்பு',
                'reengagement_title': 'மீண்டும் வரவேற்கிறோம்',
                'cross_sell_title': 'வீட்டுக் கடன் வழிகாட்டுதல்',
                'disclaimer': 'இது பொதுவான வழிகாட்டுதல், உரிமம் பெற்ற நிதி ஆலோசனை அல்ல।',
                'loading': 'AI முகவர்கள் வேலை செய்கிறார்கள்...',
                'error_message': 'ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.',
                'feedback_prompt': 'இந்த பரிந்துரை எவ்வளவு உதவிகரமாக இருந்தது?'
            }
        }
    
    def _load_regional_content(self) -> Dict[str, Dict]:
        """Map regional preferences to content"""
        return {
            'hi': {
                'preferred_examples': ['SBI', 'HDFC', 'ICICI'],
                'cultural_context': 'family_oriented',
                'investment_preferences': ['gold', 'real_estate', 'fixed_deposits'],
                'regional_festivals': ['diwali', 'holi', 'dussehra']
            },
            'ta': {
                'preferred_examples': ['Indian Bank', 'Canara Bank', 'SBI'],
                'cultural_context': 'traditional_values',
                'investment_preferences': ['gold', 'mutual_funds', 'ppf'],
                'regional_festivals': ['pongal', 'diwali', 'tamil_new_year']
            },
            'te': {
                'preferred_examples': ['Andhra Bank', 'SBI', 'HDFC'],
                'cultural_context': 'education_focused',
                'investment_preferences': ['education_funds', 'real_estate', 'sips'],
                'regional_festivals': ['ugadi', 'dussehra', 'diwali']
            }
        }
    
    def get_translation(self, key: str, language: str = 'en') -> str:
        """Get translated text for a given key"""
        if language not in self.translations:
            language = 'en'  # Fallback to English
        
        return self.translations[language].get(key, self.translations['en'].get(key, key))
    
    def detect_user_language(self, user_input: str) -> str:
        """Detect user's preferred language from input"""
        # Simple language detection (in production, use proper NLP libraries)
        hindi_chars = set('अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह')
        tamil_chars = set('அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறன')
        
        if any(char in hindi_chars for char in user_input):
            return 'hi'
        elif any(char in tamil_chars for char in user_input):
            return 'ta'
        else:
            return 'en'
    
    def localize_content_recommendations(self, recommendations: List[Dict], 
                                       language: str, user_location: str = None) -> List[Dict]:
        """Localize content recommendations based on language and region"""
        if language not in self.regional_content_mapping:
            return recommendations
        
        regional_prefs = self.regional_content_mapping[language]
        localized_recs = []
        
        for rec in recommendations:
            localized_rec = rec.copy()
            
            # Add regional context to explanations
            if 'reason' in localized_rec:
                # Add culturally relevant examples
                if language == 'hi' and 'SIP' in rec.get('categoryTags', []):
                    localized_rec['regional_context'] = (
                        "त्योहारी सीजन में SIP शुरू करना शुभ माना जाता है। "
                        "दीवाली के समय निवेश की शुरुआत करें।"
                    )
                elif language == 'ta' and 'home-loan' in rec.get('categoryTags', []):
                    localized_rec['regional_context'] = (
                        "பொங்கல் சீசனில் வீட்டுக் கடன் வட்டி விகிதங்கள் குறைவாக இருக்கலாம்"
                    )
            
            # Prioritize content with regional bank examples
            content_text = rec.get('title', '').lower()
            for bank in regional_prefs['preferred_examples']:
                if bank.lower() in content_text:
                    localized_rec['regional_relevance_score'] = 1.0
                    break
            
            localized_recs.append(localized_rec)
        
        return localized_recs
    
    def generate_multilingual_response(self, base_response: str, 
                                     target_language: str, user_context: Dict) -> str:
        """Generate response in user's preferred language"""
        if target_language == 'en':
            return base_response
        
        # In production, integrate with translation APIs (Google Translate, Azure Translator)
        # For demo, return templated responses
        
        templates = {
            'hi': {
                'sip_guidance': (
                    "SIP निवेश शुरू करने के लिए:\n"
                    "1. अपना लक्ष्य तय करें\n"
                    "2. जोखिम क्षमता समझें\n"
                    "3. छोटी राशि से शुरुआत करें\n\n"
                    "सुझावित फंड: {recommendations}"
                ),
                'home_loan': (
                    "होम लोन के लिए:\n"
                    "1. EMI कैलकुलेटर का उपयोग करें\n"
                    "2. विभिन्न बैंकों की दरों की तुलना करें\n"
                    "3. प्री-अप्रूवल लें\n\n"
                    "बेहतर दरों के लिए: {recommendations}"
                )
            },
            'ta': {
                'sip_guidance': (
                    "SIP முதலீட்டைத் தொடங்க:\n"
                    "1. உங்கள் இலக்கை நிர்ணயிக்கவும்\n"
                    "2. ரிஸ்க் திறனைப் புரிந்துகொள்ளவும்\n"
                    "3. சிறிய தொகையில் தொடங்கவும்\n\n"
                    "பரிந்துரைக்கப்பட்ட ஃபண்டுகள்: {recommendations}"
                ),
                'home_loan': (
                    "வீட்டுக் கடனுக்கு:\n"
                    "1. EMI கால்குலேட்டரைப் பயன்படுத்தவும்\n"
                    "2. வெவ்வேறு வங்கிகளின் விகிதங்களை ஒப்பிடவும்\n"
                    "3. முன் அனுமதி பெறவும்\n\n"
                    "சிறந்த விகிதங்களுக்கு: {recommendations}"
                )
            }
        }
        
        # Simple template matching (enhance with proper NLP in production)
        if 'SIP' in base_response and target_language in templates:
            return templates[target_language]['sip_guidance']
        elif 'home loan' in base_response.lower() and target_language in templates:
            return templates[target_language]['home_loan']
        
        return base_response  # Fallback to original

# Integration function
def create_multilingual_concierge_response(base_result: Dict, user_language: str) -> Dict:
    """Create multilingual version of concierge response"""
    ml_support = MultiLanguageSupport()
    
    enhanced_result = base_result.copy()
    
    # Translate UI elements
    if 'onboarding' in enhanced_result:
        original_message = enhanced_result['onboarding']['assistantMessage']
        enhanced_result['onboarding']['assistantMessage'] = ml_support.generate_multilingual_response(
            original_message, user_language, {}
        )
    
    # Localize recommendations
    if 'selectedProducts' in enhanced_result:
        enhanced_result['selectedProducts'] = ml_support.localize_content_recommendations(
            enhanced_result['selectedProducts'], user_language
        )
    
    # Add language metadata
    enhanced_result['language_info'] = {
        'detected_language': user_language,
        'supported_languages': list(ml_support.supported_languages.keys()),
        'rtl': ml_support.supported_languages[user_language].rtl if user_language in ml_support.supported_languages else False
    }
    
    return enhanced_result