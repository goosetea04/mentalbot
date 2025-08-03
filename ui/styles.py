"""
Custom CSS styles for the Mental Health Support app
"""

import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
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

def get_message_style(role, message_type="normal"):
    """Get CSS class for message styling"""
    if role == "user":
        return "user-message"
    elif message_type == "crisis":
        return "crisis-alert"
    else:
        return "bot-message"

def apply_loading_styles():
    """Apply loading animation styles specifically"""
    st.markdown("""
    <style>
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)