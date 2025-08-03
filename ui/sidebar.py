"""
Sidebar components for the Mental Health Support app
"""

import streamlit as st
from config.settings import AUSTRALIAN_CRISIS_RESOURCES

def render_sidebar(voice_available=False):
    """Render the sidebar with crisis resources and app info"""
    with st.sidebar:
        # Crisis Resources
        st.markdown("### 🆘 Crisis Resources")
        st.markdown(AUSTRALIAN_CRISIS_RESOURCES, unsafe_allow_html=True)
        
        # Voice Features Status
        if voice_available:
            st.markdown("### 🎤 Voice Enabled")
            st.markdown("""
            <div class="sidebar-section">
            🎤 Microphone button available<br>
            🔊 Auto-voice for bot responses<br>
            Speak naturally for best results
            </div>
            """, unsafe_allow_html=True)
        
        # Supportive Reminders
        st.markdown("### 💜 Remember")
        st.markdown("""
        <div class="sidebar-section">
        • You are not alone<br>
        • Your feelings are valid<br>
        • Help is available<br>
        • You matter
        </div>
        """, unsafe_allow_html=True)

def render_crisis_resources():
    """Render just the crisis resources section"""
    st.markdown("### 🆘 Crisis Resources")
    st.markdown(AUSTRALIAN_CRISIS_RESOURCES, unsafe_allow_html=True)

def render_voice_status(voice_available):
    """Render voice feature status"""
    if voice_available:
        st.markdown("### 🎤 Voice Enabled")
        st.markdown("""
        <div class="sidebar-section">
        🎤 Microphone button available<br>
        🔊 Auto-voice for bot responses<br>
        Speak naturally for best results
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 🎤 Voice Features")
        st.markdown("""
        <div class="sidebar-section">
        Voice features are not available.<br>
        Install required packages to enable.
        </div>
        """, unsafe_allow_html=True)

def render_supportive_reminders():
    """Render supportive reminders section"""
    st.markdown("### 💜 Remember")
    st.markdown("""
    <div class="sidebar-section">
    • You are not alone<br>
    • Your feelings are valid<br>
    • Help is available<br>
    • You matter
    </div>
    """, unsafe_allow_html=True)