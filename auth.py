import streamlit as st
import re

# Dummy user data storage (for demonstration purposes)
user_data = {
    "user@example.com": {"password": "password123"}
}

# Function to check login credentials
def login(email, password):
    user = user_data.get(email)
    if user and user["password"] == password:
        st.session_state.authenticated = True
        return True
    else:
        return False

# Function to register new users
def signup(email, password):
    # Check if the password meets the criteria
    if len(password) < 8 or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "weak_password"  # Return a specific status for weak passwords

    if email in user_data:
        return "email_exists"  # Email already exists
    else:
        user_data[email] = {"password": password}
        return "success"