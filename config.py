# config.py - Configuration settings for the Face Emotion Detection App

import os

# Gemini AI Configuration
GEMINI_API_KEY = "AIzaSyD8YsGR1zzgNaTiu65ziFzB97YNt8DIh4M"
GEMINI_MODEL = "gemini-1.5-flash"

# Database Configuration
DATABASE_PATH = "data/users.db"
EMOTIONS_DATA_PATH = "data/emotions_data.json"

# Emotion Detection Configuration
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
MODEL_PATH = "assets/models/emotion_model.h5"
CASCADE_PATH = "assets/models/haarcascade_frontalface_default.xml"

# Image Processing Configuration
IMG_SIZE = (48, 48)
IMG_CHANNELS = 1  # Grayscale

# App Configuration
APP_TITLE = "Face Emotion Detection App"
APP_ICON = "😊"
MAX_UPLOAD_SIZE = 10  # MB

# UI Configuration
THEME_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db'
}

# Security Configuration
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Directory Paths
ASSETS_DIR = "assets"
COMPONENTS_DIR = "components"
PAGES_DIR = "pages"
DATA_DIR = "data"
STYLES_DIR = "styles"

# Create directories if they don't exist
DIRECTORIES = [ASSETS_DIR, f"{ASSETS_DIR}/images", f"{ASSETS_DIR}/models", 
               COMPONENTS_DIR, PAGES_DIR, DATA_DIR, STYLES_DIR]

for directory in DIRECTORIES:
    if not os.path.exists(directory):
        os.makedirs(directory)
        
print("Configuration loaded successfully!")