import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from utils.auth import get_current_user, update_user_password, logout_user

# Check if authenticated
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("👤 My Profile")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Account Details")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom display of profile data
    role_color = "badge-admin" if user["role"] == "Admin" else "badge-faculty"
    
    st.markdown(f"""
    <div style="background-color: white; padding: 2rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <p style="font-size: 1rem; color: #64748b; margin-bottom: 0.25rem;">FULL NAME</p>
        <p style="font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 1.5rem;">{user["fullname"]}</p>
        
        <p style="font-size: 1rem; color: #64748b; margin-bottom: 0.25rem;">EMAIL ADDRESS</p>
        <p style="font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 1.5rem;">{user["email"]}</p>
        
        <p style="font-size: 1rem; color: #64748b; margin-bottom: 0.25rem;">USERNAME</p>
        <p style="font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 1.5rem;">{user["username"]}</p>
        
        <p style="font-size: 1rem; color: #64748b; margin-bottom: 0.25rem;">ROLE</p>
        <span class="custom-badge {role_color}" style="font-size: 1rem; padding: 0.4rem 1rem;">{user["role"]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Logout action
    if st.button("Logout", key="logout_btn", use_container_width=True):
        logout_user()
        st.toast("Logged out successfully!", icon="🔒")
        time.sleep(0.5)
        st.rerun()

with col2:
    st.subheader("Change Password")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("change_password_form", clear_on_submit=True):
        old_password = st.text_input("Current Password", type="password", placeholder="Enter current password")
        new_password = st.text_input("New Password", type="password", placeholder="At least 6 characters")
        confirm_new = st.text_input("Confirm New Password", type="password", placeholder="Re-type new password")
        
        submit_pwd = st.form_submit_button("Update Password", use_container_width=True)
        
        if submit_pwd:
            if new_password != confirm_new:
                st.error("New passwords do not match.")
            elif not old_password or not new_password:
                st.error("All password fields are required.")
            else:
                success, message = update_user_password(
                    username=user["username"],
                    old_password=old_password,
                    new_password=new_password
                )
                if success:
                    st.success(message)
                    st.toast("Password updated!", icon="🔑")
                else:
                    st.error(message)
