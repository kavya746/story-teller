import torch
import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from io import BytesIO
import google.generativeai as genai
#from google.generativeai.types import FinishReason
from dotenv import load_dotenv
import os
from auth import show_login_signup,apply_auth_background  # Import auth UI

# Load environment variables
load_dotenv()
gemini_api_key = st.secrets["api_keys"]["gemini"]
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    st.error("Gemini API key not found. Please set it in the .env file.")

# Initialize login session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Show login/signup first
if not st.session_state.authenticated:
    apply_auth_background()
    show_login_signup()
    st.stop()

# Load custom CSS if available
if os.path.exists("styles.css"):
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load BLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# Background options
background_options = {
    "White": "https://i.pinimg.com/564x/2c/42/fd/2c42fdca18965807e6f56f19ef33f439.jpg",
    "Pink": "https://i.pinimg.com/736x/d8/62/78/d86278955da0973e3b1ccd8207497cae.jpg",
    "Blue": "https://i.pinimg.com/736x/7c/97/47/7c97471a1ecff173e7f241c9110ad029.jpg",
    "Yellow": "https://i.pinimg.com/736x/3f/ae/e1/3faee18c95220c3235ea96f09c6440fb.jpg"
}

# Functions
def generate_image_caption(image):
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    caption_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption

def generate_story_with_gemini(captions, max_tokens, genre):
    genre_prompts = {
        "Fantasy": "Write a magical and imaginative fantasy story. Include fantastical elements and creatures.",
        "Science-fiction": "Write a futuristic and imaginative science-fiction story. Incorporate advanced technology or space exploration.",
        "Horror": "Write a spine-chilling horror story. Create an atmosphere of fear, suspense, and the supernatural.",
        "Mystery": "Write a gripping mystery story. Include clues, detective work, and an unexpected twist.",
        "Historical": "Write a historically accurate story, set in a specific historical period with authentic events and characters."
    }

    prompt = f"{genre_prompts.get(genre, '')} Based on the following captions:\n\n" + "\n".join(captions)

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens})
        # return response.text.strip()
        # Safely check if content exists
        if response.candidates and response.candidates[0].content.parts:
            return response.text.strip()

        # Handle safety or empty responses
        finish_reason = (
            response.candidates[0].finish_reason.name
            if response.candidates and response.candidates[0].finish_reason
            else "UNKNOWN"
        )

        if finish_reason == "SAFETY":
            st.error("Story generation was blocked by Gemini safety filters. Try using different images or genre.")
        elif finish_reason == "MAX_TOKENS":
            st.warning("Story generation stopped because the maximum token limit was reached. Try increasing the token limit.")
        else:
            st.error(f"No content returned by Gemini (Finish reason: {finish_reason}).")

        return "Could not generate the story."
        
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return "An error occurred while generating the story."

# --- Streamlit App ---
st.title("Interactive AI Storyteller")

# Sidebar: background color & genre
st.sidebar.write("#### Select Background Color")
selected_background = st.sidebar.radio("Background Color", options=list(background_options.keys()), label_visibility="collapsed")
st.session_state.selected_background = background_options[selected_background]

genre_options = ["Fantasy", "Science-fiction", "Horror", "Mystery", "Historical"]
selected_genre = st.sidebar.selectbox("#### Select Story Genre", options=genre_options)

# Sidebar: logout
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# Apply background
st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("{st.session_state.selected_background}");
            background-size: cover;
            background-position: center;
        }}
    </style>
""", unsafe_allow_html=True)

# Upload image
uploaded_files = st.file_uploader("Upload Image Files", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

# Story length
options=[1024, 2048] 
default_index = 1 if len(options) > 1 else 0
max_tokens = st.selectbox("Select Story Length (Tokens)", options=options, index=default_index)

# Captioning and story generation
if uploaded_files:
    captions = []
    for uploaded_file in uploaded_files:
        try:
            img = Image.open(BytesIO(uploaded_file.read()))
            img = img.convert("RGB")
            st.image(img, caption="Uploaded Image")
            caption = generate_image_caption(img)
            captions.append(caption)
            st.write(f"**Caption:** {caption}")
        except Exception as e:
            st.error(f"Error processing image: {e}")

    if st.button("Generate Story"):
        if captions:
            story = generate_story_with_gemini(captions, max_tokens, selected_genre)
            st.subheader("Generated Story")
            st.write(story)
        else:
            st.warning("No captions generated. Please upload valid images.")

