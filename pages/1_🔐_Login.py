import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from components.database import create_user, verify_user, get_db_connection

def is_valid_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.authenticated:
    st.success(f"Welcome back, {st.session_state.username}!")
    st.info("You are already logged in. Navigate to other pages using the sidebar.")
    st.stop()

# After successful login or signup, redirect to Real-Time Detection page
try:
    from streamlit_extras.switch_page_button import switch_page
    _has_switch_page = True
except ImportError:
    _has_switch_page = False
REALTIME_PAGE = '3_📷_Real_Time_Detection'

# Login/Signup tabs
login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

with login_tab:
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.subheader("🔑 Login to Your Account")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        login_btn = st.form_submit_button("🚀 Login")
        if login_btn:
            if not username or not password:
                st.error("⚠️ Please fill in all fields!")
            elif verify_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("✅ Login successful! Redirecting to Real-Time Detection...")
                if _has_switch_page:
                    switch_page(REALTIME_PAGE)
                else:
                    st.markdown(f'<a href="/{REALTIME_PAGE}" target="_self" style="display:inline-block;margin-top:1rem;padding:0.7rem 2rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border-radius:10px;text-decoration:none;font-weight:bold;">Go to Real-Time Detection</a>', unsafe_allow_html=True)
                st.stop()
            else:
                st.error("❌ Invalid username or password!")
    st.markdown('</div>', unsafe_allow_html=True)

with signup_tab:
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.subheader("🆕 Create New Account")
    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input("👤 Username", placeholder="Choose a username")
        new_email = st.text_input("📧 Email", placeholder="Enter your email")
        new_password = st.text_input("🔒 Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        signup_btn = st.form_submit_button("🎉 Create Account")
        if signup_btn:
            if not all([new_username, new_email, new_password, confirm_password]):
                st.error("⚠️ Please fill in all fields!")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match!")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters long!")
            elif not is_valid_email(new_email):
                st.error("❌ Please enter a valid email address!")
            else:
                conn = get_db_connection()
                user = conn.execute('SELECT username FROM users WHERE username = ?', (new_username,)).fetchone()
                conn.close()
                if user:
                    st.error("❌ Username already exists! Please choose another.")
                else:
                    if create_user(new_username, new_password, new_email):
                        st.session_state.authenticated = True
                        st.session_state.username = new_username
                        st.success("🎉 Account created and logged in! Redirecting to Real-Time Detection...")
                        if _has_switch_page:
                            switch_page(REALTIME_PAGE)
                        else:
                            st.markdown(f'<a href="/{REALTIME_PAGE}" target="_self" style="display:inline-block;margin-top:1rem;padding:0.7rem 2rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border-radius:10px;text-decoration:none;font-weight:bold;">Go to Real-Time Detection</a>', unsafe_allow_html=True)
                        st.stop()
                    else:
                        st.error("❌ Registration failed. Please try again.")
    st.markdown('</div>', unsafe_allow_html=True)