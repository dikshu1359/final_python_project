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
    page_title="Image Upload Detection",
    page_icon="🖼️",
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
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    
    .upload-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 2px dashed #11998e;
    }
    
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .emotion-result {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .confidence-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .confidence-fill {
        background: white;
        height: 20px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .face-detection-box {
        border: 3px solid #11998e;
        border-radius: 10px;
        padding: 1rem;
        background: rgba(17, 153, 142, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

# Header
st.sidebar.image('assets/images/logo.png', width=80)
st.sidebar.markdown('<h2 style="text-align:center; color:#667eea; margin-bottom:1rem;">EmotiVision</h2>', unsafe_allow_html=True)
st.markdown('<div class="app-header fade-in"><h1>Image Upload</h1><p>Upload images for emotion analysis with a beautiful interface.</p></div>', unsafe_allow_html=True)

# Initialize emotion detector
@st.cache_resource
def load_emotion_detector():
    return EmotionDetector()

detector = load_emotion_detector()

# Initialize session state
if 'uploaded_results' not in st.session_state:
    st.session_state.uploaded_results = []

# Main layout
col1, col2 = st.columns([3, 2])

with col1:
    # Upload section
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    st.markdown("### 📁 Upload Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Supported formats: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        # Process image
        with st.spinner("Analyzing emotions..."):
            result = detector.detect_emotion_from_image(uploaded_file)
        if result:
            st.success(f"✅ Analysis Complete!")
            st.image(result['processed_image'], caption="Processed Image with Face Detection", use_column_width=True)
            # Show grid of detected faces with emotions
            all_results = result.get('all_results', [])
            if all_results:
                st.markdown("<h4>Detected Faces & Emotions</h4>", unsafe_allow_html=True)
                face_cols = st.columns(min(3, len(all_results)))
                for idx, face in enumerate(all_results):
                    x, y, w, h = face['bbox']
                    face_crop = image.crop((x, y, x+w, y+h))
                    with face_cols[idx % len(face_cols)]:
                        st.image(face_crop, caption=f"{face['emotion'].upper()} ({face['confidence']*100:.1f}%)", use_column_width=True)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #666;">
            <h3>📤 Drag and drop or click to upload</h3>
            <p>Supported formats: PNG, JPG, JPEG</p>
            <p>Max file size: 200MB</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Results panel
    st.markdown("### 📊 Analysis Results")
    
    if st.session_state.uploaded_results:
        # Latest result
        latest_result = st.session_state.uploaded_results[-1]
        
        # Stats cards
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{len(st.session_state.uploaded_results)}</h3>
                <p>Images Analyzed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            total_faces = sum(r['faces_detected'] for r in st.session_state.uploaded_results)
            st.markdown(f"""
            <div class="stat-card">
                <h3>{total_faces}</h3>
                <p>Total Faces</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.uploaded_results = []
            st.rerun()
    
    else:
        st.info("Upload and analyze an image to see results here.")

# Display detailed results
if st.session_state.uploaded_results:
    st.markdown("---")
    st.markdown("### 📋 Detailed Analysis")
    
    # Show results for the latest upload
    latest_result = st.session_state.uploaded_results[-1]
    
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    
    # File info
    st.markdown(f"""
    **📁 File:** {latest_result['filename']}  
    **🕐 Analyzed:** {datetime.fromisoformat(latest_result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}  
    **👥 Faces Detected:** {latest_result['faces_detected']}
    """)
    
    # Individual face results
    for i, face_result in enumerate(latest_result['emotions']):
        st.markdown(f"#### 👤 Face {i+1}")
        
        col_info, col_chart = st.columns([1, 1])
        
        with col_info:
            emotion = face_result['emotion']
            confidence = face_result['confidence']
            
            # Emotion result display
            st.markdown(f"""
            <div class="emotion-result">
                <h3>😊 {emotion.upper()}</h3>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence*100}%"></div>
                </div>
                <p>Confidence: {confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # All emotion probabilities
            if 'all_emotions' in face_result:
                st.markdown("**All Emotion Probabilities:**")
                for emo, prob in face_result['all_emotions'].items():
                    st.progress(prob, text=f"{emo.capitalize()}: {prob:.1%}")
        
        with col_chart:
            # Emotion probabilities chart
            if 'all_emotions' in face_result:
                emotions_df = pd.DataFrame([
                    {'Emotion': emo.capitalize(), 'Probability': prob}
                    for emo, prob in face_result['all_emotions'].items()
                ])
                
                fig = px.bar(
                    emotions_df,
                    x='Probability',
                    y='Emotion',
                    orientation='h',
                    title=f"Face {i+1} - Emotion Probabilities",
                    color='Probability',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    height=300,
                    margin=dict(t=50, b=0, l=0, r=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Historical analysis
    if len(st.session_state.uploaded_results) > 1:
        st.markdown("### 📈 Historical Analysis")
        
        # Emotion distribution across all uploads
        all_emotions = []
        for result in st.session_state.uploaded_results:
            for face in result['emotions']:
                all_emotions.append(face['emotion'])
        
        if all_emotions:
            emotion_counts = pd.Series(all_emotions).value_counts()
            
            col_pie, col_trend = st.columns(2)
            
            with col_pie:
                fig_pie = px.pie(
                    values=emotion_counts.values,
                    names=emotion_counts.index,
                    title="Overall Emotion Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_trend:
                # Timeline of uploads
                upload_times = [datetime.fromisoformat(r['timestamp']) for r in st.session_state.uploaded_results]
                faces_count = [r['faces_detected'] for r in st.session_state.uploaded_results]
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=upload_times,
                    y=faces_count,
                    mode='lines+markers',
                    name='Faces Detected',
                    line=dict(color='#11998e', width=3),
                    marker=dict(size=8)
                ))
                fig_trend.update_layout(
                    title="Faces Detected Over Time",
                    xaxis_title="Upload Time",
                    yaxis_title="Number of Faces",
                    height=400
                )
                st.plotly_chart(fig_trend, use_container_width=True)

# Tips section
st.markdown("---")
st.markdown("""
<div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; border-left: 4px solid #11998e;">
    <h4>💡 Tips for Better Results</h4>
    <ul>
        <li><strong>Image Quality:</strong> Use high-resolution images with clear faces</li>
        <li><strong>Lighting:</strong> Well-lit faces produce more accurate results</li>
        <li><strong>Face Size:</strong> Faces should be clearly visible and not too small</li>
        <li><strong>Multiple Faces:</strong> The system can detect multiple faces in one image</li>
        <li><strong>Supported Emotions:</strong> Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Theme toggle and user profile
theme = st.sidebar.selectbox("🎨 Theme", ["Dark", "Light"], index=0, key="theme_selector")
st.session_state['theme'] = theme
if theme == "Light":
    st.markdown('<style>:root { --primary-color: #764ba2; --secondary-color: #667eea; --background-color: #f8f9fa; --text-color: #222; }</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>:root { --primary-color: #667eea; --secondary-color: #764ba2; --background-color: #181a1b; --text-color: #fff; }</style>', unsafe_allow_html=True)
def show_toast(message, type="info"):
    color = {"success": "#2ecc71", "error": "#e74c3c", "info": "#3498db"}.get(type, "#3498db")
    st.markdown(f'<div style="position:fixed;top:2rem;right:2rem;z-index:9999;background:{color};color:white;padding:1rem 2rem;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.2);font-weight:bold;">{message}</div>', unsafe_allow_html=True)
# User profile dropdown
with st.sidebar.expander("👤 Profile", expanded=True):
    st.write(f"**User:** {st.session_state.get('username', 'Guest')}")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        show_toast("Logged out successfully!", type="success")