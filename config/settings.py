"""
Configuration settings and constants for the Mental Health Support app
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Voice feature availability check
try:
    import speech_recognition as sr
    from gtts import gTTS
    VOICE_FEATURES_AVAILABLE = True
except ImportError:
    VOICE_FEATURES_AVAILABLE = False

# Crisis resources
CRISIS_RESOURCES = """
🆘 **Immediate Help Available 24/7:**

• **988** - Suicide & Crisis Lifeline
• **Text HOME to 741741** - Crisis Text Line
• **911** - Emergency Services

You matter. Help is available right now. 💙
"""

# Australian Crisis Resources (for sidebar)
AUSTRALIAN_CRISIS_RESOURCES = """
<div class="sidebar-section">
    <strong>24/7 Support (Canberra):</strong><br>
    📞 <strong>Lifeline: 13 11 14</strong> – Crisis Support<br>
    💬 <strong>Text 0477 13 11 14</strong> – Lifeline Text Service<br>
    🧠 <strong>Beyond Blue: 1300 22 4636</strong> – Mental Health Support<br>
    🚨 <strong>000</strong> – Emergency Services<br>
</div>
"""

# Welcome messages
WELCOME_MESSAGES = [
    "Hey there! How are you doing today?",
    "Hi! What's going on with you?",
    "Hello! How can I help you out?",
    "Hey! What's on your mind?",
    "Hi there! How are you feeling right now?"
]

# Daily affirmations
AFFIRMATIONS = [
    "You're doing better than you think 💕",
    "Your feelings make total sense 🌙", 
    "You've got this ✨",
    "You're stronger than you realize 💪",
    "You matter, always 🌍",
    "It's okay to not be okay right now",
    "You're not alone in this 💙",
    "Take it one moment at a time"
]

# Crisis detection keywords
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end it all", "self harm", 
    "hurt myself", "don't want to live"
]

# QA Chain settings
QA_CHAIN_CONFIG = {
    "temperature": 0.8,
    "search_kwargs": {"k": 2},
    "vector_store_path": "mental_health_index"
}

# Voice settings
VOICE_CONFIG = {
    "tts_model": "tts-1",
    "voice": "nova",
    "speed": 0.98,
    "listen_timeout": 5,
    "phrase_time_limit": 5
}

# Text processing settings
CASUAL_REPLACEMENTS = {
    "It's important to": "",
    "I recommend": "Maybe try",
    "Consider": "You might",
    "It would be beneficial": "It could help"
}

FOLLOW_UP_QUESTIONS = [
    " How does that sound?",
    " What do you think?", 
    " Does that resonate with you?",
    " How are you feeling about that?",
    ""  # Sometimes no follow-up
]