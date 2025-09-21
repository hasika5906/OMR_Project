import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # make sure these exist in omr_scanner.py

# Set page config
st.set_page_config(page_title="OMR Scanner", layout="wide")

# =======================
# CSS Styling
# =======================
st.markdown(
    """
    <style>
    /* Overall App Background & Text */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #0b0b17);
        color: #00ffcc;
        font-family: 'Arial', sans-serif;
    }

    /* Login & Upload Section Boxes */
    .login-box, .upload-box, .instruction-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 0px 20px rgba(0, 255, 204, 0.4);
        margin-bottom: 20px;
        color: white !important;
    }

    /* Labels */
    .login-box label, .upload-box label, .instruction-box label {
        color: white !important;
        font-weight: bold;
        font-family: Arial !important;
    }

    /* Input text & placeholder white */
    .stTextInput>div>div>input, 
    .stTextInput>div>div>input::placeholder, 
    .stFileUploader>div>div>input {
        color: white !important;
        font-family: Arial !important;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #00ffcc !important;
        color: black !important;
        font-weight: bold;
    }

    /* Scrolling marquee text */
    .marquee {
        font-size: 22px;
        font-weight: bold;
        color: #00ffcc;
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =======================
# Login Page
# =======================
def login_page():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=180)  # Add your logo in assets folder
    st.write("### Login to OMR Scanner")
    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    if st.button("Login"):
        # For prototyping: any username/password works
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Instruction Page
# =======================
def instruction_page():
    st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
    st.write("### Instructions:")
    st.markdown("""
    - Upload **OMR sheets** in JPG, PNG or ZIP of images.
    - Upload the **Answer Key JSON**.
    - After upload, click process to see **scores and answers**.
    """)
    st.markdown('<marquee class="marquee">Upload multiple sheets or a ZIP file for batch processing!</marquee>', unsafe_allow_html=True)
    if st.button("Continue to Upload"):
        st.session_state['page'] = 'upload'
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Upload & Processing Page
# =======================
def upload_page():
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.title("OMR Scanner Web App")
    uploaded_files = st.file_uploader(
        "Upload OMR sheet images (JPEG, PNG) or ZIP of images", 
        type=["jpg", "jpeg", "png", "zip"], 
        accept_multiple_files=True
    )
    answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])
    if uploaded_files and answer_key_path:
        # Save uploaded answer key
        answer_key_file_path = os.path.join("temp", "answer_key.json")
        os.makedirs("temp", exist_ok=True)
        with open(answer_key_file_path, "wb") as f:
            f.write(answer_key_path.getbuffer())

        # Load answer key
        answer_key = load_answer_keys(answer_key_file_path)

        # Prepare list of images to process
        images_to_process = []

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".zip"):
                # Extract ZIP
                with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                    zip_ref.extractall("temp/omr_images")
                for root, _, files in os.walk("temp/omr_images"):
                    for file in files:
                        if file.lower().endswith((".jpg", ".jpeg", ".png")):
                            images_to_process.append(os.path.join(root, file))
            else:
                # Save individual image
                img_path = os.path.join("temp", uploaded_file.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                images_to_process.append(img_path)

        st.subheader("Processing Results")
        for img_path in images_to_process:
            img_name = os.path.basename(img_path)
            result = process_omr_image(img_path, answer_key)
            st.write(f"**File:** {img_name}")
            st.write(f"**Score:** {result['score']} / 100")
            st.write("**Answers:**")
            st.write(result['answers'])
            st.image(result['image'], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Session Management
# =======================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['page'] = 'login'

if not st.session_state['logged_in']:
    login_page()
elif st.session_state['page'] == 'upload':
    upload_page()
else:
    instruction_page()
