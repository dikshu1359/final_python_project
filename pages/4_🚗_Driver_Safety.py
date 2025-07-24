import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.emotion_detector import EmotionDetector

st.set_page_config(page_title="Driver Safety Monitoring", page_icon="🚗", layout="wide")
st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)
st.sidebar.image('assets/images/logo.png', width=80)
st.sidebar.markdown('<h2 style="text-align:center; color:#667eea; margin-bottom:1rem;">EmotiVision</h2>', unsafe_allow_html=True)
st.markdown('<div class="app-header fade-in"><h1>Driver Safety Monitoring</h1><p>Monitor fatigue, distraction, and stress in real time for safer driving.</p></div>', unsafe_allow_html=True)

@st.cache_resource
def load_emotion_detector():
    return EmotionDetector()

detector = load_emotion_detector()

if 'driver_events' not in st.session_state:
    st.session_state.driver_events = []

st.markdown('<div class="detection-container glass-card">', unsafe_allow_html=True)
st.write("### Live Driver Monitoring")

camera_placeholder = st.empty()
alert_placeholder = st.empty()

# Haar cascades for eyes and mouth
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml') if os.path.exists(cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml') else None

fatigue_counter = 0
distraction_counter = 0
FATIGUE_THRESHOLD = 15  # frames
DISTRACTION_THRESHOLD = 15  # frames

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces, gray = detector.detect_faces(rgb_frame)
        state = "Normal"
        alert = ""
        if len(faces) == 0:
            distraction_counter += 1
            if distraction_counter > DISTRACTION_THRESHOLD:
                state = "Distraction"
                alert = "⚠️ Driver not detected! Please face the camera."
        else:
            distraction_counter = 0
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                # Age detection (use color face for DNN)
                color_face = frame[y:y+h, x:x+w] if len(frame.shape) == 3 else cv2.cvtColor(gray[y:y+h, x:x+w], cv2.COLOR_GRAY2BGR)
                if detector.age_model_available:
                    age, age_conf = detector.predict_age(color_face)
                else:
                    age, age_conf = "?", 0.0
                eyes = eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5) if eye_cascade is not None else []
                mouth = mouth_cascade.detectMultiScale(face_roi, scaleFactor=1.5, minNeighbors=11) if mouth_cascade is not None else []
                if len(eyes) < 1:
                    fatigue_counter += 1
                    if fatigue_counter > FATIGUE_THRESHOLD:
                        state = "Fatigue"
                        alert = "😴 Fatigue detected! Please take a break."
                else:
                    fatigue_counter = 0
                # Emotion/stress detection
                emotion, conf = detector.predict_emotion(face_roi)
                if emotion in ["angry", "fear", "sad"] and conf > 0.5:
                    state = "Stress"
                    alert = f"😟 Stress detected: {emotion.title()}"
                # Draw face box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                label = f"{emotion} ({conf:.1%}) | Age: {age}"
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # Show alert
        if alert:
            alert_placeholder.markdown(f'<div style="color:#e74c3c; font-size:1.2rem; text-align:center;">{alert}</div>', unsafe_allow_html=True)
            st.session_state.driver_events.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state": state,
                "alert": alert,
                "age": age if 'age' in locals() else "?"
            })
        else:
            alert_placeholder.markdown("")
        # Show camera
        camera_placeholder.image(frame, channels="BGR", use_column_width=True)
    cap.release()
else:
    camera_placeholder.markdown("<div style='text-align:center; color:#e74c3c;'>Camera not available.</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Event log
events_df = None
if st.session_state.driver_events:
    events_df = st.session_state.driver_events[-50:]
    st.markdown("### Recent Safety Events")
    st.dataframe(events_df)

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