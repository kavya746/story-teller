import openai
import torch
from PIL import Image
import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from io import BytesIO
import auth 
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Set up your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")

# Load and apply custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the BLIP model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# List of background image URLs for selection
background_options = {
    "White": "https://i.pinimg.com/564x/2c/42/fd/2c42fdca18965807e6f56f19ef33f439.jpg",
    "Pink": "https://i.pinimg.com/736x/d8/62/78/d86278955da0973e3b1ccd8207497cae.jpg",
    "Blue": "https://i.pinimg.com/736x/7c/97/47/7c97471a1ecff173e7f241c9110ad029.jpg",
    "Yellow": "https://i.pinimg.com/736x/3f/ae/e1/3faee18c95220c3235ea96f09c6440fb.jpg"
}

# Function to generate captions from images using BLIP
def generate_image_caption(image):
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    caption_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption

# Function to generate a story using GPT-3.5 based on captions and token limit
def generate_story_from_captions(captions, max_tokens, genre):
    genre_prompts = {
        "Fantasy": "Write a magical and imaginative fantasy story. Include fantastical elements and creatures.",
        "Science-fiction": "Write a futuristic and imaginative science-fiction story. Incorporate advanced technology or space exploration.",
        "Horror": "Write a spine-chilling horror story. Create an atmosphere of fear, suspense, and the supernatural.",
        "Mystery": "Write a gripping mystery story. Include clues, detective work, and an unexpected twist.",
        "Historical": "Write a historically accurate story, set in a specific historical period with authentic events and characters."
    }

    # Start the prompt with the selected genre-specific instructions
    prompt = f"{genre_prompts.get(genre, '')} Based on the following captions:\n\n" + "\n".join(captions)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a creative storyteller."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    story = response['choices'][0]['message']['content'].strip()
    return story

# Function to check remaining credits (usage tracking)
def check_openai_usage():
    try:
        usage = openai.Usage.retrieve()
        remaining_credits = usage['total_usage']  # You can refine this based on what details you need
        return remaining_credits
    except openai.error.OpenAIError as e:
        st.error(f"Error retrieving usage: {e}")
        return 0

# Manage session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_mode" not in st.session_state:  # Track current mode (Signup or Login)
    st.session_state.auth_mode = "Signup"

if not st.session_state.authenticated:
    # Dropdown for selecting between "Signup" and "Login"
    auth_option = st.selectbox("Select an option", ["Signup", "Login"], index=0, label_visibility="collapsed")
    st.session_state.auth_mode = auth_option  # Update session state with the selected option

    if st.session_state.auth_mode == "Signup":
        st.title("Sign Up")

        # Signup input fields
        username_email = st.text_input("Username/Email", label_visibility="visible")
        password = st.text_input("Password", type="password", label_visibility="visible")

        # Signup button
        if st.button("Sign Up"):
            signup_status = auth.signup(username_email, password)
            if signup_status == "success":
                st.success("Account created successfully! Please log in.")
                st.session_state.auth_mode = "Login"  # Switch to login mode
            elif signup_status == "email_exists":
                st.error("Username/Email already exists. Try logging in.")
            elif signup_status == "weak_password":
                st.error("Weak password. Please use at least 8 characters, including 1 special character.")

    elif st.session_state.auth_mode == "Login":
        st.title("Login")

        # Login input fields
        username_email = st.text_input("Username/Email", label_visibility="visible")
        password = st.text_input("Password", type="password", label_visibility="visible")

        # Login button
        if st.button("Login"):
            if auth.login(username_email, password):
                st.success("Login successful!")
                st.session_state.authenticated = True
            else:
                st.error("Invalid credentials.")

else:
    # Main app content (already logged in)
    st.title("Interactive AI Storyteller")

    # Check remaining credits before allowing story generation
    remaining_credits = check_openai_usage()

    if remaining_credits > 0:
        # Sidebar for background selection
        st.sidebar.write("#### Select Background Color")
        selected_background = st.sidebar.radio(
            "Background Color", options=list(background_options.keys()), label_visibility="collapsed"
        )
        st.session_state.selected_background = background_options[selected_background]

        # Sidebar for genre selection (after background selection)
        genre_options = ["Fantasy", "Science-fiction", "Horror", "Mystery", "Historical"]
        selected_genre = st.sidebar.selectbox("#### Select Story Genre", options=genre_options, label_visibility="visible")

        # Apply the selected background style
        st.markdown(f"""
        <style>
            .stApp {{
                background-image: url("{st.session_state.selected_background}");
                background-size: cover;
                background-position: center;
            }}
        </style>
        """, unsafe_allow_html=True)

        # File uploader for images
        uploaded_files = st.file_uploader(
            "Upload Image Files", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], label_visibility="visible"
        )

        # Dropdown to select max tokens for story generation
        max_tokens = st.selectbox(
            "Select Story Length (Tokens)", options=[500, 750], index=2, label_visibility="visible"
        )

        if uploaded_files:
            captions = []
            images = []

            # Process uploaded images
            for uploaded_file in uploaded_files:
                try:
                    img = Image.open(BytesIO(uploaded_file.read()))
                    if img is None:
                        st.error("Failed to load image.")
                    else:
                        img = img.convert("RGB")
                        st.image(img, caption="Uploaded Image")  # Ensure this works with your version of Streamlit
                    # Generate and display caption
                    caption = generate_image_caption(img)
                    captions.append(caption)
                    st.write(f"**Caption:** {caption}")

                except Exception as e:
                    st.error(f"Error processing image {uploaded_file.name}: {e}")

            # Button to generate the story based on selected genre
            if st.button("Generate Story"):
                if captions:
                    story = generate_story_from_captions(captions, max_tokens, selected_genre)
                    st.subheader("Generated Story")
                    st.write(story)
                else:
                    st.warning("No captions were generated. Please upload valid images.")
    else:
        st.error("You have exhausted your free credits. Please upgrade your plan to continue using the API.")
