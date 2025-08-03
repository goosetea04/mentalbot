import streamlit as st
import random
from datetime import datetime

from config.settings import *
from utils.text_processing import make_response_casual, detect_crisis_keywords
from utils.voice_handler import VoiceHandler
from utils.qa_chain import initialize_qa_chain
from ui.styles import apply_custom_css
from ui.sidebar import render_sidebar
from ui.chat_display import render_chat_history
from ui.input_handlers import render_input_section, render_action_buttons

# Streamlit Configuration
st.set_page_config(
    page_title="Mental Health Support", 
    page_icon="💙",
    layout="centered"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        welcome_msg = random.choice(WELCOME_MESSAGES)
        st.session_state.chat_history.append(("bot", welcome_msg))

    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = initialize_qa_chain()

    if "generating_response" not in st.session_state:
        st.session_state.generating_response = False

    if "audio_generated" not in st.session_state:
        st.session_state.audio_generated = set()

    if "pending_audio" not in st.session_state:
        st.session_state.pending_audio = None

    if "voice_handler" not in st.session_state:
        st.session_state.voice_handler = VoiceHandler()

def process_user_input(user_input):
    """Process user input and generate bot response"""
    try:
        # Check for crisis
        is_crisis = detect_crisis_keywords(user_input)
        
        # Get response
        response = st.session_state.qa_chain.invoke({"question": user_input})
        answer = make_response_casual(response["answer"])
        
        # Add bot response to history
        if is_crisis:
            crisis_response = f"I can see you're going through something really difficult right now. You're not alone. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
            st.session_state.chat_history.append(("bot", crisis_response))
        else:
            st.session_state.chat_history.append(("bot", answer))
        
        # Mark that we need to generate audio for the new bot message
        if st.session_state.voice_handler.is_available():
            message_id = len(st.session_state.chat_history) - 1
            st.session_state.pending_audio = message_id
        
        return True
    except Exception as e:
        st.session_state.chat_history.append(("bot", f"I apologize, but I encountered an error: {e}. Please try again."))
        return False

def handle_pending_audio():
    """Handle pending audio generation"""
    if st.session_state.voice_handler.is_available() and st.session_state.pending_audio is not None:
        message_index = st.session_state.pending_audio
        if message_index < len(st.session_state.chat_history):
            role, message = st.session_state.chat_history[message_index]
            if role == "bot" and message_index not in st.session_state.audio_generated:
                audio_html = st.session_state.voice_handler.text_to_speech_with_progress(message)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
                st.session_state.audio_generated.add(message_index)
        
        # Clear pending audio
        st.session_state.pending_audio = None

def main():
    # Initialize everything
    initialize_session_state()
    
    # Header
    st.title("💙 Mental Health Support")
    st.markdown("<p class='subtitle'>A safe space for mental wellness guidance</p>", unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar(st.session_state.voice_handler.is_available())
    
    # Chat display
    render_chat_history(st.session_state.chat_history)
    
    # Handle pending audio generation
    handle_pending_audio()
    
    # Show loading bubble if bot is generating response
    if st.session_state.generating_response:
        st.markdown('<div class="bot-loading">💭 <span class="typing-dots">Thinking</span></div>', unsafe_allow_html=True)
    
    # Input section
    user_input = render_input_section(st.session_state.voice_handler)
    
    # Process user input
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.generating_response = True
    
    # Process the response if we're in generating state
    if st.session_state.generating_response and st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]
        if last_message[0] == "user":  # Last message is from user and we need to respond
            user_question = last_message[1]
            success = process_user_input(user_question)
            st.session_state.generating_response = False
            st.rerun()
    
    # Action buttons
    render_action_buttons(st.session_state.voice_handler.is_available())
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9em; margin-top: 1rem;">
        💙 You are not alone. Help is always available. 💙
    </div>
    """, unsafe_allow_html=True)
    
    # Voice setup info
    if not st.session_state.voice_handler.is_available():
        with st.expander("Enable Voice Features"):
            st.info("""
            To add voice capabilities, install:
            ```bash
            pip install SpeechRecognition gtts pyaudio
            ```
            Then restart the app.
            """)

if __name__ == "__main__":
    main()