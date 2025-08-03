"""
Chat display components for the Mental Health Support app
"""

import streamlit as st

def render_chat_history(chat_history):
    """Render the chat history with proper styling"""
    if chat_history:
        for i, (role, message) in enumerate(chat_history):
            if role == "user":
                st.markdown(f'<div class="user-message">{message}</div>', unsafe_allow_html=True)
            else:
                if "🆘 **Immediate Help Available" in message:
                    st.markdown(f'<div class="crisis-alert">{message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">{message}</div>', unsafe_allow_html=True)

def render_loading_message():
    """Render a loading message while bot is thinking"""
    st.markdown('<div class="bot-loading">💭 <span class="typing-dots">Thinking</span></div>', unsafe_allow_html=True)

def format_message_for_display(message, role):
    """Format message content for proper display"""
    # Clean up any extra whitespace
    message = message.strip()
    
    # Handle line breaks for better formatting
    if role == "bot" and "\n\n" in message:
        # Convert double line breaks to HTML breaks for better spacing
        message = message.replace("\n\n", "<br><br>")
    
    return message