import hashlib
# pyrefly: ignore [missing-import]
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from utils.database import get_user_by_username, add_user, get_users, save_users

def hash_password(password: str, username: str) -> str:
    """
    Hashes a password with username as a salt using SHA-256.
    """
    salt = username.lower()
    hash_input = password + salt
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

def verify_password(password: str, username: str, hashed: str) -> bool:
    """
    Verifies a password against its hashed value.
    """
    return hash_password(password, username) == hashed

def register_user(fullname: str, email: str, username: str, password: str, role: str) -> Tuple[bool, str]:
    """
    Registers a new user in the database.
    """
    username_clean = username.strip()
    if not fullname.strip() or not email.strip() or not username_clean or not password.strip():
        return False, "All fields are required."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    if get_user_by_username(username_clean):
        return False, f"Username '{username_clean}' is already registered."
        
    hashed_pwd = hash_password(password, username_clean)
    
    user_data = {
        "fullname": fullname.strip(),
        "email": email.strip(),
        "username": username_clean,
        "password": hashed_pwd,
        "role": role  # "Admin" or "Faculty"
    }
    
    success = add_user(user_data)
    if success:
        return True, "Registration successful!"
    return False, "An error occurred. Please try again."

def login_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticates a user and starts a session.
    """
    username_clean = username.strip()
    if not username_clean or not password:
        return False, "Please enter both username and password."
        
    user = get_user_by_username(username_clean)
    if not user:
        return False, "Invalid username or password."
        
    if not verify_password(password, username_clean, user["password"]):
        return False, "Invalid username or password."
        
    # Store user in session state
    st.session_state["authenticated"] = True
    st.session_state["user"] = {
        "fullname": user["fullname"],
        "email": user["email"],
        "username": user["username"],
        "role": user["role"]
    }
    return True, "Login successful!"

def logout_user() -> None:
    """
    Clears the login session.
    """
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    if "current_page" in st.session_state:
        st.session_state["current_page"] = "Login"

def is_logged_in() -> bool:
    """
    Checks if a user is logged in.
    """
    return st.session_state.get("authenticated", False) and st.session_state.get("user") is not None

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Gets the current logged in user details.
    """
    return st.session_state.get("user")

def update_user_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Updates the password for a user.
    """
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
        
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
        
    if not verify_password(old_password, username, user["password"]):
        return False, "Incorrect old password."
        
    # Hash new password and save
    user["password"] = hash_password(new_password, username)
    users = get_users()
    for i, u in enumerate(users):
        if u.get("username") == username:
            users[i] = user
            break
            
    if save_users(users):
        return True, "Password updated successfully!"
    return False, "Failed to update password. Please try again."
