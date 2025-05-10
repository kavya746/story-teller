import streamlit as st
import re
import requests
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore, credentials, initialize_app, get_app
import json

# Load Firebase API Key
load_dotenv()
API_KEY = st.secrets["api_keys"]["firebase"]

# Check if Firebase is already initialized
try:
    app = get_app()
except ValueError:
    firebase_config = st.secrets["firebase"]
    cred = credentials.Certificate(dict(firebase_config))
    app = firebase_admin.initialize_app(cred)

# Firestore reference to store user details
db = firestore.client()

# Background styling
def apply_auth_background():
    st.markdown("""
    <style>
        .stApp {
            background-image: url("https://i.pinimg.com/564x/2c/42/fd/2c42fdca18965807e6f56f19ef33f439.jpg");
            background-size: cover;
            background-position: center;
        }
        .auth-box {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# Function to signup new user
def signup(email, password):
    # Password validation
    if len(password) < 8 or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "weak_password"
    
    # Firebase Authentication signup URL
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    # Send request to Firebase
    res = requests.post(url, json=payload)
    data = res.json()

    if res.status_code == 200:
        # Store user data in Firestore after successful signup
        user_ref = db.collection('users').document(email)
        user_ref.set({
            "email": email,
            "password": password  # You should ideally hash passwords in production
        })
        return "success"
    elif "EMAIL_EXISTS" in data.get("error", {}).get("message", ""):
        return "email_exists"
    else:
        return "error"

# Function to login user
def login(email, password):
    # Firebase Authentication login URL
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    # Send request to Firebase
    res = requests.post(url, json=payload)
    data = res.json()

    if res.status_code == 200:
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.id_token = data.get("idToken")
        return True
    else:
        return False

# UI for login/signup
def show_login_signup():
    apply_auth_background()
    st.title("Login / Signup")

    # Add selectbox for switching between login and signup
    choice = st.selectbox("Choose an option", ["Login", "Signup"],key="auth_choice")

    if choice == "Signup":
        st.subheader("Signup")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Signup"):
            result = signup(email, password)
            if result == "success":
                st.success("Signup successful. You can now log in.")
            elif result == "email_exists":
                st.error("Email already exists.")
            elif result == "weak_password":
                st.error("Password is too weak. Use 8+ chars with a special character.")
            else:
                st.error("Something went wrong during signup.")
    elif choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login(email, password):
                st.success("Login successful!")
            else:
                st.error("Invalid email or password.")


# Main logic
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login_signup()
else:
    st.success(f"Welcome, {st.session_state.user_email}!")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()
