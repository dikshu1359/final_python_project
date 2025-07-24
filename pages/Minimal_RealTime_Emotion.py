import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.emotion_detector import EmotionDetector

st.set_page_config(page_title="Minimal Real-Time Emotion Detection", page_icon="😊", layout="centered")
st.title("Minimal Real-Time Emotion Detection")

@st.cache_resource
def load_emotion_detector():
    return EmotionDetector()

detector = load_emotion_detector()

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

col1, col2 = st.columns(2)
with col1:
    if st.button("Start Camera"):
        st.session_state.camera_active = True
        st.rerun()
with col2:
    if st.button("Stop Camera"):
        st.session_state.camera_active = False
        st.rerun()

camera_placeholder = st.empty()
emotion_placeholder = st.empty()

if st.session_state.camera_active:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed_frame, results = detector.process_camera_frame(rgb_frame)
            camera_placeholder.image(processed_frame, channels="RGB", use_column_width=True)
            if results:
                best_result = max(results, key=lambda x: x['confidence'])
                emotion = best_result['emotion']
                confidence = best_result['confidence']
                emotion_placeholder.success(f"Detected Emotion: {emotion.upper()} (Confidence: {confidence:.1%})")
            else:
                emotion_placeholder.warning("No face detected. Please face the camera.")
    cap.release()
else:
    camera_placeholder.info("Click 'Start Camera' to begin real-time emotion detection.")
    emotion_placeholder.empty() 