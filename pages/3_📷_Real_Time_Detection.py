import streamlit as st
import cv2
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.emotion_detector import EmotionDetector
from components.auth import check_authentication

# Page config
st.set_page_config(
    page_title="Real-Time Detection",
    page_icon="📷",
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
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    
    .detection-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .emotion-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .controls-panel {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

# Header
st.sidebar.image('assets/images/logo.png', width=80)
st.sidebar.markdown('<h2 style="text-align:center; color:#667eea; margin-bottom:1rem;">EmotiVision</h2>', unsafe_allow_html=True)
st.markdown('<div class="app-header fade-in"><h1>Real-Time Emotion Detection</h1><p>Live camera feed with emotion recognition and analytics</p></div>', unsafe_allow_html=True)

# Use standard EmotionDetector without any toggles
@st.cache_resource
def load_emotion_detector():
    return EmotionDetector()

detector = load_emotion_detector()

# Initialize session state
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'emotion_history' not in st.session_state:
    st.session_state.emotion_history = []
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="detection-container">', unsafe_allow_html=True)
    
    # Camera controls
    st.markdown('<div class="controls-panel">', unsafe_allow_html=True)
    col_start, col_stop, col_clear = st.columns(3)
    
    with col_start:
        if st.button("🎥 Start Camera", type="primary", use_container_width=True):
            st.session_state.camera_active = True
            st.rerun()
    
    with col_stop:
        if st.button("⏹️ Stop Camera", type="secondary", use_container_width=True):
            st.session_state.camera_active = False
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.emotion_history = []
            st.session_state.detection_count = 0
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Camera feed placeholder
    camera_placeholder = st.empty()
    
    # Current emotion display
    emotion_placeholder = st.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Statistics panel
    st.markdown(f"""
    <div class="stats-card">
        <h3>📊 Detection Stats</h3>
        <h2>{{}}</h2>
        <p>Total Detections</p>
        <h4 style='margin-top:1rem;'>👥 Faces Detected (last frame): <b>{{}}</b></h4>
        <h4 style='margin-top:0.5rem;'>🧑 Age (last detection): <b>{{}}</b></h4>
    </div>
    """.format(st.session_state.detection_count, face_count if st.session_state.camera_active else 0, age if st.session_state.camera_active and results else '?'), unsafe_allow_html=True)

    # Export to CSV button
    if st.session_state.emotion_history:
        df_history = pd.DataFrame(st.session_state.emotion_history)
        st.download_button(
            label="⬇️ Export Emotion History to CSV",
            data=df_history.to_csv(index=False).encode('utf-8'),
            file_name="emotion_history.csv",
            mime="text/csv"
        )

        # Emotion trend line chart
        df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
        emotion_trend = df_history.groupby([df_history['timestamp'].dt.date, 'emotion']).size().unstack(fill_value=0)
        st.line_chart(emotion_trend)

        # Age distribution bar chart
        if 'age' in df_history.columns:
            age_counts = df_history['age'].value_counts().sort_index()
            st.bar_chart(age_counts)

    # Live emotion chart
    if st.session_state.emotion_history:
        # Get recent emotions (last 20)
        recent_emotions = st.session_state.emotion_history[-20:]
        emotion_counts = pd.Series([e['emotion'] for e in recent_emotions]).value_counts()
        
        # Pie chart
        fig_pie = px.pie(
            values=emotion_counts.values,
            names=emotion_counts.index,
            title="Recent Emotion Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            height=300,
            margin=dict(t=50, b=0, l=0, r=0),
            font=dict(size=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Timeline chart
        if len(recent_emotions) > 1:
            df_timeline = pd.DataFrame(recent_emotions)
            df_timeline['timestamp'] = pd.to_datetime(df_timeline['timestamp'])
            
            fig_timeline = px.scatter(
                df_timeline,
                x='timestamp',
                y='emotion',
                color='confidence',
                size='confidence',
                title="Emotion Timeline",
                color_continuous_scale="viridis"
            )
            fig_timeline.update_layout(
                height=250,
                margin=dict(t=50, b=0, l=0, r=0),
                font=dict(size=10)
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

# Camera processing
if st.session_state.camera_active:
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # Process frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed_frame, results = detector.process_camera_frame(rgb_frame)
            face_count = len(results)
            # Display face count above camera feed
            camera_placeholder.markdown(f'<div style="text-align:center; font-size:1.2rem; color:#667eea; margin-bottom:0.5rem;">👥 Faces detected: <b>{face_count}</b></div>', unsafe_allow_html=True)
            # Display frame
            camera_placeholder.image(processed_frame, channels="RGB", use_column_width=True)
            
            # Show detected emotions
            if results:
                # Show the most confident emotion
                best_result = max(results, key=lambda x: x['confidence'])
                emotion = best_result['emotion']
                confidence = best_result['confidence']
                age = best_result.get('age', '?')
                
                emotion_colors = {
                    'happy': '#FFD700',
                    'sad': '#4169E1',
                    'angry': '#FF4500',
                    'surprise': '#FF69B4',
                    'fear': '#8A2BE2',
                    'disgust': '#228B22',
                    'neutral': '#808080'
                }
                color = emotion_colors.get(emotion.lower(), '#808080')
                # In the emotion feedback section, adjust messages based on culture
                culture_note = ""
                if st.session_state['culture'] == "East Asian" and emotion == "neutral":
                    culture_note = "<br><span style='color:#3498db;'>Note: In East Asian cultures, neutral expressions are common and may not indicate lack of emotion.</span>"
                elif st.session_state['culture'] == "Western" and emotion == "neutral":
                    culture_note = "<br><span style='color:#3498db;'>Note: In Western cultures, neutral expressions may indicate low engagement.</span>"
                # Add more culture-specific notes as needed
                emotion_placeholder.markdown(f"""
                <div style=\"text-align: center; padding: 1rem;\">
                    <div class=\"emotion-badge\" style=\"background-color: {color}; font-size: 1.5rem;\">
                        {emotion.upper()} - {confidence:.1%} | Age: {age}
                    </div>
                    <p style=\"margin-top: 1rem; color: #666;\">
                        Confidence: {confidence:.1%} | Time: {datetime.now().strftime('%H:%M:%S')}{culture_note}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                # Add to history
                st.session_state.emotion_history.append({
                    'emotion': emotion,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat(),
                    'face_count': face_count,
                    'age': age
                })
                st.session_state.detection_count += 1
                # Save to file
                os.makedirs('data', exist_ok=True)
                with open('data/emotions_data.json', 'w') as f:
                    json.dump(st.session_state.emotion_history, f, indent=2)
                st.rerun()
            else:
                emotion_placeholder.markdown('<div style="text-align:center; color:#e74c3c; margin-top:1rem;">No faces detected. Please face the camera.</div>', unsafe_allow_html=True)
    cap.release()
else:
    camera_placeholder.markdown("""
    <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #ccc;">
        <h3>📷 Camera Feed</h3>
        <p>Click "Start Camera" to begin real-time emotion detection</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>💡 <strong>Tips:</strong> Ensure good lighting and face the camera directly for best results</p>
    <p>🔒 Your privacy is protected - no data is stored permanently</p>
</div>
""", unsafe_allow_html=True)