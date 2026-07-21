import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from utils.auth import login_user

# Center container logic using columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Display logo if exists
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=280)
    else:
        st.markdown("<h1 style='text-align: center; color: #1d4ed8;'>EduAttend</h1>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>Sign in to your account</h3>", unsafe_allow_html=True)
    
    # Create the form
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        
        # Show/Hide password checkbox outside form doesn't work well, but inside form is fine.
        # However, to avoid form submission on checkbox change, we can place it here.
        show_password = st.checkbox("Show Password", value=False)
        password_type = "default" if show_password else "password"
        
        password = st.text_input("Password", type=password_type, placeholder="Enter your password")
        
        # Remember Me and Forgot Password (dummy) row
        col_rem, col_forgot = st.columns([1, 1])
        with col_rem:
            remember_me = st.checkbox("Remember Me", value=False)
        with col_forgot:
            # We use an empty button style or link
            forgot_clicked = st.form_submit_button("Forgot Password?", type="secondary")
            
        submit_btn = st.form_submit_button("Login", use_container_width=True)
        
        if forgot_clicked:
            st.info("Forgot password? Please contact your System Administrator to reset it.")
            
        if submit_btn:
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.toast("Welcome back!", icon="🎓")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)
                
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bottom redirect link
    st.markdown("<p style='text-align: center; margin-top: 1.5rem;'>New here? Go to the Register tab in the sidebar.</p>", unsafe_allow_html=True)
