import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys

# ---- PAGE CONFIG ----
st.set_page_config(page_title="OMR Scanner", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #ff4b2b;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
    }
    .stTextInput>div>input, .stFileUploader>div>input {
        background-color: #222;
        color: white;
        border-radius: 8px;
        padding: 0.5em;
    }
    .stExpanderHeader {
        font-weight: bold;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# ---- LOGIN PAGE ----
def login_page():
    st.title("Welcome to OMR Scanner")
    st.subheader("Login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username.strip() != "" and password.strip() != "":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Instructions"
            st.experimental_rerun()
        else:
            st.error("Please enter username and password")

# ---- NAVIGATION MENU ----
def sidebar_menu():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Instructions", "Dashboard", "About", "Contact"])
    st.session_state['page'] = page

# ---- INSTRUCTIONS PAGE ----
def instructions_page():
    st.title("Instructions")
    st.markdown("""
    1. Upload OMR sheet images (JPEG, PNG) or a ZIP of images.  
    2. Upload the answer key in JSON format.  
    3. Click 'Process' to see results.  
    4. Results include score and detected answers.  
    """)
    st.info("Use the sidebar to navigate to Dashboard, About, or Contact pages.")

# ---- DASHBOARD PAGE ----
def dashboard_page():
    st.title("OMR Scanner Dashboard")
    uploaded_files = st.file_uploader(
        "Upload OMR sheet images (JPEG, PNG) or ZIP of images", 
        type=["jpg", "jpeg", "png", "zip"], 
        accept_multiple_files=True
    )
    answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])

    if uploaded_files and answer_key_path:
        os.makedirs("temp", exist_ok=True)

        # Save answer key
        answer_key_file_path = os.path.join("temp", "answer_key.json")
        with open(answer_key_file_path, "wb") as f:
            f.write(answer_key_path.getbuffer())

        # Load answer key
        answer_key = load_answer_keys(answer_key_file_path)

        # Prepare images to process
        images_to_process = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".zip"):
                with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                    zip_ref.extractall("temp/omr_images")
                for root, _, files in os.walk("temp/omr_images"):
                    for file in files:
                        if file.lower().endswith((".jpg", ".jpeg", ".png")):
                            images_to_process.append(os.path.join(root, file))
            else:
                img_path = os.path.join("temp", uploaded_file.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                images_to_process.append(img_path)

        # Process images
        st.subheader("Processing Results")
        for img_path in images_to_process:
            img_name = os.path.basename(img_path)
            result = process_omr_image(img_path, answer_key)
            st.write(f"**File:** {img_name}")
            st.write(f"**Score:** {result['score']} / 100")
            st.write("**Answers:**")
            st.write(result['answers'])
            st.image(result['image'], use_container_width=True)

# ---- ABOUT PAGE ----
def about_page():
    st.title("About OMR Scanner")
    st.markdown("""
    This web app is a prototype OMR Scanner built using Python and Streamlit.  
    Features include:  
    - Upload individual images or ZIP files of OMR sheets.  
    - Upload JSON answer keys.  
    - Automatic grading and scoring.  
    - Multi-page interface with instructions, dashboard, about, and contact pages.  
    """)

# ---- CONTACT PAGE ----
def contact_page():
    st.title("Contact Us")
    st.markdown("""
    **Email:** support@omrscanner.com  
    **Phone:** +123-456-7890  
    **Address:** 123 AI Lane, Tech City  
    """)

# ---- MAIN LOGIC ----
if not st.session_state['logged_in']:
    login_page()
else:
    sidebar_menu()
    page = st.session_state['page']
    if page == "Instructions":
        instructions_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "About":
        about_page()
    elif page == "Contact":
        contact_page()
