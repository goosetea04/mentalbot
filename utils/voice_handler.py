"""
Voice processing handler for the Mental Health Support app
"""

import streamlit as st
import base64
import time
from config.settings import VOICE_FEATURES_AVAILABLE, VOICE_CONFIG, OPENAI_API_KEY
from utils.text_processing import enhance_text_for_speech

if VOICE_FEATURES_AVAILABLE:
    import speech_recognition as sr
    from gtts import gTTS
    import io

class VoiceHandler:
    def __init__(self):
        self.available = VOICE_FEATURES_AVAILABLE
        self.config = VOICE_CONFIG
        
    def is_available(self):
        """Check if voice features are available"""
        return self.available
    
    def listen_for_speech(self):
        """Simple speech recognition"""
        if not self.available:
            return None
        
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎤 Listening... speak now")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(
                    source, 
                    timeout=self.config["listen_timeout"], 
                    phrase_time_limit=self.config["phrase_time_limit"]
                )
            
            st.info("Processing...")
            return recognizer.recognize_google(audio)
        except Exception as e:
            st.warning("Could not understand audio. Please try again.")
            return None
    
    def text_to_speech_gtts(self, text):
        """Convert text to speech using gTTS (fallback method)"""
        if not self.available:
            return None
        
        try:
            import re
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            clean_text = re.sub(r'[^\w\s.,!?;:\'-]', '', clean_text)
            clean_text = re.sub(r'\n+', '. ', clean_text)
            
            tts = gTTS(text=clean_text, lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode()
            return f"""
            <audio controls style="width: 100%; margin: 10px 0;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """
        except Exception:
            return None
    
    def text_to_speech_openai(self, text):
        """Convert text to speech using OpenAI TTS"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=OPENAI_API_KEY)
            enhanced_text = enhance_text_for_speech(text)
            
            response = client.audio.speech.create(
                model=self.config["tts_model"],
                voice=self.config["voice"],
                input=enhanced_text,
                speed=self.config["speed"]
            )
            
            audio_base64 = base64.b64encode(response.content).decode()
            
            return f"""
            <audio controls autoplay style="width: 100%; margin: 10px 0;">
                <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
            </audio>
            """
        except Exception as e:
            # Fallback to gTTS if OpenAI fails
            return self.text_to_speech_gtts(text)
    
    def text_to_speech_with_progress(self, text):
        """
        Convert text to speech with progress indicator
        """
        try:
            # Show loading message
            loading_placeholder = st.empty()
            loading_placeholder.markdown(
                '<div class="tts-loading">🎵 Converting to speech...</div>', 
                unsafe_allow_html=True
            )
            
            # Create progress bar
            progress_bar = st.progress(0)
            
            # Simulate progress steps
            progress_bar.progress(10)
            time.sleep(0.1)
            
            progress_bar.progress(30)
            time.sleep(0.1)
            
            # Try OpenAI TTS first
            audio_html = self.text_to_speech_openai(text)
            
            progress_bar.progress(70)
            time.sleep(0.1)
            
            progress_bar.progress(90)
            time.sleep(0.1)
            
            progress_bar.progress(100)
            time.sleep(0.2)
            
            # Clear loading indicators
            loading_placeholder.empty()
            progress_bar.empty()
            
            return audio_html
            
        except Exception as e:
            # Clear loading indicators on error
            if 'loading_placeholder' in locals():
                loading_placeholder.empty()
            if 'progress_bar' in locals():
                progress_bar.empty()
            return None
    
    def process_voice_input(self, qa_chain, chat_history, callback_func):
        """Process voice input and return the result"""
        speech_text = self.listen_for_speech()
        if speech_text:
            st.success(f"You said: '{speech_text}'")
            return speech_text
        return None