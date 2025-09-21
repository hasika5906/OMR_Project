import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # ensure these exist

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="OMR Scanner", layout="wide", initial_sidebar_state="expanded")

# ===============================
# CUSTOM CSS
# ===============================
st.markdown(
    """
    <style>
    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #0b0b17);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }

    /* Big title */
    .big-title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #00ffcc;
    }

    /* Instructions box */
    .instructions {
        background-color: rgba(0, 255, 204, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #00ffcc;
    }

    /* Footer links */
    .footer {
        color: #00ffcc;
        text-align: center;
        font-size: 14px;
        margin-top: 20px;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #00ffcc;
        color: black;
        font-weight: bold;
    }

    /* File uploader */
    .stFileUploader > label {
        color: #00ffcc;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# LOGIN PAGE (Option A)
# ===============================
def login_page():
    st.markdown('<p class="big-title">🔐 Welcome to OMR Scanner (Prototype)</p>', unsafe_allow_html=True)

    # Logo (online placeholder)
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Check_green_icon.svg/768px-Check_green_icon.svg.png",
        width=120,
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login", type="primary"):
        # Accept any non-empty username/password
        if username.strip() != "" and password.strip() != "":
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Logged in as {username} (prototype mode)")
        else:
            st.error("Please enter a username and password (prototype mode accepts any non-empty values).")

    st.markdown(
        """
        <div class="instructions">
            <h4>ℹ️ Prototype Login Instructions</h4>
            <ul>
                <li>Enter any username and password to login.</li>
                <li>This is for demo/prototype only.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Show main app if authenticated
    if st.session_state.get("authenticated", False):
        main_app()


# ===============================
# MAIN APP (OMR Processing)
# ===============================
def main_app():
    st.markdown(f"<h2 style='color:#00ffcc;'>👋 Hello, {st.session_state.get('username', '')}</h2>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="instructions">
            <h4>Instructions:</h4>
            <ul>
                <li>Upload OMR sheet images (JPEG, PNG) or ZIP of images.</li>
                <li>Upload corresponding answer key JSON file.</li>
                <li>Results will display score and detected answers with image.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Upload OMR sheets
    uploaded_files = st.file_uploader(
        "Upload OMR sheet images or ZIP", 
        type=["jpg", "jpeg", "png", "zip"], 
        accept_multiple_files=True
    )

    # Upload answer key
    answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])

    if uploaded_files and answer_key_path:
        os.makedirs("temp", exist_ok=True)
        answer_key_file_path = os.path.join("temp", "answer_key.json")
        with open(answer_key_file_path, "wb") as f:
            f.write(answer_key_path.getbuffer())

        try:
            answer_key = load_answer_keys(answer_key_file_path)
        except Exception as e:
            st.error(f"Error loading answer key: {e}")
            return

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

        st.subheader("Processing Results")
        for img_path in images_to_process:
            img_name = os.path.basename(img_path)
            try:
                result = process_omr_image(img_path, answer_key)
                st.write(f"**File:** {img_name}")
                st.write(f"**Score:** {result['score']} / 100")
                st.write("**Answers:**")
                st.write(result['answers'])
                st.image(result['image'], use_container_width=True)
            except Exception as e:
                st.error(f"Error processing {img_name}: {e}")

    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>About | Contact | Prototype Version</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ===============================
# RUN
# ===============================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

login_page()
