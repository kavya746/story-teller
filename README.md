
Check it here - https://storyteller-using-ai.streamlit.app/

# 🧠📖 Interactive AI Storyteller

An AI-powered web app that generates captivating stories based on images you upload! This Streamlit-based application uses **BLIP** for image captioning and **Gemini (Google Generative AI)** to create stories in various genres. User authentication is handled with Firebase.

---

## ✨ Features

* 🔐 **User Authentication**: Signup/Login via Firebase.
* 🖼️ **Multi-Image Upload**: Upload multiple images to build a visual narrative.
* 📝 **Image Captioning**: Uses BLIP (from Hugging Face) to generate intelligent captions.
* 🤖 **AI Story Generation**: Uses Gemini 2.5 Flash API to create stories based on image captions.
* 🎭 **Genre Selection**: Choose from Fantasy, Sci-Fi, Horror, Mystery, and Historical.
* 🎨 **Custom Backgrounds**: Select a visual background theme for your storytelling experience.

---


## 🛠️ Tech Stack

| Technology             | Purpose                             |
| ---------------------- | ----------------------------------- |
| `Streamlit`            | Web App UI                          |
| `Firebase`             | Authentication & Firestore Database |
| `BLIP (Salesforce)`    | Image Captioning                    |
| `Gemini 2.5 Flash API` | Story Generation                    |
| `Python`               | Backend logic                       |
| `dotenv`               | Environment configuration           |

---

## 📂 Project Structure

```
📁 interactive-ai-storyteller/
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication logic with Firebase
├── styles.css             # Optional CSS for UI styling
├── .streamlit/
│   └── secrets.toml       # Stores API keys (do not share publicly)
├── requirements.txt       # List of dependencies
├── README.md              # Project documentation
└── .env                   # Environment variables (Gemini API Key, etc.)
```

---

## 🔐 Setup & Installation

### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/interactive-ai-storyteller.git
cd interactive-ai-storyteller
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Add Environment Variables**

Create a `.env` file:

```env
# .env
GEMINI_API_KEY=your_gemini_api_key
```

Or use `secrets.toml` for Streamlit Cloud:

```toml
# .streamlit/secrets.toml
[api_keys]
gemini = "your_gemini_api_key"
firebase = "your_firebase_web_api_key"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxx@your-project-id.iam.gserviceaccount.com"
...
```

> 🔒 **Never share your API keys or `.env` file publicly.**

---

## ▶️ Run the App Locally

```bash
streamlit run app.py
```

---

## 📷 Sample Usage

1. Sign up or login.
2. Upload one or more images.
3. Select a background and a genre (e.g., Horror, Mystery).
4. Choose story length (e.g., 1024 or 2048 tokens).
5. Click **Generate Story** to see the magic!

---

## 🧠 How It Works

1. **BLIP** generates a caption for each image.
2. Captions are combined into a prompt.
3. **Gemini** generates a story based on the prompt and genre.
4. Story is displayed on a visually styled Streamlit interface.

---

## 🔐 Firebase Authentication

* Signup/Login via email & password.
* Password validation (min 8 chars, includes a special character).
* Firestore used to store user data (email, password).

