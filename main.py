import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import os
import sys
import json
import uuid

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.database import init_database
from components.auth import check_authentication, create_user, verify_user
import config

# Page configuration
st.set_page_config(
    page_title="Face Emotion Detection App",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "# Face Emotion Detection App\nBuilt with Streamlit, OpenCV, and Keras"
    }
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0c3fc 50%, #8ec5fc 100%) !important;
        min-height: 100vh;
    }
    
    .auth-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        max-width: 400px;
        margin: 0 auto;
    }
    
    .welcome-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
        font-weight: 600;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
    }
    
    .emotion-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: #3498db;
        color: white;
        border-radius: 20px;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    .stats-card {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    # Initialize database
    init_database()
    # Initialize session state ONCE at the top
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    # Do NOT re-initialize session state here
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='welcome-header'>😊 Face Emotion Detection</h1>", unsafe_allow_html=True)
        
        # Use a truly unique key for the radio widget
        auth_mode = st.radio("Choose an option:", ["Login", "Sign Up"], horizontal=True, key=str(uuid.uuid4()))
        
        form_key = f"auth_form_{uuid.uuid4()}"
        with st.form(form_key):
            username = st.text_input("Username", placeholder="Enter your username", key=f"username_{form_key}")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key=f"password_{form_key}")
            
            if auth_mode == "Sign Up":
                email = st.text_input("Email", placeholder="Enter your email", key=f"email_{form_key}")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key=f"confirm_{form_key}")
            
            submit_button = st.form_submit_button(f"{auth_mode}", use_container_width=True)
            
            if submit_button:
                if auth_mode == "Login":
                    if verify_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                
                else:  # Sign Up
                    if password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    elif create_user(username, password, email):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # App features preview
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: white;'>🚀 Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h3>📷 Real-time Detection</h3>
            <p>Live emotion detection using your webcam</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h3>🖼️ Image Analysis</h3>
            <p>Upload images for emotion analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h3>🤖 AI Chatbot</h3>
            <p>Chat with Gemini AI about emotions</p>
        </div>
        """, unsafe_allow_html=True)

def show_profile_dropdown():
    if 'show_edit_profile' not in st.session_state:
        st.session_state.show_edit_profile = False
    username = st.session_state.get('username', 'User')
    avatar_path = f"assets/images/avatars/{username}.png"
    avatar_url = avatar_path if os.path.exists(avatar_path) else "https://ui-avatars.com/api/?name=" + username + "&background=8ec5fc&color=222&size=128"
    profile_html = f'''
    <div style="position: fixed; top: 1.5rem; right: 2.5rem; z-index: 9999;">
        <div style="background: #fff; color: #222; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 0.7rem 1.5rem; display: flex; align-items: center; gap: 1rem;">
            <img src='{avatar_url}' alt='avatar' style='width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #8ec5fc;'>
            <span style="font-weight: 600;">{username}</span>
            <form action="#" method="post" style="margin:0;display:inline;">
                <button type="submit" name="logout_btn_profile" style="background: linear-gradient(90deg, #8ec5fc 0%, #e0c3fc 100%); color: #222; border: none; border-radius: 15px; padding: 0.3rem 1.2rem; font-weight: 600; cursor: pointer; margin-left: 1rem;">Logout</button>
            </form>
            <form action="#" method="post" style="margin:0;display:inline;">
                <button type="submit" name="edit_profile_btn" style="background: linear-gradient(90deg, #e0c3fc 0%, #8ec5fc 100%); color: #222; border: none; border-radius: 15px; padding: 0.3rem 1.2rem; font-weight: 600; cursor: pointer; margin-left: 0.5rem;">Edit Profile</button>
            </form>
        </div>
    </div>
    '''
    st.markdown(profile_html, unsafe_allow_html=True)
    # Handle logout
    if st.session_state.get('logout_btn_profile'):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    # Handle edit profile
    if st.session_state.get('edit_profile_btn'):
        st.session_state.show_edit_profile = True
    if st.session_state.show_edit_profile:
        st.markdown("""
        <div style='position: fixed; top: 5.5rem; right: 2.5rem; z-index: 9999; background: #fff; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 1.5rem 2rem; min-width: 320px;'>
        <h4 style='margin-bottom:1rem;'>Edit Profile</h4>
        """, unsafe_allow_html=True)
        # Avatar upload
        uploaded_avatar = st.file_uploader("Upload Avatar (PNG, JPG)", type=["png", "jpg", "jpeg"], key="edit_avatar")
        if uploaded_avatar:
            from PIL import Image
            img = Image.open(uploaded_avatar)
            os.makedirs(f"assets/images/avatars", exist_ok=True)
            img.save(avatar_path)
            st.success("Avatar updated!")
        # Editable fields
        new_username = st.text_input("New Username", value=username, key="edit_username")
        new_email = st.text_input("New Email", key="edit_email")
        new_password = st.text_input("New Password", type="password", key="edit_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="edit_confirm_password")
        if st.button("Save Changes", key="save_profile_btn"):
            if new_password and new_password != confirm_password:
                st.error("Passwords do not match!")
            elif new_password and len(new_password) < 6:
                st.error("Password must be at least 6 characters long!")
            else:
                from components.database import get_db_connection, hash_password
                conn = get_db_connection()
                # Check for username change and uniqueness
                if new_username != username:
                    existing = conn.execute('SELECT username FROM users WHERE username = ?', (new_username,)).fetchone()
                    if existing:
                        st.error("Username already exists!")
                        conn.close()
                        return
                    conn.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, username))
                    st.session_state.username = new_username
                if new_email:
                    conn.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, st.session_state.username))
                if new_password:
                    conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hash_password(new_password), st.session_state.username))
                conn.commit()
                conn.close()
                st.success("Profile updated successfully!")
                st.session_state.show_edit_profile = False
        if st.button("Cancel", key="cancel_profile_btn"):
            st.session_state.show_edit_profile = False
        st.markdown("</div>", unsafe_allow_html=True)

def show_main_app():
    show_profile_dropdown()
    # Sidebar
    with st.sidebar:
        st.markdown(f"<h2 style='color: white;'>Welcome, {st.session_state.username}! 👋</h2>", unsafe_allow_html=True)
        if st.button("🔓 Logout", use_container_width=True, key=f"logout_btn_{uuid.uuid4()}"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        st.markdown("---")
        st.markdown("<h3 style='color: white;'>📊 Quick Stats</h3>", unsafe_allow_html=True)
        stats = load_user_stats()
        st.markdown(f"""
        <div class='metric-container'>
            <h4>Images Analyzed: {stats.get('images_analyzed', 0)}</h4>
        </div>
        <div class='metric-container'>
            <h4>Sessions: {stats.get('sessions', 0)}</h4>
        </div>
        <div class='metric-container'>
            <h4>Most Detected: {stats.get('most_emotion', 'Happy')}</h4>
        </div>
        """, unsafe_allow_html=True)
        # In show_main_app or main sidebar, add a link to the Profile page
        st.markdown('---')
        st.page_link('pages/6_👤_Profile.py', label='👤 My Profile', icon='👤')
    st.markdown("<h1 style='text-align: center; color: white;'>😊 Face Emotion Detection Dashboard</h1>", unsafe_allow_html=True)
    selected_tab = st.selectbox("Select a page:", ["Dashboard", "Real-time", "Upload", "Chatbot"], index=0)
    if selected_tab == "Dashboard":
        show_dashboard()
    elif selected_tab == "Real-time":
        show_realtime_detection()
    elif selected_tab == "Upload":
        show_image_upload()
    elif selected_tab == "Chatbot":
        show_chatbot()

def load_user_stats():
    """Load user statistics"""
    try:
        if os.path.exists('data/emotions_data.json'):
            with open('data/emotions_data.json', 'r') as f:
                data = json.load(f)
                user_data = data.get(st.session_state.username, {})
                return user_data
        return {}
    except:
        return {}

def show_dashboard():
    st.markdown("<h2>📊 Emotion Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # Create sample data for demonstration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='stats-card'>
            <h3>😊</h3>
            <h4>Happy</h4>
            <p>45%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stats-card'>
            <h3>😢</h3>
            <h4>Sad</h4>
            <p>15%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='stats-card'>
            <h3>😮</h3>
            <h4>Surprise</h4>
            <p>20%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='stats-card'>
            <h3>😠</h3>
            <h4>Angry</h4>
            <p>10%</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Emotion Trends")
        # Sample chart data
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        emotions_data = {
            'Date': dates,
            'Happy': np.random.randint(10, 50, 30),
            'Sad': np.random.randint(5, 25, 30),
            'Angry': np.random.randint(2, 15, 30),
            'Surprise': np.random.randint(5, 30, 30)
        }
        df = pd.DataFrame(emotions_data)
        st.line_chart(df.set_index('Date'))
    
    with col2:
        st.subheader("🥧 Emotion Distribution")
        # Pie chart data
        emotions = ['Happy', 'Sad', 'Angry', 'Surprise', 'Fear', 'Disgust', 'Neutral']
        values = [45, 15, 10, 20, 5, 3, 2]
        
        pie_data = pd.DataFrame({
            'Emotion': emotions,
            'Percentage': values
        })
        
        import plotly.express as px
        fig = px.pie(pie_data, values='Percentage', names='Emotion', 
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

def show_realtime_detection():
    st.markdown("<h2>📷 Real-time Emotion Detection</h2>", unsafe_allow_html=True)
    
    from components.emotion_detector import EmotionDetector
    
    detector = EmotionDetector()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📹 Live Camera Feed")
        
        # Camera input
        camera_input = st.camera_input("Take a picture for emotion detection")
        
        if camera_input is not None:
            # Process the image
            result = detector.detect_emotion_from_image(camera_input)
            
            if result:
                st.success(f"Detected Emotion: **{result['emotion']}** (Confidence: {result['confidence']:.2f})")
                
                # Show processed image
                st.image(result['processed_image'], caption="Processed Image with Face Detection")
    
    with col2:
        st.markdown("### 📊 Live Stats")
        
        # Emotion indicators
        emotions = ['Happy', 'Sad', 'Angry', 'Surprise', 'Fear', 'Disgust', 'Neutral']
        
        for emotion in emotions:
            # confidence = np.random.random()
            st.progress(0.0, text=f"{emotion}: N/A")

def show_image_upload():
    st.markdown("<h2>🖼️ Image Upload & Analysis</h2>", unsafe_allow_html=True)
    
    from components.emotion_detector import EmotionDetector
    
    detector = EmotionDetector()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image...", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image containing faces for emotion detection"
        )
        
        if uploaded_file is not None:
            # Display original image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            # Process image
            with st.spinner("Analyzing emotions..."):
                result = detector.detect_emotion_from_image(uploaded_file)
            
            if result:
                st.success(f"✅ Analysis Complete!")
                
                # Show results
                st.markdown(f"### Detected Emotion: **{result['emotion']}**")
                st.markdown(f"**Confidence:** {result['confidence']:.2f}")
                
                # Show processed image
                if 'processed_image' in result:
                    st.image(result['processed_image'], caption="Processed Image with Detection")
    
    with col2:
        st.markdown("### 🎯 Detection Results")
        
        if 'result' in locals() and result:
            # Show confidence scores for all emotions
            st.markdown("#### Confidence Scores:")
            
            emotions = ['Happy', 'Sad', 'Angry', 'Surprise', 'Fear', 'Disgust', 'Neutral']
            
            for emotion in emotions:
                # confidence = np.random.random()  # Replace with actual confidence scores
                st.progress(0.0, text=f"{emotion}")
        
        st.markdown("### 📝 Tips")
        st.info("""
        - Use clear, well-lit images
        - Ensure faces are visible
        - Multiple faces will be detected
        - Supported formats: JPG, PNG
        """)

def show_chatbot():
    st.markdown("<h2>🤖 Emotion AI Chatbot</h2>", unsafe_allow_html=True)
    
    from components.chatbot import GeminiChatbot
    
    chatbot = GeminiChatbot()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your emotion AI assistant. Ask me anything about emotions, mental health, or share how you're feeling today! 😊"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Move chat_input to the top level (not inside any container)
    prompt = st.chat_input("Ask me about emotions or how you're feeling...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.get_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with suggested questions
    st.sidebar.markdown("### 💡 Suggested Questions")
    
    suggestions = [
        "How can I improve my mood?",
        "What are the different types of emotions?",
        "Tips for managing stress",
        "How to recognize facial emotions?",
        "What makes people happy?"
    ]
    
    for suggestion in suggestions:
        if st.sidebar.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            response = chatbot.get_response(suggestion)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Add sidebar style for light background and black font
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #f8fafc !important;
    color: #222 !important;
}
[data-testid="stSidebar"] * {
    color: #222 !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# Add a landing page with a beautiful background and Get Started button
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

if not st.session_state.show_login:
    st.markdown("""
    <div style="height: 90vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <h1 style="font-size: 3rem; color: #222; margin-bottom: 1rem;">😊 Face Emotion Detection App</h1>
        <p style="font-size: 1.3rem; color: #444; max-width: 600px; text-align: center; margin-bottom: 2rem;">
            Welcome! This app uses AI to detect emotions from your face in real time. Analyze your mood, get insights, and chat with our AI assistant. Click below to get started!
        </p>
        <button style="background: linear-gradient(90deg, #8ec5fc 0%, #e0c3fc 100%); color: #222; font-size: 1.2rem; padding: 1rem 3rem; border: none; border-radius: 30px; font-weight: bold; box-shadow: 0 4px 20px rgba(0,0,0,0.08); cursor: pointer;" onclick="window.location.reload()" id="getStartedBtn">Get Started</button>
    </div>
    <script>
    const btn = window.parent.document.getElementById('getStartedBtn');
    if (btn) btn.onclick = function() { window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: true}, '*'); };
    </script>
    """, unsafe_allow_html=True)
    if st.button("Get Started", key="get_started_btn", use_container_width=True):
        st.session_state.show_login = True
        st.rerun()
else:
    main()

if __name__ == "__main__":
    main()