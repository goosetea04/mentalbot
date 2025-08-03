"""
Input handling and action button components
"""

import streamlit as st
import random
from config.settings import WELCOME_MESSAGES, AFFIRMATIONS
from utils.text_processing import detect_crisis_keywords, make_response_casual

def render_input_section(voice_handler):
    """Render the input section with text input and microphone button"""
    input_col, mic_col = st.columns([5, 1])
    
    with input_col:
        user_input = st.chat_input("Share what's on your mind...")
    
    with mic_col:
        if voice_handler.is_available():
            if st.button("🎤", help="Click to speak", use_container_width=True, key="mic_button"):
                speech_text = voice_handler.listen_for_speech()
                if speech_text:
                    st.success(f"You said: '{speech_text}'")
                    # Return the speech text to be processed
                    return speech_text
        else:
            st.markdown('<div style="padding: 12px; text-align: center; color: #999;">🎤</div>', unsafe_allow_html=True)
    
    return user_input

def process_voice_input(voice_handler, qa_chain):
    """Process voice input and add to chat"""
    speech_text = voice_handler.listen_for_speech()
    if speech_text:
        st.success(f"You said: '{speech_text}'")
        try:
            is_crisis = detect_crisis_keywords(speech_text)
            response = qa_chain.invoke({"question": speech_text})
            answer = make_response_casual(response["answer"])
            
            # Add to chat history
            st.session_state.chat_history.append(("user", speech_text))
            
            if is_crisis:
                from config.settings import CRISIS_RESOURCES
                crisis_response = f"I can see you're going through something difficult. You're not alone. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
                st.session_state.chat_history.append(("bot", crisis_response))
            else:
                st.session_state.chat_history.append(("bot", answer))
            
            # Mark that we need to generate audio for the new bot message
            if voice_handler.is_available():
                message_id = len(st.session_state.chat_history) - 1
                st.session_state.pending_audio = message_id
            
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")

def render_action_buttons(voice_available):
    """Render action buttons for new conversation and daily affirmation"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.generating_response = False
            st.session_state.audio_generated = set()  # Reset audio tracking
            st.session_state.pending_audio = None
            welcome_msg = random.choice(WELCOME_MESSAGES)
            st.session_state.chat_history.append(("bot", welcome_msg))
            # Mark that we need to generate audio for the welcome message
            if voice_available:
                st.session_state.pending_audio = 0
            st.rerun()
    
    with col2:
        if st.button("💝 Daily Affirmation", use_container_width=True):
            affirmation = random.choice(AFFIRMATIONS)
            st.session_state.chat_history.append(("bot", f"Here's a gentle reminder: {affirmation}"))
            # Mark that we need to generate audio for the affirmation
            if voice_available:
                message_id = len(st.session_state.chat_history) - 1
                st.session_state.pending_audio = message_id
            st.rerun()

def handle_user_input_processing(user_input, qa_chain):
    """Handle processing of user input and generate bot response"""
    from config.settings import CRISIS_RESOURCES
    
    try:
        # Check for crisis
        is_crisis = detect_crisis_keywords(user_input)
        
        # Get response
        response = qa_chain.invoke({"question": user_input})
        answer = make_response_casual(response["answer"])
        
        # Add bot response to history
        if is_crisis:
            crisis_response = f"I can see you're going through something really difficult right now. You're not alone. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
            st.session_state.chat_history.append(("bot", crisis_response))
        else:
            st.session_state.chat_history.append(("bot", answer))
        
        return True
    except Exception as e:
        st.session_state.chat_history.append(("bot", f"I apologize, but I encountered an error: {e}. Please try again."))
        return False