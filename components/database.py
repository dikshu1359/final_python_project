# components/database.py - Database management for user authentication and data storage

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from config import DATABASE_PATH, EMOTIONS_DATA_PATH

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create emotions_log table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emotions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            emotion TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    # Create sessions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            emotions_detected INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize emotions data file
    if not os.path.exists(EMOTIONS_DATA_PATH):
        with open(EMOTIONS_DATA_PATH, 'w') as f:
            json.dump({}, f)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email=None):
    """Create a new user"""
    try:
        conn = get_db_connection()
        password_hash = hash_password(password)
        
        conn.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, password_hash, email)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    password_hash = hash_password(password)
    
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, password_hash)
    ).fetchone()
    
    if user:
        # Update last login
        conn.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?',
            (username,)
        )
        conn.commit()
    
    conn.close()
    return user is not None

def log_emotion(username, emotion, confidence, image_path=None):
    """Log detected emotion to database"""
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO emotions_log (username, emotion, confidence, image_path) VALUES (?, ?, ?, ?)',
        (username, emotion, confidence, image_path)
    )
    conn.commit()
    conn.close()
    
    # Also update JSON data
    update_emotions_json(username, emotion, confidence)

def update_emotions_json(username, emotion, confidence):
    """Update emotions data in JSON file"""
    try:
        with open(EMOTIONS_DATA_PATH, 'r') as f:
            data = json.load(f)
    except:
        data = {}
    
    if username not in data:
        data[username] = {
            'emotions': {},
            'total_detections': 0,
            'sessions': 0,
            'last_activity': None
        }
    
    # Update emotion count
    if emotion not in data[username]['emotions']:
        data[username]['emotions'][emotion] = 0
    
    data[username]['emotions'][emotion] += 1
    data[username]['total_detections'] += 1
    data[username]['last_activity'] = datetime.now().isoformat()
    
    # Find most common emotion
    if data[username]['emotions']:
        most_emotion = max(data[username]['emotions'], key=data[username]['emotions'].get)
        data[username]['most_emotion'] = most_emotion
    
    with open(EMOTIONS_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_stats(username):
    """Get user statistics"""
    conn = get_db_connection()
    
    # Get emotion counts
    emotions = conn.execute(
        'SELECT emotion, COUNT(*) as count FROM emotions_log WHERE username = ? GROUP BY emotion',
        (username,)
    ).fetchall()
    
    # Get total detections
    total = conn.execute(
        'SELECT COUNT(*) as total FROM emotions_log WHERE username = ?',
        (username,)
    ).fetchone()
    
    # Get session count
    sessions = conn.execute(
        'SELECT COUNT(*) as sessions FROM sessions WHERE username = ?',
        (username,)
    ).fetchone()
    
    conn.close()
    
    stats = {
        'emotions': {row['emotion']: row['count'] for row in emotions},
        'total_detections': total['total'] if total else 0,
        'sessions': sessions['sessions'] if sessions else 0
    }
    
    if stats['emotions']:
        stats['most_emotion'] = max(stats['emotions'], key=stats['emotions'].get)
    else:
        stats['most_emotion'] = 'None'
    
    return stats

def start_session(username):
    """Start a new session for user"""
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO sessions (username) VALUES (?)',
        (username,)
    )
    conn.commit()
    
    session_id = conn.lastrowid
    conn.close()
    
    return session_id

def end_session(session_id, emotions_detected=0):
    """End a session"""
    conn = get_db_connection()
    
    conn.execute(
        'UPDATE sessions SET session_end = CURRENT_TIMESTAMP, emotions_detected = ? WHERE id = ?',
        (emotions_detected, session_id)
    )
    conn.commit()
    conn.close()

def get_recent_emotions(username, limit=10):
    """Get recent emotion detections for user"""
    conn = get_db_connection()
    
    emotions = conn.execute(
        'SELECT emotion, confidence, timestamp FROM emotions_log WHERE username = ? ORDER BY timestamp DESC LIMIT ?',
        (username, limit)
    ).fetchall()
    
    conn.close()
    
    return [dict(row) for row in emotions]

def get_emotion_trends(username, days=30):
    """Get emotion trends for the past N days"""
    conn = get_db_connection()
    
    trends = conn.execute('''
        SELECT DATE(timestamp) as date, emotion, COUNT(*) as count 
        FROM emotions_log 
        WHERE username = ? AND timestamp >= date('now', '-{} days')
        GROUP BY DATE(timestamp), emotion
        ORDER BY date DESC
    '''.format(days), (username,)).fetchall()
    
    conn.close()
    
    return [dict(row) for row in trends]

# Initialize database on import
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")