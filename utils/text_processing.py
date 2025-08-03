"""
Text processing utilities for the Mental Health Support app
"""

import random
import re
from config.settings import CASUAL_REPLACEMENTS, FOLLOW_UP_QUESTIONS, CRISIS_KEYWORDS

def make_response_casual(response_text):
    """Make bot responses more casual and concise"""
    
    # Remove overly clinical language
    for formal, casual in CASUAL_REPLACEMENTS.items():
        response_text = response_text.replace(formal, casual)
    
    # Split into sentences and keep only the most relevant ones
    sentences = response_text.split('.')
    
    # Keep first 1-2 sentences if they're substantial
    if len(sentences) > 2:
        # Look for the most conversational/supportive sentences
        casual_sentences = []
        for sentence in sentences[:3]:  # Only check first 3
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short fragments
                casual_sentences.append(sentence)
        
        if casual_sentences:
            response_text = '. '.join(casual_sentences[:2]) + '.'
    
    # Add a casual follow-up question sometimes
    if len(response_text) < 100 and random.random() < 0.4:  # 40% chance for short responses
        response_text += random.choice(FOLLOW_UP_QUESTIONS)
    
    return response_text.strip()

def detect_crisis_keywords(text):
    """Detect if text contains crisis-related keywords"""
    return any(word in text.lower() for word in CRISIS_KEYWORDS)

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

def clean_text_for_display(text):
    """Clean text for better display in chat"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Ensure proper sentence spacing
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    return text.strip()