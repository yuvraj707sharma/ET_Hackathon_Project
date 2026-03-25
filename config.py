"""
Configuration Module for ET AI Concierge
Manages feature flags, environment settings, and phase-based configurations
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class DeploymentPhase(Enum):
    """Deployment phases for feature rollout"""
    PHASE_1 = "phase_1"  # Current: Basic 4-agent pipeline
    PHASE_2 = "phase_2"  # Q2 2026: Cloudflare AI + Market Intelligence
    PHASE_3 = "phase_3"  # Q3 2026: Voice + WhatsApp + Mobile
    PHASE_4 = "phase_4"  # Q4 2026: Autonomous Advisory + Enterprise

@dataclass
class FeatureFlags:
    """Feature flags for different capabilities"""
    
    # Core Features (Phase 1)
    agent_pipeline: bool = True
    llm_enhancement: bool = True
    analytics_tracking: bool = True
    et_content_integration: bool = True
    
    # Phase 2 Features
    cloudflare_ai_integration: bool = False
    real_time_market_data: bool = False
    advanced_personalization: bool = False
    regulatory_monitoring: bool = False
    
    # Phase 3 Features
    voice_interface: bool = False
    whatsapp_integration: bool = False
    multilingual_support: bool = False
    mobile_app: bool = False
    
    # Phase 4 Features
    autonomous_advisory: bool = False
    portfolio_management: bool = False
    sebi_compliance: bool = False
    enterprise_integration: bool = False
    
    # Development Features
    debug_mode: bool = False
    mock_data: bool = False
    performance_monitoring: bool = True

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.current_phase = DeploymentPhase(
            os.getenv('DEPLOYMENT_PHASE', DeploymentPhase.PHASE_1.value)
        )
        self.features = self._initialize_features()
        self.api_keys = self._load_api_keys()
        self.database = self._load_database_config()
        self.ui_settings = self._load_ui_settings()
        self.business_rules = self._load_business_rules()
    
    def _initialize_features(self) -> FeatureFlags:
        """Initialize feature flags based on current phase"""
        features = FeatureFlags()
        
        # Enable features based on deployment phase
        if self.current_phase in [DeploymentPhase.PHASE_2, DeploymentPhase.PHASE_3, DeploymentPhase.PHASE_4]:
            features.cloudflare_ai_integration = True
            features.real_time_market_data = True
            features.advanced_personalization = True
            features.regulatory_monitoring = True
        
        if self.current_phase in [DeploymentPhase.PHASE_3, DeploymentPhase.PHASE_4]:
            features.voice_interface = True
            features.whatsapp_integration = True
            features.multilingual_support = True
            features.mobile_app = True
        
        if self.current_phase == DeploymentPhase.PHASE_4:
            features.autonomous_advisory = True
            features.portfolio_management = True
            features.sebi_compliance = True
            features.enterprise_integration = True
        
        # Override with environment variables
        features.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        features.mock_data = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        return features
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys and credentials"""
        return {
            # Core LLM APIs
            'groq_api_key': os.getenv('GROQ_API_KEY', ''),
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            
            # Phase 2 APIs
            'cloudflare_ai_api_key': os.getenv('CLOUDFLARE_AI_API_KEY', ''),
            'et_api_key': os.getenv('ET_API_KEY', ''),
            'nse_api_key': os.getenv('NSE_API_KEY', ''),
            'bse_api_key': os.getenv('BSE_API_KEY', ''),
            
            # Phase 3 APIs
            'azure_speech_key': os.getenv('AZURE_SPEECH_KEY', ''),
            'azure_speech_region': os.getenv('AZURE_SPEECH_REGION', 'centralindia'),
            'twilio_account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
            'twilio_auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
            'whatsapp_business_number': os.getenv('WHATSAPP_BUSINESS_NUMBER', ''),
            
            # Phase 4 APIs
            'sebi_api_key': os.getenv('SEBI_API_KEY', ''),
            'rbi_api_key': os.getenv('RBI_API_KEY', ''),
            'salesforce_api_key': os.getenv('SALESFORCE_API_KEY', ''),
        }
    
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'postgres_url': os.getenv('DATABASE_URL', 'postgresql://localhost:5432/et_concierge'),
            'mongodb_url': os.getenv('MONGODB_URL', 'mongodb://localhost:27017/et_concierge'),
            'cache_ttl': int(os.getenv('CACHE_TTL', '3600')),  # 1 hour
            'session_timeout': int(os.getenv('SESSION_TIMEOUT', '1800')),  # 30 minutes
        }
    
    def _load_ui_settings(self) -> Dict[str, Any]:
        """Load UI and UX settings"""
        return {
            'theme': os.getenv('UI_THEME', 'light'),
            'brand_colors': {
                'primary': '#1B365D',  # ET Blue
                'secondary': '#FF6B35',  # ET Orange
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'info': '#17a2b8'
            },
            'animation_enabled': os.getenv('ENABLE_ANIMATIONS', 'true').lower() == 'true',
            'auto_refresh_interval': int(os.getenv('AUTO_REFRESH_INTERVAL', '30')),  # seconds
            'max_chat_history': int(os.getenv('MAX_CHAT_HISTORY', '50')),
        }
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules and compliance settings"""
        return {
            'max_investment_recommendation': float(os.getenv('MAX_INVESTMENT_AMOUNT', '1000000')),  # 10L
            'min_user_age': int(os.getenv('MIN_USER_AGE', '18')),
            'max_user_age': int(os.getenv('MAX_USER_AGE', '80')),
            'risk_assessment_required': os.getenv('REQUIRE_RISK_ASSESSMENT', 'true').lower() == 'true',
            'kyc_verification_required': os.getenv('REQUIRE_KYC', 'false').lower() == 'true',
            'disclaimer_required': True,
            'sebi_compliance_mode': self.features.sebi_compliance,
            'data_retention_days': int(os.getenv('DATA_RETENTION_DAYS', '365')),
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on available APIs"""
        if self.api_keys['groq_api_key']:
            return {
                'provider': 'groq',
                'api_key': self.api_keys['groq_api_key'],
                'model': os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),
                'base_url': os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1'),
                'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
                'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            }
        elif self.api_keys['openai_api_key']:
            return {
                'provider': 'openai',
                'api_key': self.api_keys['openai_api_key'],
                'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
                'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            }
        else:
            return {
                'provider': 'mock',
                'enabled': False
            }
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get supported languages configuration"""
        if not self.features.multilingual_support:
            return {'english': {'code': 'en', 'name': 'English'}}
        
        return {
            'english': {'code': 'en', 'name': 'English', 'locale': 'en-IN'},
            'hindi': {'code': 'hi', 'name': 'हिंदी', 'locale': 'hi-IN'},
            'tamil': {'code': 'ta', 'name': 'தமிழ்', 'locale': 'ta-IN'},
            'telugu': {'code': 'te', 'name': 'తెలుగు', 'locale': 'te-IN'},
            'gujarati': {'code': 'gu', 'name': 'ગુજરાતી', 'locale': 'gu-IN'},
            'bengali': {'code': 'bn', 'name': 'বাংলা', 'locale': 'bn-IN'},
            'marathi': {'code': 'mr', 'name': 'मराठी', 'locale': 'mr-IN'},
            'kannada': {'code': 'kn', 'name': 'ಕನ್ನಡ', 'locale': 'kn-IN'},
        }
    
    def get_et_integration_config(self) -> Dict[str, Any]:
        """Get ET ecosystem integration configuration"""
        return {
            'base_urls': {
                'et_markets': 'https://economictimes.indiatimes.com/markets',
                'et_prime': 'https://economictimes.indiatimes.com/prime',
                'et_money': 'https://etmoney.com',
                'et_masterclass': 'https://economictimes.indiatimes.com/et-masterclass',
                'et_rise': 'https://economictimes.indiatimes.com/small-biz',
                'et_auto': 'https://economictimes.indiatimes.com/industry/auto',
            },
            'api_endpoints': {
                'content_api': f"https://api.economictimes.com/v1/content",
                'market_data': f"https://api.economictimes.com/v1/markets",
                'user_api': f"https://api.economictimes.com/v1/users",
            },
            'rate_limits': {
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
            },
            'cache_settings': {
                'content_cache_ttl': 1800,  # 30 minutes
                'market_data_cache_ttl': 60,  # 1 minute
                'user_data_cache_ttl': 3600,  # 1 hour
            }
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled"""
        return getattr(self.features, feature_name, False)
    
    def get_phase_info(self) -> Dict[str, Any]:
        """Get current phase information"""
        phase_info = {
            DeploymentPhase.PHASE_1: {
                'name': 'Foundation',
                'description': '4-agent pipeline with basic ET integration',
                'features': ['agent_pipeline', 'llm_enhancement', 'analytics_tracking']
            },
            DeploymentPhase.PHASE_2: {
                'name': 'Intelligence Enhancement',
                'description': 'Real-time market data and Cloudflare AI integration',
                'features': ['cloudflare_ai_integration', 'real_time_market_data', 'advanced_personalization']
            },
            DeploymentPhase.PHASE_3: {
                'name': 'Multi-modal Experience',
                'description': 'Voice interface and mobile-first experience',
                'features': ['voice_interface', 'whatsapp_integration', 'multilingual_support']
            },
            DeploymentPhase.PHASE_4: {
                'name': 'Autonomous Advisory',
                'description': 'SEBI-compliant autonomous investment advisory',
                'features': ['autonomous_advisory', 'portfolio_management', 'enterprise_integration']
            }
        }
        
        return phase_info.get(self.current_phase, {})
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'missing_keys': []
        }
        
        # Check required API keys based on enabled features
        if self.features.llm_enhancement:
            if not (self.api_keys['groq_api_key'] or self.api_keys['openai_api_key']):
                validation_results['warnings'].append('No LLM API key configured')
        
        if self.features.cloudflare_ai_integration and not self.api_keys['cloudflare_ai_api_key']:
            validation_results['missing_keys'].append('CLOUDFLARE_AI_API_KEY')
        
        if self.features.voice_interface and not self.api_keys['azure_speech_key']:
            validation_results['missing_keys'].append('AZURE_SPEECH_KEY')
        
        if self.features.whatsapp_integration:
            if not self.api_keys['twilio_account_sid']:
                validation_results['missing_keys'].append('TWILIO_ACCOUNT_SID')
            if not self.api_keys['twilio_auth_token']:
                validation_results['missing_keys'].append('TWILIO_AUTH_TOKEN')
        
        # Set validation status
        if validation_results['missing_keys']:
            validation_results['valid'] = False
            validation_results['errors'].append(
                f"Missing required API keys: {', '.join(validation_results['missing_keys'])}"
            )
        
        return validation_results

# Global configuration instance
config = Config()

# Convenience functions
def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return config.is_feature_enabled(feature_name)

def get_api_key(key_name: str) -> str:
    """Get API key by name"""
    return config.api_keys.get(key_name, '')

def get_current_phase() -> DeploymentPhase:
    """Get current deployment phase"""
    return config.current_phase

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration"""
    return config.get_llm_config()

# Export commonly used configurations
FEATURES = config.features
API_KEYS = config.api_keys
UI_SETTINGS = config.ui_settings
BUSINESS_RULES = config.business_rules
ET_CONFIG = config.get_et_integration_config()
SUPPORTED_LANGUAGES = config.get_supported_languages()

if __name__ == "__main__":
    # Configuration validation and info
    print("ET AI Concierge Configuration")
    print("=" * 40)
    print(f"Current Phase: {config.current_phase.value}")
    print(f"Phase Info: {config.get_phase_info()}")
    print(f"LLM Config: {config.get_llm_config()}")
    print(f"Validation: {config.validate_configuration()}")
    print(f"Supported Languages: {list(config.get_supported_languages().keys())}")