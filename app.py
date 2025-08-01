import streamlit as st
from dotenv import load_dotenv
import os
import random
from datetime import datetime
import base64
import io

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
    import pygame
    VOICE_FEATURES_AVAILABLE = True
except ImportError:
    VOICE_FEATURES_AVAILABLE = False
    st.warning("⚠️ Voice features require additional packages. Install with: pip install SpeechRecognition gtts pygame pyaudio")

# Load environment variables
load_dotenv()

# Initialize embedding model
embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Load FAISS vector store
vectorstore = FAISS.load_local(
    "mental_health_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

# Create custom prompt template with Gen Z persona
custom_prompt = PromptTemplate(
    input_variables=["context", "question", "chat_history"],
    template="""You are a mental health first aid assistant with a Gen Z persona. You're knowledgeable, empathetic, and speak in a way that resonates with young people while maintaining professionalism when dealing with serious mental health situations.

Your communication style:
- Use casual, supportive language ("hey", "totally get that", "ngl", "fr", "that's valid")
- Be authentic and relatable without being unprofessional
- Show genuine care and understanding
- Use modern slang appropriately but don't overdo it
- Be direct but kind when discussing serious topics
- Always prioritize safety and proper mental health guidance

IMPORTANT CRISIS PROTOCOLS:
- If someone mentions self-harm, suicide, or immediate danger, immediately provide crisis resources
- Always encourage professional help when appropriate
- Never minimize someone's feelings or experiences
- Provide practical, evidence-based mental health first aid techniques

Use the following context from mental health first aid materials to inform your responses:
{context}

Previous conversation:
{chat_history}

Current question: {question}

Remember: Balance being relatable and supportive with providing accurate mental health information. If this is a crisis situation, prioritize safety and immediate resources while maintaining your caring, Gen Z tone.

Response:"""
)

# Create LLM
llm = OpenAI(
    temperature=0.7,  # Slightly higher for more personality
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# Conversational Retrieval Chain with custom prompt
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),  # Get more context
    memory=memory,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": custom_prompt}
)

# Voice processing functions
def initialize_speech_recognition():
    """Initialize the speech recognition engine"""
    if not VOICE_FEATURES_AVAILABLE:
        return None
    return sr.Recognizer()

def listen_for_speech(recognizer, duration=5):
    """Listen for speech input and convert to text"""
    if not VOICE_FEATURES_AVAILABLE or not recognizer:
        return None
    
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
        st.info("🔄 Processing your speech...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        st.warning("⏰ No speech detected. Please try again.")
        return None
    except sr.UnknownValueError:
        st.warning("🤔 Couldn't understand the audio. Please try speaking clearly.")
        return None
    except sr.RequestError as e:
        st.error(f"❌ Speech recognition service error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        return None

def text_to_speech(text, lang='en'):
    """Convert text to speech and return audio data"""
    if not VOICE_FEATURES_AVAILABLE:
        return None
    
    try:
        # Clean text for TTS (remove markdown and special characters)
        clean_text = clean_text_for_tts(text)
        
        # Create TTS object
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.getvalue()
    except Exception as e:
        st.error(f"❌ Text-to-speech error: {e}")
        return None

def clean_text_for_tts(text):
    """Clean text for better TTS output"""
    import re
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold text
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic text
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code text
    text = re.sub(r'#{1,6}\s', '', text)          # Headers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
    
    # Remove emojis for cleaner speech
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove crisis resources formatting for speech
    text = re.sub(r'🚨.*?Crisis Text Line.*?741741', 'If you need immediate help, please call 988 or text HOME to 741741', text)
    
    return text.strip()

def create_audio_player(audio_data, key):
    """Create an audio player widget"""
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode()
        audio_html = f"""
        <audio controls style="width: 200px; height: 30px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    return None

# Crisis keywords detection function
def detect_crisis_keywords(text):
    crisis_keywords = [
        "suicide", "kill myself", "end it all", "self harm", "cutting", 
        "hurt myself", "don't want to live", "better off dead", 
        "overdose", "jump off", "hanging", "weapon"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in crisis_keywords)

# Crisis resources
CRISIS_RESOURCES = """
🚨 **IMMEDIATE HELP AVAILABLE 24/7:**

**Crisis Text Line:** Text HOME to 741741
**National Suicide Prevention Lifeline:** 988
**Crisis Chat:** suicidepreventionlifeline.org/chat

**If you're in immediate danger, please call 911 or go to your nearest emergency room.**

You matter, and there are people who want to help. These resources have trained counselors available right now. 💙
"""

# Affirmations and welcome messages
DAILY_AFFIRMATIONS = [
    "You are worthy of love and kindness, especially from yourself 💕",
    "Your feelings are valid, and it's okay to not be okay sometimes 🌙",
    "Every small step you take towards healing matters 🌱",
    "You have survived 100% of your difficult days so far - that's pretty amazing ✨",
    "Your story isn't over yet, and you have so much beautiful life ahead of you 🌈",
    "You're stronger than you know, braver than you feel, and more loved than you realize 💪",
    "It's okay to rest, to breathe, and to take things one moment at a time 🌸",
    "You belong here, you matter, and the world is better with you in it 🌍",
    "Your mental health journey is unique to you, and you're doing the best you can 🦋",
    "You are not your struggles - you are a whole person deserving of joy and peace ☀️"
]

GREETING_MESSAGES = [
    "How was your day, Goose? 🪿✨",
    "Hey beautiful soul, how are you feeling today? 💝",
    "What's on your heart today, friend? 🤗",
    "How's your energy feeling right now? 🌟",
    "What's been weighing on your mind lately? 💭",
    "How can I support you today, lovely? 🌺",
    "What would make today feel a little brighter for you? ☀️"
]

def get_time_based_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning! ☀️"
    elif 12 <= hour < 17:
        return "Good afternoon! 🌤️"
    elif 17 <= hour < 21:
        return "Good evening! 🌅"
    else:
        return "Hey night owl! 🌙"

def generate_welcome_message():
    time_greeting = get_time_based_greeting()
    personal_greeting = random.choice(GREETING_MESSAGES)
    affirmation = random.choice(DAILY_AFFIRMATIONS)
    
    return f"""{time_greeting} I'm your mental health first aid buddy, and I'm genuinely glad you're here. 💙

{personal_greeting}

Today's gentle reminder: {affirmation}

I'm here to support you with evidence-based guidance, whether you're helping someone else or need support yourself. We can chat about anything - big feelings, small worries, or just life stuff. What feels right for you today?"""

# Streamlit UI Configuration
st.set_page_config(
    page_title="MHFA Chatbot 💙", 
    page_icon="🤗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS Styling (keeping original styles and adding voice features)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main app background with animated gradient */
        .stApp {
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe, #00f2fe);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Main container styling */
        .main .block-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 2.5rem;
            backdrop-filter: blur(15px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-top: 1rem;
        }
        
        /* Voice input container */
        .voice-input-container {
            background: linear-gradient(135deg, rgba(168, 237, 234, 0.9) 0%, rgba(254, 214, 227, 0.9) 100%);
            border-radius: 20px;
            padding: 20px;
            margin: 15px 0;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        /* Voice button styling */
        .voice-button {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 15px 30px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
            margin: 5px !important;
        }
        
        .voice-button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 35px rgba(255, 107, 107, 0.6) !important;
        }
        
        /* TTS button in chat bubbles */
        .tts-button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 8px 15px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            margin-top: 10px !important;
            margin-left: 10px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3) !important;
        }
        
        .tts-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5) !important;
        }
        
        /* Welcome card styling */
        .welcome-card {
            background: linear-gradient(135deg, rgba(168, 237, 234, 0.8) 0%, rgba(254, 214, 227, 0.8) 100%);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            animation: gentleBob 3s ease-in-out infinite;
        }
        
        @keyframes gentleBob {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        /* Chat bubbles with improved styling */
        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 22px;
            border-radius: 25px 25px 8px 25px;
            margin: 12px 0;
            max-width: 75%;
            float: right;
            clear: both;
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
            font-weight: 500;
            animation: slideInRight 0.4s ease-out;
            position: relative;
        }
        
        .user-bubble::before {
            content: '';
            position: absolute;
            bottom: -8px;
            right: 15px;
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-top: 15px solid #764ba2;
        }
        
        .bot-bubble {
            background: linear-gradient(135deg, rgba(168, 237, 234, 0.9) 0%, rgba(254, 214, 227, 0.9) 100%);
            color: #2d3748;
            padding: 18px 22px;
            border-radius: 25px 25px 25px 8px;
            margin: 12px 0;
            max-width: 85%;
            float: left;
            clear: both;
            box-shadow: 0 6px 25px rgba(168, 237, 234, 0.5);
            line-height: 1.7;
            animation: slideInLeft 0.4s ease-out;
            border: 1px solid rgba(255, 255, 255, 0.4);
            position: relative;
        }
        
        .bot-bubble::before {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 15px;
            width: 0;
            height: 0;
            border-right: 15px solid transparent;
            border-top: 15px solid rgba(168, 237, 234, 0.9);
        }
        
        /* Crisis alert with pulsing effect */
        .crisis-alert {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border: 3px solid #ff6b6b;
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            color: #c53030;
            box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4);
            animation: urgentPulse 2s infinite;
            font-weight: 600;
        }
        
        @keyframes urgentPulse {
            0%, 100% { transform: scale(1); box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4); }
            50% { transform: scale(1.02); box-shadow: 0 12px 40px rgba(255, 107, 107, 0.6); }
        }
        
        /* Enhanced source styling */
        .source-list {
            font-size: 0.9rem;
            margin-top: 10px;
            color: #4a5568;
            background: rgba(255, 255, 255, 0.8);
            padding: 12px 16px;
            border-radius: 15px;
            border-left: 5px solid #9f7aea;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        /* Chat container improvements */
        .chat-container {
            max-height: 650px;
            overflow-y: auto;
            padding: 20px 5px;
            scrollbar-width: thin;
            scrollbar-color: #a8edea transparent;
        }
        
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #a8edea, #fed6e3);
            border-radius: 10px;
        }
        
        /* Sidebar enhancements */
        .css-1d391kg {
            background: linear-gradient(180deg, rgba(168, 237, 234, 0.9) 0%, rgba(254, 214, 227, 0.9) 100%);
            backdrop-filter: blur(10px);
        }
        
        /* Input styling */
        .stChatInput > div > div > textarea {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid #a8edea !important;
            border-radius: 25px !important;
            color: #2d3748 !important;
            font-size: 16px !important;
            padding: 15px 20px !important;
            box-shadow: 0 5px 20px rgba(168, 237, 234, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stChatInput > div > div > textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Button styling improvements */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 12px 25px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* Enhanced animations */
        @keyframes slideInRight {
            from { 
                transform: translateX(100%) rotate(5deg); 
                opacity: 0; 
            }
            to { 
                transform: translateX(0) rotate(0deg); 
                opacity: 1; 
            }
        }
        
        @keyframes slideInLeft {
            from { 
                transform: translateX(-100%) rotate(-5deg); 
                opacity: 0; 
            }
            to { 
                transform: translateX(0) rotate(0deg); 
                opacity: 1; 
            }
        }
        
        /* Microphone animation */
        @keyframes micPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .mic-active {
            animation: micPulse 1s ease-in-out infinite;
        }
        
        /* Title with rainbow text effect */
        h1 {
            background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            font-weight: 700;
            font-size: 3rem !important;
            animation: rainbowShift 3s ease infinite;
            margin-bottom: 0.5rem !important;
        }
        
        @keyframes rainbowShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        /* Subtitle styling */
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #6b46c1;
            font-weight: 500;
            margin-bottom: 2rem;
            animation: gentleFade 2s ease-in;
        }
        
        @keyframes gentleFade {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Audio player styling */
        audio {
            margin-top: 10px;
            border-radius: 20px;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1.5rem;
                margin: 0.5rem;
            }
            
            .user-bubble, .bot-bubble {
                max-width: 90%;
                font-size: 14px;
            }
            
            h1 {
                font-size: 2rem !important;
            }
            
            .voice-input-container {
                padding: 15px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Add personalized welcome message
    welcome_msg = generate_welcome_message()
    st.session_state.chat_history.append(("Bot", welcome_msg, []))

if "recognizer" not in st.session_state and VOICE_FEATURES_AVAILABLE:
    st.session_state.recognizer = initialize_speech_recognition()

# Title and subtitle
st.title("🌈 Mental Health First Aid Chat")
st.markdown("<p class='subtitle'>Your compassionate companion for mental wellness support ✨💙</p>", unsafe_allow_html=True)

# Voice input section
if VOICE_FEATURES_AVAILABLE:
    st.markdown("""
    <div class='voice-input-container'>
        <h4 style='margin-bottom: 15px; color: #2d3748;'>🎤 Voice Input Available</h4>
        <p style='margin-bottom: 15px; color: #4a5568;'>Click the button below to speak instead of typing!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_voice1, col_voice2, col_voice3 = st.columns([1, 2, 1])
    with col_voice2:
        if st.button("🎤 Start Voice Input", key="voice_input_btn", help="Click and speak your message"):
            if st.session_state.recognizer:
                with st.spinner("🎤 Listening for your voice..."):
                    speech_text = listen_for_speech(st.session_state.recognizer)
                    if speech_text:
                        st.success(f"📝 Heard: '{speech_text}'")
                        st.session_state.voice_input = speech_text
                        # Process the voice input immediately
                        user_input = speech_text
                        
                        try:
                            # Check for crisis keywords
                            is_crisis = detect_crisis_keywords(user_input)
                            
                            # Get response from chain
                            response = qa_chain.invoke({"question": user_input})
                            answer = response["answer"]
                            sources = response.get("source_documents", [])
                            
                            # Add to chat history
                            st.session_state.chat_history.append(("You", user_input))
                            
                            # If crisis detected, prepend crisis resources
                            if is_crisis:
                                crisis_response = f"Hey, I can see you might be going through something really tough right now. First things first - you're not alone in this. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
                                st.session_state.chat_history.append(("Bot", crisis_response, sources))
                            else:
                                st.session_state.chat_history.append(("Bot", answer, sources))
                                
                            st.rerun()

                        except Exception as e:
                            st.error(f"Oops, something went wrong: {e}")
else:
    st.info("💡 Install voice packages (SpeechRecognition, gtts, pygame, pyaudio) to enable voice features!")

# Enhanced sidebar with more resources
with st.sidebar:
    st.markdown("### 🆘 Crisis Resources")
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.8); padding: 15px; border-radius: 15px; margin: 10px 0;">
    <strong>24/7 Support:</strong><br>
    🔴 <strong>988</strong> - Suicide & Crisis Lifeline<br>
    💬 <strong>Text HOME to 741741</strong> - Crisis Text Line<br>
    🚨 <strong>911</strong> - Emergency Services<br><br>
    
    <strong>Online Support:</strong><br>
    💻 <a href="https://suicidepreventionlifeline.org/chat" target="_blank">Crisis Chat</a><br>
    🤝 <a href="https://www.samhsa.gov/find-help/national-helpline" target="_blank">SAMHSA Helpline</a>
    </div>
    """, unsafe_allow_html=True)
    
    if VOICE_FEATURES_AVAILABLE:
        st.markdown("### 🔊 Voice Features")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.8); padding: 15px; border-radius: 15px; margin: 10px 0;">
        ✅ <strong>Voice Input:</strong> Available<br>
        ✅ <strong>Text-to-Speech:</strong> Available<br><br>
        <small>Look for 🔊 buttons next to bot responses to hear them spoken aloud!</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🌱 Daily Wellness")
    daily_tip = random.choice([
        "Take 3 deep breaths right now 🌬️",
        "Name 3 things you're grateful for today 🙏",
        "Stretch your arms above your head 🙆‍♀️",
        "Drink a glass of water 💧",
        "Step outside for 2 minutes 🌞",
        "Send someone a kind message 💌",
        "Listen to your favorite song 🎵"
    ])
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                padding: 15px; border-radius: 15px; margin: 10px 0; 
                text-align: center; font-weight: 500;">
    <strong>Mindful Moment:</strong><br>
    {daily_tip}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💜 Gentle Reminders")
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.7); padding: 15px; border-radius: 15px;">
    • You are enough, just as you are 💫<br>
    • Healing isn't linear 🌿<br>
    • Your feelings are valid 🤗<br>
    • Small steps count too 👣<br>
    • You're not alone in this 🫂<br>
    • Tomorrow is a new day 🌅
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.9em; color: #666; text-align: center; font-style: italic;">
    💙 This bot provides support and guidance, but isn't a replacement for professional help when needed.
    </div>
    """, unsafe_allow_html=True)

# Display welcome card if it's the first message
if len(st.session_state.chat_history) == 1:
    bot_message = st.session_state.chat_history[0][1]
    st.markdown(f"""
    <div class='welcome-card'>
        <div style="text-align: center; font-size: 1.1em; line-height: 1.6;">
            {bot_message.replace('\n', '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Share what's on your mind... 💭✨")

if user_input:
    try:
        # Check for crisis keywords
        is_crisis = detect_crisis_keywords(user_input)
        
        # Get response from chain
        response = qa_chain.invoke({"question": user_input})
        answer = response["answer"]
        sources = response.get("source_documents", [])
        
        # Add to chat history
        st.session_state.chat_history.append(("You", user_input))
        
        # If crisis detected, prepend crisis resources
        if is_crisis:
            crisis_response = f"Hey, I can see you might be going through something really tough right now. First things first - you're not alone in this. 💙\n\n{CRISIS_RESOURCES}\n\n{answer}"
            st.session_state.chat_history.append(("Bot", crisis_response, sources))
        else:
            st.session_state.chat_history.append(("Bot", answer, sources))

    except Exception as e:
        st.error(f"Oops, something went wrong: {e}")

# Display chat with enhanced bubbles and TTS
if len(st.session_state.chat_history) > 1:  # Skip the welcome message display here
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for i, entry in enumerate(st.session_state.chat_history[1:], 1):  # Skip first welcome message
        role = entry[0]
        if role == "You":
            message = entry[1]
            st.markdown(f"<div class='user-bubble'>{message}</div>", unsafe_allow_html=True)
        else:
            bot_message, source_docs = entry[1], entry[2]
            
            # Check if this is a crisis response
            if "🚨 **IMMEDIATE HELP AVAILABLE" in bot_message:
                st.markdown(f"<div class='crisis-alert'>{bot_message.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-bubble'>{bot_message.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            # Add TTS button for bot responses
            if VOICE_FEATURES_AVAILABLE:
                col_tts1, col_tts2, col_tts3 = st.columns([0.15, 0.7, 0.15])
                with col_tts1:
                    if st.button("🔊", key=f"tts_{i}", help="Click to hear this response"):
                        with st.spinner("🎵 Converting to speech..."):
                            audio_data = text_to_speech(bot_message)
                            if audio_data:
                                audio_html = create_audio_player(audio_data, f"audio_{i}")
                                if audio_html:
                                    st.markdown(audio_html, unsafe_allow_html=True)
                                    st.success("🎵 Audio ready! Click play above.")
                            else:
                                st.error("❌ Could not generate audio")

            # Show sources in collapsible section
            if source_docs:
                with st.expander("📚 Sources from MHFA materials", expanded=False):
                    for j, doc in enumerate(source_docs):
                        page = doc.metadata.get("page", "Unknown")
                        content_preview = doc.page_content[:300].replace('\n', ' ')
                        st.markdown(f"<div class='source-list'><strong>Source {j+1} - Page {page + 1}:</strong><br>{content_preview}...</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Enhanced action buttons
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("🔄 Fresh Start"):
        st.session_state.chat_history = []
        welcome_msg = generate_welcome_message()
        st.session_state.chat_history.append(("Bot", welcome_msg, []))
        st.rerun()

with col2:
    if st.button("💝 New Affirmation"):
        affirmation = random.choice(DAILY_AFFIRMATIONS)
        affirmation_msg = f"Here's a gentle reminder for you: {affirmation}"
        st.session_state.chat_history.append(("Bot", affirmation_msg, []))
        st.rerun()

with col3:
    if st.button("🌟 Wellness Check"):
        wellness_msg = f"Hey! Just wanted to check in with you. {random.choice(GREETING_MESSAGES)} Remember, I'm here whenever you need support. 💙"
        st.session_state.chat_history.append(("Bot", wellness_msg, []))
        st.rerun()

with col4:
    if VOICE_FEATURES_AVAILABLE and st.button("🎤 Quick Voice"):
        if st.session_state.recognizer:
            speech_text = listen_for_speech(st.session_state.recognizer, duration=3)
            if speech_text:
                st.session_state.quick_voice = speech_text
                st.success(f"Quick voice captured: '{speech_text}'")

# Footer with additional support info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;">
    <p>💙 Remember: You are worthy of support, healing, and happiness 💙</p>
    <p><em>If you're in crisis, please reach out to the resources in the sidebar or call 988</em></p>
</div>
""", unsafe_allow_html=True)

# Installation instructions for voice features
if not VOICE_FEATURES_AVAILABLE:
    st.markdown("---")
    st.info("""
    ### 🎤 Enable Voice Features
    
    To add voice input and text-to-speech capabilities, install these packages:
    
    ```bash
    pip install SpeechRecognition gtts pygame pyaudio
    ```
    
    **Note:** On some systems, you may need additional setup:
    - **Windows:** Install PyAudio from wheel: `pip install PyAudio`
    - **macOS:** Install portaudio first: `brew install portaudio`
    - **Linux:** Install system dependencies: `sudo apt-get install python3-pyaudio portaudio19-dev`
    
    After installation, restart the app to enable voice features! 🎉
    """)