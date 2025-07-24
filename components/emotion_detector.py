# components/emotion_detector.py - Emotion detection using OpenCV and Keras

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import streamlit as st
from PIL import Image
import io
import os
from datetime import datetime
from config import EMOTIONS, MODEL_PATH, IMG_SIZE
import urllib.request
import subprocess
import tempfile

AGE_PROTO_URL = "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/age_deploy.prototxt"
AGE_MODEL_URL = "https://github.com/spmallick/learnopencv/raw/master/AgeGender/age_net.caffemodel"
# Manual download links for age model files:
# age_deploy.prototxt: https://github.com/spmallick/learnopencv/raw/master/AgeGender/age_deploy.prototxt
# age_net.caffemodel: https://github.com/spmallick/learnopencv/raw/master/AgeGender/age_net.caffemodel

AGE_PROTO_PATH = "assets/models/age_deploy.prototxt"
AGE_MODEL_PATH = "assets/models/age_net.caffemodel"
AGE_BUCKETS = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

# Use FER2013 standard emotion order
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
MODEL_PATH = 'models/emotion_model.h5'  # Path to your pretrained model
# Download a real pretrained model from:
# https://github.com/oarriaga/face_classification/releases/download/v0.1/fer2013_mini_XCEPTION.102-0.66.hdf5
# Rename to emotion_model.h5 and place in models/

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detector"""
        self.emotions = EMOTIONS
        self.model = None
        self.face_cascade = None
        self.load_face_cascade()
        self.setup_model()
        self.age_net = None
        self.age_model_available = False
        self.load_age_model()

    def load_face_cascade(self):
        """Load Haar cascade for face detection"""
        try:
            # Try to load from OpenCV data
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Test if cascade is loaded properly
            if self.face_cascade.empty():
                raise Exception("Could not load face cascade")
                
        except Exception as e:
            st.error(f"Error loading face cascade: {e}")
            # Create a dummy cascade for demo purposes
            self.face_cascade = None
    
    def create_model(self):
        """Create CNN model for emotion detection"""
        model = keras.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2, 2),
            layers.Dropout(0.25),
            
            # Second Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2, 2),
            layers.Dropout(0.25),
            
            # Third Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2, 2),
            layers.Dropout(0.25),
            
            # Dense Layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.emotions), activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def setup_model(self):
        """Setup or load the emotion detection model"""
        try:
            # Try to load existing model
            if os.path.exists(MODEL_PATH):
                self.model = keras.models.load_model(MODEL_PATH)
                st.success("Pre-trained emotion model loaded successfully!")
            else:
                st.error(f"No pre-trained model found at {MODEL_PATH}. Please download a real model and place it there. See code comments for link.")
                raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        except Exception as e:
            st.error(f"Model loading failed: {e}. Please ensure you have a real pre-trained model.")
            raise
    
    def train_sample_model(self):
        """Train model with sample data for demonstration"""
        try:
            st.info("Training model with sample data...")
            
            # Generate sample training data
            X_train = np.random.rand(500, 48, 48, 1)
            y_train = np.random.randint(0, len(self.emotions), 500)
            
            # Train for a few epochs
            with st.spinner("Training in progress..."):
                self.model.fit(
                    X_train, y_train,
                    epochs=5,
                    batch_size=32,
                    verbose=0
                )
            
            # Save the model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            self.model.save(MODEL_PATH)
            st.success("Model trained and saved successfully!")
            
        except Exception as e:
            st.error(f"Training failed: {e}")
    
    def preprocess_image(self, image):
        """Preprocess image for emotion detection"""
        try:
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                if image.shape[2] == 4:  # RGBA
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
                else:  # RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Resize to model input size
            resized = cv2.resize(image, IMG_SIZE)
            
            # Normalize pixel values
            normalized = resized.astype(np.float32) / 255.0
            
            # Reshape for model input
            return normalized.reshape(1, 48, 48, 1)
            
        except Exception as e:
            st.error(f"Image preprocessing failed: {e}")
            return None
    
    def detect_faces(self, image):
        """Detect faces in image"""
        try:
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # Convert to grayscale for face detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Detect faces
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                return faces, gray
            else:
                # For demo purposes, return a dummy face region
                h, w = gray.shape[:2]
                return [(w//4, h//4, w//2, h//2)], gray
                
        except Exception as e:
            st.error(f"Face detection failed: {e}")
            return [], None
    
    def predict_emotion(self, face_image):
        """Predict emotion from face image"""
        try:
            if self.model is None:
                return None, 0.0
            
            # Preprocess the face image
            processed_image = self.preprocess_image(face_image)
            
            if processed_image is None:
                return None, 0.0
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Get the emotion with highest confidence
            emotion_index = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_index])
            emotion = self.emotions[emotion_index]
            
            return emotion, confidence
            
        except Exception as e:
            st.error(f"Emotion prediction failed: {e}")
            return None, 0.0
    
    def detect_emotion_from_image(self, uploaded_file):
        """Main function to detect emotion from uploaded image"""
        try:
            # Load image
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Detect faces
            faces, gray = self.detect_faces(image)
            
            if len(faces) == 0:
                st.warning("No faces detected in the image!")
                return None
            
            results = []
            processed_image = image_array.copy()
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face region
                face_image = gray[y:y+h, x:x+w]
                
                # Predict emotion
                emotion, confidence = self.predict_emotion(face_image)
                
                if emotion:
                    results.append({
                        'emotion': emotion,
                        'confidence': confidence,
                        'bbox': (x, y, w, h),
                        'features': [] # No AU features
                    })
                    
                    # Draw rectangle and label on image
                    cv2.rectangle(processed_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Add emotion label
                    label = f"{emotion}: {confidence:.2f}"
                    cv2.putText(processed_image, label, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if results:
                # Return the first (or most confident) result
                best_result = max(results, key=lambda x: x['confidence'])
                
                return {
                    'emotion': best_result['emotion'],
                    'confidence': best_result['confidence'],
                    'all_results': results,
                    'processed_image': processed_image,
                    'faces_count': len(faces)
                }
            
            return None
            
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return None
    
    def get_emotion_probabilities(self, face_image):
        """Get probabilities for all emotions"""
        try:
            if self.model is None:
                return {}
            
            processed_image = self.preprocess_image(face_image)
            
            if processed_image is None:
                return {}
            
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Create emotion probability dictionary
            emotion_probs = {}
            for i, emotion in enumerate(self.emotions):
                emotion_probs[emotion] = float(predictions[0][i])
            
            return emotion_probs
            
        except Exception as e:
            st.error(f"Error getting emotion probabilities: {e}")
            return {}
    
    def download_file(self, url, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(url, path)

    def load_age_model(self):
        if not (os.path.exists(AGE_PROTO_PATH) and os.path.exists(AGE_MODEL_PATH)):
            st.warning("Age model files not found! Age recognition will be skipped. Emotion detection will still work.")
            self.age_model_available = False
            return
        self.age_net = cv2.dnn.readNetFromCaffe(AGE_PROTO_PATH, AGE_MODEL_PATH)
        self.age_model_available = True

    def predict_age(self, face_image):
        if not self.age_model_available:
            return "?", 0.0
        try:
            blob = cv2.dnn.blobFromImage(face_image, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
            self.age_net.setInput(blob)
            preds = self.age_net.forward()
            age = AGE_BUCKETS[preds[0].argmax()]
            confidence = preds[0].max()
            return age, confidence
        except Exception as e:
            return "?", 0.0

    def process_camera_frame(self, frame):
        """Process a single camera frame for real-time detection"""
        try:
            # Detect faces
            faces, gray = self.detect_faces(frame)
            
            results = []
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_image = gray[y:y+h, x:x+w]
                
                # Predict emotion
                emotion, confidence = self.predict_emotion(face_image)
                
                # Age prediction (use color face for DNN)
                if self.age_model_available:
                    color_face = frame[y:y+h, x:x+w] if len(frame.shape) == 3 else cv2.cvtColor(gray[y:y+h, x:x+w], cv2.COLOR_GRAY2BGR)
                    age, age_conf = self.predict_age(color_face)
                else:
                    age, age_conf = "?", 0.0
                
                if emotion:
                    results.append({
                        'emotion': emotion,
                        'confidence': confidence,
                        'bbox': (x, y, w, h),
                        'age': age,
                        'age_confidence': age_conf,
                        'features': [] # No AU features
                    })
                    
                    # Draw rectangle and label
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Add emotion label
                    label = f"{emotion}: {confidence:.2f} | Age: {age}"
                    cv2.putText(frame, label, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return frame, results
            
        except Exception as e:
            st.error(f"Error processing camera frame: {e}")
            return frame, []
    
    def save_detection_result(self, username, emotion, confidence, image_path=None):
        """Save detection result to database"""
        try:
            from components.database import log_emotion
            log_emotion(username, emotion, confidence, image_path)
        except Exception as e:
            st.error(f"Error saving result: {e}")
    
    def get_model_info(self):
        """Get information about the current model"""
        if self.model is None:
            return {"status": "No model loaded"}
        
        try:
            return {
                "status": "Model loaded",
                "input_shape": self.model.input_shape,
                "output_shape": self.model.output_shape,
                "parameters": self.model.count_params(),
                "emotions": self.emotions
            }
        except:
            return {"status": "Model information unavailable"}

# Utility functions for emotion detection
def create_emotion_chart(emotion_probs):
    """Create a chart showing emotion probabilities"""
    import plotly.graph_objects as go
    
    emotions = list(emotion_probs.keys())
    probabilities = list(emotion_probs.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=emotions,
            y=probabilities,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        )
    ])
    
    fig.update_layout(
        title="Emotion Detection Probabilities",
        xaxis_title="Emotions",
        yaxis_title="Probability",
        showlegend=False,
        height=400
    )
    
    return fig

def create_emotion_pie_chart(emotion_probs):
    """Create a pie chart showing emotion distribution"""
    import plotly.express as px
    import pandas as pd
    
    df = pd.DataFrame({
        'Emotion': list(emotion_probs.keys()),
        'Probability': list(emotion_probs.values())
    })
    
    fig = px.pie(df, values='Probability', names='Emotion', 
                 title="Emotion Distribution",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    return fig