import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from utils.auth import register_user

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
        
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>Create a new account</h3>", unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=True):
        fullname = st.text_input("Full Name", placeholder="e.g. John Doe")
        email = st.text_input("Email", placeholder="e.g. johndoe@school.edu")
        username = st.text_input("Username", placeholder="Create username")
        
        role = st.selectbox("Role", ["Faculty", "Admin"])
        
        password = st.text_input("Password", type="password", placeholder="Choose a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        
        submit_btn = st.form_submit_button("Register", use_container_width=True)
        
        if submit_btn:
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(
                    fullname=fullname,
                    email=email,
                    username=username,
                    password=password,
                    role=role
                )
                if success:
                    st.success(message + " You can now log in.")
                    st.toast("Registration completed!", icon="📝")
                    time.sleep(1.5)
                else:
                    st.error(message)
                    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Redirect to login instruction
    st.markdown("<p style='text-align: center; margin-top: 1.5rem;'>Already have an account? Go to the Login tab in the sidebar.</p>", unsafe_allow_html=True)
