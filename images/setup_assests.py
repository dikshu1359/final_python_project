#!/usr/bin/env python3
"""
setup_assets.py - Generate background images, logo, and emotion model
Run this script to create all the necessary asset files for the Face Emotion Detection App
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, BatchNormalization
import sqlite3
import json
import bcrypt

def create_directories():
    """Create all necessary directories"""
    directories = [
        'assets/images',
        'assets/models', 
        'data',
        'components',
        'pages',
        'styles'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_background_image():
    """Create a beautiful gradient background image"""
    width, height = 1920, 1080
    
    # Create gradient background
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create gradient from purple to blue
    for y in range(height):
        # Calculate color gradient
        ratio = y / height
        r = int(102 + (118 - 102) * ratio)  # 667eea to 764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add some geometric patterns
    for i in range(50):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(20, 100)
        alpha = np.random.randint(10, 50)
        
        # Create overlay with transparency
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, alpha))
        
        # Blend with main image
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    
    # Save background image
    image.save('assets/images/background.jpg', quality=95)
    print("✅ Created background.jpg")

def create_logo():
    """Create a logo for the app"""
    size = 512
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw main circle (face)
    center = size // 2
    radius = size // 3
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                fill=(255, 215, 0, 255), outline=(255, 140, 0, 255), width=8)
    
    # Draw eyes
    eye_radius = radius // 6
    left_eye_x = center - radius // 2
    right_eye_x = center + radius // 2
    eye_y = center - radius // 3
    
    draw.ellipse([left_eye_x-eye_radius, eye_y-eye_radius, 
                 left_eye_x+eye_radius, eye_y+eye_radius], fill=(0, 0, 0, 255))
    draw.ellipse([right_eye_x-eye_radius, eye_y-eye_radius, 
                 right_eye_x+eye_radius, eye_y+eye_radius], fill=(0, 0, 0, 255))
    
    # Draw smile
    smile_y = center + radius // 4
    smile_width = radius
    draw.arc([center-smile_width//2, smile_y-30, center+smile_width//2, smile_y+30], 
             start=0, end=180, fill=(0, 0, 0, 255), width=8)
    
    image.save('assets/images/logo.png')
    print("✅ Created logo.png")

def create_emotion_model():
    """Create and save the emotion detection model"""
    model = Sequential([
        # First Convolutional Block
        Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
        BatchNormalization(),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        
        # Second Convolutional Block
        Conv2D(64, (3, 3), activation='relu'),
        BatchNormalization(),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        
        # Third Convolutional Block
        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        
        # Fourth Convolutional Block
        Conv2D(256, (3, 3), activation='relu'),
        BatchNormalization(),
        Dropout(0.25),
        
        # Fully Connected Layers
        Flatten(),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(7, activation='softmax')  # 7 emotion classes
    ])
    
    # Compile the model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Build the model with sample input
    model.build((None, 48, 48, 1))
    
    # Save the model
    model.save('assets/models/emotion_model.h5')
    print("✅ Created emotion_model.h5")
    
    # Print model summary
    print("\n📊 Model Summary:")
    model.summary()

def create_database():
    """Create SQLite database with sample data"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create emotion sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_type TEXT NOT NULL,
            emotions_detected TEXT NOT NULL,
            total_faces INTEGER DEFAULT 1,
            session_duration INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            theme TEXT DEFAULT 'dark',
            notifications BOOLEAN DEFAULT 1,
            auto_save BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample user (password: demo123)
    hashed_password = bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password) 
            VALUES (?, ?, ?)
        ''', ('demo_user', 'demo@example.com', hashed_password))
        
        # Insert sample emotion sessions
        cursor.execute('''
            INSERT INTO emotion_sessions (user_id, session_type, emotions_detected) 
            VALUES (?, ?, ?)
        ''', (1, 'real_time', '{"Happy": 45, "Sad": 12, "Angry": 8, "Surprise": 15, "Fear": 5, "Disgust": 3, "Neutral": 35}'))
        
        cursor.execute('''
            INSERT INTO emotion_sessions (user_id, session_type, emotions_detected) 
            VALUES (?, ?, ?)
        ''', (1, 'image_upload', '{"Happy": 38, "Sad": 18, "Angry": 12, "Surprise": 10, "Fear": 8, "Disgust": 4, "Neutral": 42}'))
        
        print("✅ Created users.db with sample data")
        print("   📝 Demo credentials: username='demo_user', password='demo123'")
        
    except sqlite3.IntegrityError:
        print("✅ Database already exists with sample data")
    
    conn.commit()
    conn.close()

def create_emotions_json():
    """Create the emotions_data.json file"""
    emotions_data = {
        "sessions": [
            {
                "id": 1,
                "user_id": 1,
                "date": "2024-07-24",
                "time": "14:30:25",
                "session_type": "real_time",
                "emotions": {
                    "Happy": 45,
                    "Sad": 12,
                    "Angry": 8,
                    "Surprise": 15,
                    "Fear": 5,
                    "Disgust": 3,
                    "Neutral": 35
                },
                "total_faces_detected": 3,
                "session_duration": 120,
                "average_confidence": 0.87
            },
            {
                "id": 2,
                "user_id": 1,
                "date": "2024-07-23",
                "time": "16:45:10",
                "session_type": "image_upload",
                "emotions": {
                    "Happy": 38,
                    "Sad": 18,
                    "Angry": 12,
                    "Surprise": 10,
                    "Fear": 8,
                    "Disgust": 4,
                    "Neutral": 42
                },
                "total_faces_detected": 5,
                "session_duration": 45,
                "average_confidence": 0.92
            }
        ],
        "emotion_analytics": {
            "total_sessions": 2,
            "total_detections": 255,
            "most_detected_emotion": "Happy",
            "least_detected_emotion": "Disgust"
        }
    }
    
    with open('data/emotions_data.json', 'w') as f:
        json.dump(emotions_data, f, indent=2)
    
    print("✅ Created emotions_data.json")

def create_init_files():
    """Create __init__.py files for packages"""
    init_files = [
        'components/__init__.py',
        'pages/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"✅ Created {init_file}")

def main():
    """Main setup function"""
    print("🚀 Setting up Face Emotion Detection App Assets...")
    print("=" * 50)
    
    try:
        create_directories()
        create_background_image()
        create_logo()
        create_emotion_model()
        create_database()
        create_emotions_json()
        create_init_files()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n📁 Files created:")
        print("   • assets/images/background.jpg")
        print("   • assets/images/logo.png")
        print("   • assets/models/emotion_model.h5")
        print("   • data/users.db")
        print("   • data/emotions_data.json")
        print("\n🎯 Next steps:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Run: streamlit run main.py")
        print("   3. Login with: username='demo_user', password='demo123'")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    main()