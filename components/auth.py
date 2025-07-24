# components/auth.py - Authentication system for the Face Emotion Detection App

import streamlit as st
import hashlib
import sqlite3
from datetime import datetime, timedelta
import re
from components.database import get_db_connection, hash_password

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid username"

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 50:
        return False, "Password must be less than 50 characters"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Strong password"

def create_user(username, password, email=None):
    """Create a new user account"""
    try:
        # Validate inputs
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            st.error(username_msg)
            return False
        
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            st.error(password_msg)
            return False
        
        if email and not validate_email(email):
            st.error("Please enter a valid email address")
            return False
        
        # Check if username already exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT username FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            st.error("Username already exists! Please choose a different username.")
            return False
        
        # Create new user
        password_hash = hash_password(password)
        conn.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, password_hash, email)
        )
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating account: {str(e)}")
        return False

def verify_user(username, password):
    """Verify user credentials"""
    try:
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
            return True
        
        conn.close()
        return False
        
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def login_user(username):
    """Login user and set session state"""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.login_time = datetime.now()

def logout_user():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None
    
    # Clear other session states
    keys_to_clear = ['messages', 'emotion_history', 'current_session']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_user_info(username):
    """Get user information"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT username, email, created_at, last_login FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
        
    except Exception as e:
        st.error(f"Error getting user info: {str(e)}")
        return None

def update_user_profile(username, email=None):
    """Update user profile"""
    try:
        if email and not validate_email(email):
            st.error("Please enter a valid email address")
            return False
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET email = ? WHERE username = ?',
            (email, username)
        )
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error updating profile: {str(e)}")
        return False

def change_password(username, old_password, new_password):
    """Change user password"""
    try:
        # Verify old password
        if not verify_user(username, old_password):
            st.error("Current password is incorrect")
            return False
        
        # Validate new password
        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            st.error(password_msg)
            return False
        
        # Update password
        conn = get_db_connection()
        new_password_hash = hash_password(new_password)
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE username = ?',
            (new_password_hash, username)
        )
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error changing password: {str(e)}")
        return False

def delete_user_account(username, password):
    """Delete user account"""
    try:
        # Verify password
        if not verify_user(username, password):
            st.error("Password is incorrect")
            return False
        
        conn = get_db_connection()
        
        # Delete user data
        conn.execute('DELETE FROM emotions_log WHERE username = ?', (username,))
        conn.execute('DELETE FROM sessions WHERE username = ?', (username,))
        conn.execute('DELETE FROM users WHERE username = ?', (username,))
        
        conn.commit()
        conn.close()
        
        # Logout user
        logout_user()
        
        return True
        
    except Exception as e:
        st.error(f"Error deleting account: {str(e)}")
        return False

def session_timeout_check():
    """Check if session has timed out"""
    if not check_authentication():
        return False
    
    login_time = st.session_state.get('login_time')
    if not login_time:
        return False
    
    # Check if session has been active for more than 2 hours
    if datetime.now() - login_time > timedelta(hours=2):
        logout_user()
        st.warning("Your session has expired. Please login again.")
        return False
    
    return True

def show_login_form():
    """Display login form"""
    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        if login_button:
            if username and password:
                if verify_user(username, password):
                    login_user(username)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
            else:
                st.error("Please enter both username and password")
        
        if forgot_password:
            st.info("Contact admin for password reset: admin@example.com")

def show_signup_form():
    """Display signup form"""
    with st.form("signup_form"):
        st.subheader("📝 Create Account")
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email (optional)")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        signup_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if signup_button:
            if not terms_accepted:
                st.error("Please accept the Terms of Service and Privacy Policy")
                return
            
            if not username or not password:
                st.error("Username and password are required")
                return
            
            if password != confirm_password:
                st.error("Passwords don't match!")
                return
            
            if create_user(username, password, email):
                st.success("Account created successfully! Please login.")
                return True
    
    return False

def show_profile_settings():
    """Display profile settings"""
    if not check_authentication():
        return
    
    username = st.session_state.username
    user_info = get_user_info(username)
    
    if not user_info:
        st.error("Could not load user information")
        return
    
    st.subheader(f"👤 Profile Settings for {username}")
    
    # User info display
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {user_info['username']}")
        st.info(f"**Email:** {user_info.get('email', 'Not provided')}")
    
    with col2:
        st.info(f"**Member since:** {user_info['created_at'][:10]}")
        st.info(f"**Last login:** {user_info.get('last_login', 'Unknown')[:19] if user_info.get('last_login') else 'Unknown'}")
    
    # Update profile form
    with st.expander("📧 Update Email"):
        with st.form("update_email_form"):
            new_email = st.text_input("New Email", value=user_info.get('email', ''))
            update_email_btn = st.form_submit_button("Update Email")
            
            if update_email_btn:
                if update_user_profile(username, new_email):
                    st.success("Email updated successfully!")
                    st.rerun()
    
    # Change password form
    with st.expander("🔒 Change Password"):
        with st.form("change_password_form"):
            old_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            change_password_btn = st.form_submit_button("Change Password")
            
            if change_password_btn:
                if new_password != confirm_new_password:
                    st.error("New passwords don't match!")
                elif change_password(username, old_password, new_password):
                    st.success("Password changed successfully!")
    
    # Delete account section
    with st.expander("⚠️ Delete Account", expanded=False):
        st.warning("This action cannot be undone!")
        with st.form("delete_account_form"):
            delete_password = st.text_input("Enter your password to confirm deletion", type="password")
            delete_account_btn = st.form_submit_button("Delete Account", type="secondary")
            
            if delete_account_btn:
                if delete_user_account(username, delete_password):
                    st.success("Account deleted successfully!")
                    st.rerun()

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None