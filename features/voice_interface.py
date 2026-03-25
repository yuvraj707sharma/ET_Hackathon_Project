"""
Voice Interface Module
Phase 3 Feature: Multi-language Voice Interaction

This module provides voice-based interaction capabilities:
- Speech-to-text in multiple Indian languages
- Text-to-speech with natural voices
- Voice command processing
- Integration with existing agent pipeline
"""

import asyncio
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import wave

# Note: These imports will be available when Phase 3 is implemented
try:
    import speech_recognition as sr
    import pyttsx3
    from googletrans import Translator
    import azure.cognitiveservices.speech as speechsdk
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError:
    VOICE_DEPENDENCIES_AVAILABLE = False
    logging.warning("Voice interface dependencies not installed. Install with: pip install speechrecognition pyttsx3 googletrans azure-cognitiveservices-speech")

logger = logging.getLogger(__name__)

class VoiceInterface:
    """
    Multi-language voice interface for ET AI Concierge
    
    Supports:
    - Hindi, English, Tamil, Telugu, Gujarati, Bengali
    - Real-time speech recognition
    - Natural text-to-speech
    - Voice command processing
    """
    
    def __init__(self):
        self.supported_languages = {
            'english': {'code': 'en', 'locale': 'en-IN'},
            'hindi': {'code': 'hi', 'locale': 'hi-IN'},
            'tamil': {'code': 'ta', 'locale': 'ta-IN'},
            'telugu': {'code': 'te', 'locale': 'te-IN'},
            'gujarati': {'code': 'gu', 'locale': 'gu-IN'},
            'bengali': {'code': 'bn', 'locale': 'bn-IN'},
            'marathi': {'code': 'mr', 'locale': 'mr-IN'},
            'kannada': {'code': 'kn', 'locale': 'kn-IN'}
        }
        
        if VOICE_DEPENDENCIES_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            self.translator = Translator()
            
            # Configure TTS engine
            self._configure_tts_engine()
            
            # Azure Speech Service (for better Indian language support)
            self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY')
            self.azure_region = os.getenv('AZURE_SPEECH_REGION', 'centralindia')
        else:
            logger.warning("Voice interface initialized in mock mode")
    
    def _configure_tts_engine(self):
        """Configure text-to-speech engine settings"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return
            
        # Set voice properties
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find Indian English voice
        for voice in voices:
            if 'india' in voice.name.lower() or 'indian' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Slower for clarity
        self.tts_engine.setProperty('volume', 0.8)
    
    async def process_voice_query(self, audio_data: bytes = None, 
                                language: str = 'english',
                                use_microphone: bool = True) -> Dict:
        """
        Process voice input and return structured response
        
        Args:
            audio_data: Raw audio bytes (optional, will use microphone if None)
            language: Language for speech recognition
            use_microphone: Whether to use microphone for input
            
        Returns:
            Dict containing processed query and response
        """
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return self._get_mock_voice_response()
        
        try:
            # Step 1: Convert speech to text
            if use_microphone:
                text_query = await self._speech_to_text_microphone(language)
            else:
                text_query = await self._speech_to_text_audio(audio_data, language)
            
            if not text_query:
                return {
                    'status': 'error',
                    'message': 'Could not understand speech',
                    'language': language
                }
            
            # Step 2: Translate to English if needed
            english_query = await self._translate_to_english(text_query, language)
            
            # Step 3: Process through agent pipeline
            agent_response = await self._process_through_agents(english_query)
            
            # Step 4: Translate response back to user's language
            localized_response = await self._translate_from_english(
                agent_response['text'], language
            )
            
            # Step 5: Generate audio response
            audio_response = await self._text_to_speech(localized_response, language)
            
            return {
                'status': 'success',
                'original_query': text_query,
                'english_query': english_query,
                'agent_response': agent_response,
                'localized_text': localized_response,
                'audio_response': audio_response,
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing voice query: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'language': language
            }
    
    async def _speech_to_text_microphone(self, language: str) -> str:
        """Convert speech from microphone to text"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return "Mock speech input"
        
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Listening for speech...")
                
                # Listen for speech with timeout
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
            
            # Use Azure Speech Service for better Indian language support
            if self.azure_speech_key and language != 'english':
                return await self._azure_speech_to_text(audio, language)
            else:
                # Use Google Speech Recognition
                lang_code = self.supported_languages[language]['locale']
                text = self.recognizer.recognize_google(audio, language=lang_code)
                return text
                
        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout")
            return ""
        except sr.UnknownValueError:
            logger.warning("Could not understand speech")
            return ""
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return ""
    
    async def _speech_to_text_audio(self, audio_data: bytes, language: str) -> str:
        """Convert audio bytes to text"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return "Mock audio input"
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load audio file
            with sr.AudioFile(temp_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Recognize speech
            if self.azure_speech_key and language != 'english':
                return await self._azure_speech_to_text(audio, language)
            else:
                lang_code = self.supported_languages[language]['locale']
                text = self.recognizer.recognize_google(audio, language=lang_code)
                return text
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return ""
    
    async def _azure_speech_to_text(self, audio, language: str) -> str:
        """Use Azure Speech Service for better Indian language support"""
        try:
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key, 
                region=self.azure_region
            )
            speech_config.speech_recognition_language = self.supported_languages[language]['locale']
            
            # Create audio config from the recorded audio
            # Note: This is a simplified implementation
            # In practice, you'd need to convert the audio format properly
            
            # For now, fall back to Google Speech Recognition
            lang_code = self.supported_languages[language]['locale']
            text = self.recognizer.recognize_google(audio, language=lang_code)
            return text
            
        except Exception as e:
            logger.error(f"Azure speech recognition error: {e}")
            # Fallback to Google
            lang_code = self.supported_languages[language]['locale']
            return self.recognizer.recognize_google(audio, language=lang_code)
    
    async def _translate_to_english(self, text: str, source_language: str) -> str:
        """Translate text to English if needed"""
        if source_language == 'english' or not VOICE_DEPENDENCIES_AVAILABLE:
            return text
        
        try:
            source_code = self.supported_languages[source_language]['code']
            translated = self.translator.translate(text, src=source_code, dest='en')
            return translated.text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original if translation fails
    
    async def _translate_from_english(self, text: str, target_language: str) -> str:
        """Translate text from English to target language"""
        if target_language == 'english' or not VOICE_DEPENDENCIES_AVAILABLE:
            return text
        
        try:
            target_code = self.supported_languages[target_language]['code']
            translated = self.translator.translate(text, src='en', dest=target_code)
            return translated.text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original if translation fails
    
    async def _process_through_agents(self, query: str) -> Dict:
        """Process query through the existing agent pipeline"""
        # This would integrate with the existing agent system
        # For now, return a mock response
        
        return {
            'text': f"Thank you for your query: '{query}'. Our AI agents are analyzing your needs and will provide personalized recommendations shortly.",
            'recommendations': [
                {
                    'title': 'ET Masterclass: Investment Basics',
                    'url': 'https://economictimes.indiatimes.com/et-masterclass',
                    'type': 'education'
                },
                {
                    'title': 'ET Money: SIP Calculator',
                    'url': 'https://etmoney.com/sip-calculator',
                    'type': 'tool'
                }
            ],
            'next_steps': [
                'Complete your risk assessment',
                'Explore recommended investment options',
                'Start your learning journey'
            ]
        }
    
    async def _text_to_speech(self, text: str, language: str) -> bytes:
        """Convert text to speech in specified language"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return b"Mock audio response"
        
        try:
            # For Indian languages, use Azure Speech Service if available
            if self.azure_speech_key and language != 'english':
                return await self._azure_text_to_speech(text, language)
            else:
                return await self._pyttsx3_text_to_speech(text)
                
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return b""
    
    async def _azure_text_to_speech(self, text: str, language: str) -> bytes:
        """Use Azure Speech Service for natural Indian language voices"""
        try:
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key, 
                region=self.azure_region
            )
            
            # Set voice based on language
            voice_map = {
                'hindi': 'hi-IN-SwaraNeural',
                'tamil': 'ta-IN-PallaviNeural',
                'telugu': 'te-IN-ShrutiNeural',
                'gujarati': 'gu-IN-DhwaniNeural',
                'bengali': 'bn-IN-BashkarNeural',
                'marathi': 'mr-IN-AarohiNeural',
                'kannada': 'kn-IN-SapnaNeural',
                'english': 'en-IN-NeerjaNeural'
            }
            
            speech_config.speech_synthesis_voice_name = voice_map.get(language, 'en-IN-NeerjaNeural')
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                logger.error(f"Azure TTS error: {result.reason}")
                return await self._pyttsx3_text_to_speech(text)
                
        except Exception as e:
            logger.error(f"Azure TTS error: {e}")
            return await self._pyttsx3_text_to_speech(text)
    
    async def _pyttsx3_text_to_speech(self, text: str) -> bytes:
        """Use pyttsx3 for text-to-speech (fallback)"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Generate speech
            self.tts_engine.save_to_file(text, temp_file_path)
            self.tts_engine.runAndWait()
            
            # Read audio data
            with open(temp_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up
            os.unlink(temp_file_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"pyttsx3 TTS error: {e}")
            return b""
    
    def _get_mock_voice_response(self) -> Dict:
        """Mock voice response for development/demo purposes"""
        return {
            'status': 'success',
            'original_query': 'मुझे निवेश के बारे में जानकारी चाहिए',
            'english_query': 'I need information about investment',
            'agent_response': {
                'text': 'I can help you learn about investments. Let me recommend some resources.',
                'recommendations': [
                    {
                        'title': 'ET Masterclass: Investment Basics',
                        'url': 'https://economictimes.indiatimes.com/et-masterclass',
                        'type': 'education'
                    }
                ]
            },
            'localized_text': 'मैं आपको निवेश के बारे में सीखने में मदद कर सकता हूं। मुझे कुछ संसाधन सुझाने दें।',
            'audio_response': b'mock_audio_data',
            'language': 'hindi',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.supported_languages.keys())
    
    async def test_voice_interface(self, language: str = 'english') -> Dict:
        """Test the voice interface functionality"""
        logger.info(f"Testing voice interface in {language}")
        
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return self._get_mock_voice_response()
        
        # Test with mock input
        mock_query = {
            'english': 'I want to start investing in mutual funds',
            'hindi': 'मुझे म्यूचुअल फंड में निवेश शुरू करना है',
            'tamil': 'நான் மியூச்சுவல் ஃபண்டில் முதலீடு செய்ய ஆரம்பிக்க விரும்புகிறேன்'
        }.get(language, 'I want to start investing')
        
        # Simulate processing
        response = await self._process_through_agents(mock_query)
        
        return {
            'status': 'test_success',
            'language': language,
            'mock_query': mock_query,
            'response': response,
            'supported_languages': self.get_supported_languages()
        }


class VoiceCommandProcessor:
    """
    Process voice commands for specific actions
    
    Handles commands like:
    - "Show me SIP calculator"
    - "What are today's market trends?"
    - "Explain mutual funds in Hindi"
    """
    
    def __init__(self):
        self.voice_interface = VoiceInterface()
        self.command_patterns = {
            'calculator': ['calculator', 'calculate', 'compute'],
            'market_data': ['market', 'stock', 'price', 'trend'],
            'education': ['explain', 'learn', 'teach', 'what is'],
            'recommendation': ['recommend', 'suggest', 'advise'],
            'portfolio': ['portfolio', 'investment', 'holdings']
        }
    
    async def process_voice_command(self, audio_data: bytes = None, 
                                  language: str = 'english') -> Dict:
        """Process voice command and execute appropriate action"""
        
        # Get voice input
        voice_result = await self.voice_interface.process_voice_query(
            audio_data, language, use_microphone=(audio_data is None)
        )
        
        if voice_result['status'] != 'success':
            return voice_result
        
        # Analyze command intent
        command_intent = self._analyze_command_intent(voice_result['english_query'])
        
        # Execute appropriate action
        action_result = await self._execute_command_action(
            command_intent, voice_result['english_query']
        )
        
        # Combine results
        return {
            **voice_result,
            'command_intent': command_intent,
            'action_result': action_result
        }
    
    def _analyze_command_intent(self, query: str) -> str:
        """Analyze the intent of the voice command"""
        query_lower = query.lower()
        
        for intent, patterns in self.command_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return 'general_query'
    
    async def _execute_command_action(self, intent: str, query: str) -> Dict:
        """Execute the appropriate action based on command intent"""
        
        actions = {
            'calculator': self._handle_calculator_request,
            'market_data': self._handle_market_data_request,
            'education': self._handle_education_request,
            'recommendation': self._handle_recommendation_request,
            'portfolio': self._handle_portfolio_request,
            'general_query': self._handle_general_query
        }
        
        handler = actions.get(intent, self._handle_general_query)
        return await handler(query)
    
    async def _handle_calculator_request(self, query: str) -> Dict:
        """Handle calculator-related requests"""
        return {
            'action': 'open_calculator',
            'tool': 'ET Money SIP Calculator',
            'url': 'https://etmoney.com/sip-calculator',
            'description': 'Opening SIP calculator for your investment planning'
        }
    
    async def _handle_market_data_request(self, query: str) -> Dict:
        """Handle market data requests"""
        return {
            'action': 'show_market_data',
            'tool': 'ET Markets',
            'url': 'https://economictimes.indiatimes.com/markets',
            'description': 'Showing current market trends and stock prices'
        }
    
    async def _handle_education_request(self, query: str) -> Dict:
        """Handle educational content requests"""
        return {
            'action': 'provide_education',
            'tool': 'ET Masterclass',
            'url': 'https://economictimes.indiatimes.com/et-masterclass',
            'description': 'Providing educational content on your topic of interest'
        }
    
    async def _handle_recommendation_request(self, query: str) -> Dict:
        """Handle recommendation requests"""
        return {
            'action': 'generate_recommendations',
            'description': 'Generating personalized investment recommendations',
            'next_step': 'Complete profile assessment for better recommendations'
        }
    
    async def _handle_portfolio_request(self, query: str) -> Dict:
        """Handle portfolio-related requests"""
        return {
            'action': 'analyze_portfolio',
            'tool': 'ET Money Portfolio',
            'description': 'Analyzing your investment portfolio and performance'
        }
    
    async def _handle_general_query(self, query: str) -> Dict:
        """Handle general queries"""
        return {
            'action': 'general_assistance',
            'description': 'Processing your query through our AI agents',
            'next_step': 'Our agents will provide personalized guidance'
        }


# Usage example
async def demo_voice_interface():
    """Demo the voice interface functionality"""
    voice_interface = VoiceInterface()
    
    # Test supported languages
    languages = voice_interface.get_supported_languages()
    print(f"Supported languages: {languages}")
    
    # Test voice interface
    for language in ['english', 'hindi']:
        result = await voice_interface.test_voice_interface(language)
        print(f"\nTest result for {language}:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(demo_voice_interface())