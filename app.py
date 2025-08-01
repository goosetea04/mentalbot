import streamlit as st
from dotenv import load_dotenv
import os
import random
from datetime import datetime
import re
import io
import base64
import time

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Audio processing imports
try:
    import speech_recognition as sr
    from gtts import gTTS
    import io
    import base64
    VOICE_FEATURES_AVAILABLE = True
except ImportError:
    VOICE_FEATURES_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize components
@st.cache_resource
def initialize_qa_chain():
    """Initialize the QA chain with caching"""
    embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    vectorstore = FAISS.load_local(
        "mental_health_index",
        embedding_model,
        allow_dangerous_deserialization=True
    )
    
    custom_prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""You are a compassionate mental health first aid assistant. Speak with warmth, empathy, and understanding while providing evidence-based guidance.

Use the following context: {context}
Previous conversation: {chat_history}
Question: {question}

Respond with genuine care and practical support. If this seems like a crisis, prioritize safety resources."""
    )
    
    llm = OpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt}
    )

# Voice functions
def listen_for_speech():
    """Simple speech recognition"""
    if not VOICE_FEATURES_AVAILABLE:
        return None
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... speak now")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        st.info("Processing...")
        return recognizer.recognize_google(audio)
    except Exception as e:
        st.warning("Could not understand audio. Please try again.")
        return None

def text_to_speech(text):
    """Convert text to speech"""
    if not VOICE_FEATURES_AVAILABLE:
        return None
    
    try:
        # Clean text for better speech
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

# Crisis detection
def detect_crisis_keywords(text):
    crisis_words = ["suicide", "kill myself", "end it all", "self harm", "hurt myself", "don't want to live"]
    return any(word in text.lower() for word in crisis_words)

# Constants
CRISIS_RESOURCES = """
🆘 **Immediate Help Available 24/7:**

• **988** - Suicide & Crisis Lifeline
• **Text HOME to 741741** - Crisis Text Line
• **911** - Emergency Services

You matter. Help is available right now. 💙
"""

WELCOME_MESSAGES = [
    "Hi there! I'm here to support you with mental health guidance. How are you feeling today? 💙",
    "Hello! I'm your mental health first aid companion. What's on your mind? 🌸",
    "Hey! I'm here to listen and help. How can I support you today? ✨"
]

# Streamlit Configuration
st.set_page_config(
    page_title="Mental Health Support", 
    page_icon="💙",
    layout="centered"
)

# Simple, soothing CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2d3748;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px auto 10px 0;
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);
        line-height: 1.6;
    }
    
    .crisis-alert {
        background: #ffe6e6;
        border: 2px solid #ff6b6b;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: #c53030;
        font-weight: 500;
    }
    
    .input-section {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 10px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .mic-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 18px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .mic-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
    }
    
    .sidebar-section {
        background: rgba(255, 255, 255, 0.8);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }
    
    h1 {
        color: #4a5568;
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .tts-loading {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        color: #2d3436;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: center;
        font-size: 0.9em;
        animation: pulse 1.5s ease-in-out infinite alternate;
    }
    
    @keyframes pulse {
        from { opacity: 0.7; }
        to { opacity: 1; }
    }
    
    .bot-loading {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2d3748;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px auto 10px 0;
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);
        line-height: 1.6;
        text-align: center;
        animation: pulse 1.5s ease-in-out infinite alternate;
    }
    
    .typing-dots {
        display: inline-block;
        animation: typing 1.4s infinite;
    }
    
    .typing-dots::after {
        content: '...';
        animation: dots 1.4s steps(4, end) infinite;
    }
    
    @keyframes typing {
        0%, 20% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    welcome_msg = random.choice(WELCOME_MESSAGES)
    st.session_state.chat_history.append(("bot", welcome_msg))

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = initialize_qa_chain()

if "generating_response" not in st.session_state:
    st.session_state.generating_response = False

# Header
st.title("💙 Mental Health Support")
st.markdown("<p class='subtitle'>A safe space for mental wellness guidance</p>", unsafe_allow_html=True)

# Sidebar with essential resources
with st.sidebar:
    st.markdown("### 🆘 Crisis Resources")
    st.markdown("""
    <div class="sidebar-section">
        <strong>24/7 Support (Canberra):</strong><br>
        📞 <strong>Lifeline: 13 11 14</strong> – Crisis Support<br>
        💬 <strong>Text 0477 13 11 14</strong> – Lifeline Text Service<br>
        🧠 <strong>Beyond Blue: 1300 22 4636</strong> – Mental Health Support<br>
        🚨 <strong>000</strong> – Emergency Services<br>
    </div>
    """, unsafe_allow_html=True)
    
    if VOICE_FEATURES_AVAILABLE:
        st.markdown("### 🎤 Voice Enabled")
        st.markdown("""
        <div class="sidebar-section">
        🎤 Microphone button available<br>
        🔊 Auto-voice for bot responses<br>
        Speak naturally for best results
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💜 Remember")
    st.markdown("""
    <div class="sidebar-section">
    • You are not alone<br>
    • Your feelings are valid<br>
    • Help is available<br>
    • You matter
    </div>
    """, unsafe_allow_html=True)

def enhance_text_for_speech(text):
    """Enhanced text preprocessing for more natural speech"""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Handle special characters and formatting
    text = re.sub(r'💙|💕|🌙|✨|💪|🌍|🆘|📞|💬|🚨|💜|🎤|🔊', '', text)  # Remove emojis
    text = re.sub(r'•', 'and', text)  # Replace bullets
    text = re.sub(r'\n+', '. ', text)  # Convert line breaks to pauses
    
    # Add natural pauses and emphasis
    text = re.sub(r'(\w+):', r'\1, ', text)  # Convert colons to natural pauses
    text = re.sub(r'(\d{3})', r'\1 ', text)  # Add space in phone numbers like "988"
    
    # Handle crisis resources more naturally
    text = re.sub(r'988', 'nine eight eight', text)
    text = re.sub(r'741741', 'seven four one, seven four one', text)
    text = re.sub(r'911', 'nine one one', text)
    
    # Add natural speech patterns
    text = re.sub(r'^(Hi|Hello|Hey)', r'\1 there', text)
    text = re.sub(r'You are not alone', 'Remember, you are not alone', text)
    
    # Clean up extra spaces and punctuation
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    
    return text.strip()

def text_to_speech_openai_with_progress(text):
    """
    OpenAI TTS with progress bar
    """
    try:
        from openai import OpenAI
        
        # Show loading message
        loading_placeholder = st.empty()
        loading_placeholder.markdown('<div class="tts-loading">🎵 Converting to speech...</div>', unsafe_allow_html=True)
        
        # Create progress bar
        progress_bar = st.progress(0)
        
        # Simulate progress steps
        progress_bar.progress(10)
        time.sleep(0.1)
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        enhanced_text = enhance_text_for_speech(text)
        
        progress_bar.progress(30)
        time.sleep(0.1)
        
        response = client.audio.speech.create(
            model="tts-1",              # Faster model
            voice="nova",               # Friendly, natural-sounding voice
            input=enhanced_text,
            speed=0.98                  # Slightly faster, more casual flow
        )
        
        progress_bar.progress(70)
        time.sleep(0.1)
        
        audio_base64 = base64.b64encode(response.content).decode()
        
        progress_bar.progress(90)
        time.sleep(0.1)
        
        audio_html = f"""
        <audio controls autoplay style="width: 100%; margin: 10px 0;">
            <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
        </audio>
        """
        
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

# Voice input handling function
def process_voice_input():
    """Process voice input and add to chat"""
    speech_text = listen_for_speech()
    if speech_text:
        st.success(f"You said: '{speech_text}'")
        # Process the speech input
        try:
            is_crisis = detect_crisis_keywords(speech_text)
            response = st.session_state.qa_chain.invoke({"question": speech_text})
            answer = response["answer"]
            
            # Add to chat history
            st.session_state.chat_history.append(("user", speech_text))
            
            if is_crisis:
                crisis_response = f"I can see you're going through something difficult. You're not alone. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
                st.session_state.chat_history.append(("bot", crisis_response))
            else:
                st.session_state.chat_history.append(("bot", answer))
            
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Chat display with auto voice and progress bars
if st.session_state.chat_history:
    for i, (role, message) in enumerate(st.session_state.chat_history):
        if role == "user":
            st.markdown(f'<div class="user-message">{message}</div>', unsafe_allow_html=True)
        else:
            if "🆘 **Immediate Help Available" in message:
                st.markdown(f'<div class="crisis-alert">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{message}</div>', unsafe_allow_html=True)
            
            # Auto-generate audio for bot messages if voice is available
            if VOICE_FEATURES_AVAILABLE and role == "bot":
                # Use a unique key for each message to avoid conflicts
                audio_key = f"audio_{i}_{hash(message[:50])}"
                
                # Only generate audio for the latest bot message to avoid multiple audio generations
                if i == len(st.session_state.chat_history) - 1:
                    audio_html = text_to_speech_openai_with_progress(message)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)

# Show loading bubble if bot is generating response
if st.session_state.generating_response:
    st.markdown('<div class="bot-loading">💭 <span class="typing-dots">Thinking</span></div>', unsafe_allow_html=True)

# Chat input with microphone button
input_col, mic_col = st.columns([5, 1])

with input_col:
    user_input = st.chat_input("Share what's on your mind...")

with mic_col:
    if VOICE_FEATURES_AVAILABLE:
        if st.button("🎤", help="Click to speak", use_container_width=True, key="mic_button"):
            process_voice_input()
    else:
        st.markdown('<div style="padding: 12px; text-align: center; color: #999;">🎤</div>', unsafe_allow_html=True)

if user_input:
    # Add user message immediately to chat
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.generating_response = True
    st.rerun()

# Process the response if we're in generating state
if st.session_state.generating_response and st.session_state.chat_history:
    last_message = st.session_state.chat_history[-1]
    if last_message[0] == "user":  # Last message is from user and we need to respond
        try:
            user_question = last_message[1]
            
            # Check for crisis
            is_crisis = detect_crisis_keywords(user_question)
            
            # Get response
            response = st.session_state.qa_chain.invoke({"question": user_question})
            answer = response["answer"]
            
            # Add bot response to history
            if is_crisis:
                crisis_response = f"I can see you're going through something really difficult right now. You're not alone. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
                st.session_state.chat_history.append(("bot", crisis_response))
            else:
                st.session_state.chat_history.append(("bot", answer))
            
            # Stop generating
            st.session_state.generating_response = False
            st.rerun()
            
        except Exception as e:
            st.session_state.chat_history.append(("bot", f"I apologize, but I encountered an error: {e}. Please try again."))
            st.session_state.generating_response = False
            st.rerun()

# Simple action buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.generating_response = False
        welcome_msg = random.choice(WELCOME_MESSAGES)
        st.session_state.chat_history.append(("bot", welcome_msg))
        st.rerun()

with col2:
    if st.button("💝 Daily Affirmation", use_container_width=True):
        affirmations = [
            "You are worthy of love and kindness 💕",
            "Your feelings are valid 🌙",
            "You have survived 100% of your difficult days ✨",
            "You are stronger than you know 💪",
            "You belong here and you matter 🌍"
        ]
        affirmation = random.choice(affirmations)
        st.session_state.chat_history.append(("bot", f"Here's a gentle reminder: {affirmation}"))
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.9em; margin-top: 1rem;">
    💙 You are not alone. Help is always available. 💙
</div>
""", unsafe_allow_html=True)

# Voice setup info
if not VOICE_FEATURES_AVAILABLE:
    with st.expander("Enable Voice Features"):
        st.info("""
        To add voice capabilities, install:
        ```bash
        pip install SpeechRecognition gtts pyaudio
        ```
        Then restart the app.
        """)