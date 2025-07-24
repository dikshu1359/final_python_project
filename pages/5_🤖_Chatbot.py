import streamlit as st
import json
import os
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.chatbot import GeminiChatbot
from components.auth import check_authentication

# Page config
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("You must be logged in to access this page. Please go to the Login page.")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b 0%, #feca57 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 20%;
        position: relative;
        word-wrap: break-word;
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #ff6b6b;
        position: relative;
        word-wrap: break-word;
    }
    
    .message-time {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        position: sticky;
        bottom: 0;
        z-index: 100;
    }
    
    .quick-actions {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .action-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .chat-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        background: #f8f9fa;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #ff6b6b;
    }
    
    .typing-dots {
        display: flex;
        gap: 0.2rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff6b6b;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.sidebar.image('assets/images/logo.png', width=80)
st.sidebar.markdown('<h2 style="text-align:center; color:#667eea; margin-bottom:1rem;">EmotiVision</h2>', unsafe_allow_html=True)
st.markdown('<div class="app-header fade-in"><h1>AI Chatbot</h1><p>Get emotional guidance and support from our intelligent chatbot.</p></div>', unsafe_allow_html=True)

# Sidebar: API key input
with st.sidebar:
    st.markdown('---')
    api_key = st.text_input('Gemini API Key', type='password', value='AIzaSyAjwpJQ-wSWX0ipJi0HvX7MWL8AycfmDFg', key='gemini_api_key')
    if not api_key:
        st.warning('Please enter your Gemini API key to use the chatbot.')

# Initialize chatbot with API key as cache key
@st.cache_resource
def load_chatbot(api_key):
    return GeminiChatbot(api_key=api_key)

chatbot = load_chatbot(api_key)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

# Layout
col1, col2 = st.columns([3, 1])

with col1:
    # Chat container
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
    # Welcome message
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="bot-message">
            <div>👋 Hello! I'm your AI companion powered by Gemini 1.5 Flash. I'm here to help you understand emotions, discuss psychology, provide mental wellness tips, and chat about anything related to emotional well-being. How can I assist you today?</div>
            <div class="message-time">🤖 AI Assistant</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <div>{message['content']}</div>
                <div class="message-time">👤 You - {message['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <div>{message['content']}</div>
                <div class="message-time">🤖 AI Assistant - {message['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Chat statistics
    st.markdown(f"""
    <div class="chat-stats">
        <h3>💬 Chat Stats</h3>
        <h2>{st.session_state.message_count}</h2>
        <p>Messages Exchanged</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    quick_prompts = [
        "🧠 Explain different emotions",
        "😊 Tips for managing stress",
        "💡 How to improve mood",
        "🔍 Analyze my recent emotions",
        "📊 Mental wellness strategies",
        "🎯 Set emotional goals"
    ]
    
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True, key=f"quick_{prompt}"):
            # Add user message
            user_message = {
                'role': 'user',
                'content': prompt[2:],  # Remove emoji
                'timestamp': datetime.now().strftime('%H:%M')
            }
            st.session_state.chat_history.append(user_message)
            st.session_state.message_count += 1
            # Get bot response immediately
            with st.spinner("🤖 AI is thinking..."):
                context = f"User's recent emotions: {emotion_context}" if emotion_context else ""
                bot_response = chatbot.get_response(prompt[2:], context)
            bot_message = {
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.now().strftime('%H:%M')
            }
            st.session_state.chat_history.append(bot_message)
            st.session_state.message_count += 1
            # Save chat history
            os.makedirs('data', exist_ok=True)
            with open('data/chat_history.json', 'w') as f:
                json.dump(st.session_state.chat_history, f, indent=2)
            st.rerun()
    
    # Clear chat button
    if st.button("🧹 Clear Chat", type="secondary", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.message_count = 0
        st.rerun()

# Input section
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Emotion context (if available from previous sessions)
emotion_context = ""
if os.path.exists('data/emotions_data.json'):
    try:
        with open('data/emotions_data.json', 'r') as f:
            emotion_data = json.load(f)
            if emotion_data:
                recent_emotions = emotion_data[-5:]  # Last 5 emotions
                emotions_list = [e['emotion'] for e in recent_emotions]
                emotion_context = f"Recent detected emotions: {', '.join(emotions_list)}"
    except:
        pass

if emotion_context:
    st.info(f"💡 Context: {emotion_context}")

# Chat input
col_input, col_send = st.columns([4, 1])
with col_input:
    user_input = st.text_input(
        "Type your message...",
        placeholder="Ask about emotions, mental health, or just chat!",
        key="chat_input"
    )

with col_send:
    send_button = st.button("📤 Send", type="primary", use_container_width=True)

# Process message
if send_button and user_input.strip():
    # Add user message
    user_message = {
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().strftime('%H:%M')
    }
    st.session_state.chat_history.append(user_message)
    # Show typing indicator
    with st.spinner("🤖 AI is thinking..."):
        context = f"User's recent emotions: {emotion_context}" if emotion_context else ""
        bot_response = chatbot.get_response(user_input, context)
    bot_message = {
        'role': 'assistant',
        'content': bot_response,
        'timestamp': datetime.now().strftime('%H:%M')
    }
    st.session_state.chat_history.append(bot_message)
    st.session_state.message_count += 2
    # Save chat history
    os.makedirs('data', exist_ok=True)
    with open('data/chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f, indent=2)
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Features section
st.markdown("---")
st.markdown("""
<div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; border-left: 4px solid #ff6b6b;">
    <h4>🌟 Chatbot Features</h4>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div>
            <h5>🧠 Emotion Understanding</h5>
            <p>Get insights about different emotions and their impacts</p>
        </div>
        <div>
            <h5>💡 Mental Wellness Tips</h5>
            <p>Receive personalized advice for emotional well-being</p>
        </div>
        <div>
            <h5>📊 Context Awareness</h5>
            <p>Considers your recent emotion detection results</p>
        </div>
        <div>
            <h5>🎯 Goal Setting</h5>
            <p>Help set and track emotional wellness goals</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

# Theme toggle
theme = st.sidebar.selectbox("🎨 Theme", ["Dark", "Light"], index=0, key="theme_selector")
st.session_state['theme'] = theme
if theme == "Light":
    st.markdown('<style>:root { --primary-color: #764ba2; --secondary-color: #667eea; --background-color: #f8f9fa; --text-color: #222; }</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>:root { --primary-color: #667eea; --secondary-color: #764ba2; --background-color: #181a1b; --text-color: #fff; }</style>', unsafe_allow_html=True)

# User profile dropdown
with st.sidebar.expander("👤 Profile", expanded=True):
    st.write(f"**User:** {st.session_state.get('username', 'Guest')}")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        show_toast("Logged out successfully!", type="success")

def show_toast(message, type="info"):
    color = {"success": "#2ecc71", "error": "#e74c3c", "info": "#3498db"}.get(type, "#3498db")
    st.markdown(f'<div style="position:fixed;top:2rem;right:2rem;z-index:9999;background:{color};color:white;padding:1rem 2rem;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.2);font-weight:bold;">{message}</div>', unsafe_allow_html=True)