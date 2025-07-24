import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from components.auth import check_authentication, get_user_info, update_user_profile
from components.auth import show_profile_settings

st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")

# Check authentication
if not check_authentication():
    st.warning("You must be logged in to access this page. Please go to the Login page.")
    st.stop()

st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>👤 My Profile</h2>", unsafe_allow_html=True)

show_profile_settings() 