# streamlit_app.py

import streamlit as st
from PIL import Image
import os
import zipfile
from io import BytesIO
from omr_scanner import load_answer_keys, grade_omr_image  # Make sure your grading functions exist

# ----- Page Config -----
st.set_page_config(
    page_title="OMR Scanner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- UI Styles -----
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        color: #212529;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        height: 40px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True
)

# ----- Header -----
st.title("📄 Interactive OMR Scanner")
st.markdown("Upload OMR images or a ZIP file and instantly get your scores!")

# ----- Sidebar: Answer Key Selection -----
st.sidebar.header("Configuration")
answer_key_set = st.sidebar.selectbox("Select Answer Key Set:", ["A", "B"])
BASE_DIR = os.path.dirname(__file__)
answer_key_path = os.path.join(BASE_DIR, f"answer_key_Set{answer_key_set}.json")

# Load Answer Key
try:
    answer_key = load_answer_keys(answer_key_path)
except FileNotFoundError:
    st.error(f"Answer key file not found: {answer_key_path}")
    st.stop()

# ----- File Upload -----
st.sidebar.header("Upload OMR Sheets")
uploaded_files = st.sidebar.file_uploader(
    "Upload image(s) or a ZIP file",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True
)

def process_uploaded_file(file):
    """Return a list of images from uploaded file"""
    images = []
    if file.name.endswith(".zip"):
        with zipfile.ZipFile(file) as z:
            for fname in z.namelist():
                if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(Image.open(BytesIO(z.read(fname))))
    else:
        images.append(Image.open(file))
    return images

# ----- Main Processing -----
if uploaded_files:
    all_images = []
    for file in uploaded_files:
        all_images.extend(process_uploaded_file(file))

    st.subheader("Grading Results")
    for idx, img in enumerate(all_images, start=1):
        st.markdown(f"### Image {idx}")
        st.image(img, use_container_width=True)

        # Convert PIL image to proper format for your grading function if needed
        score, per_question = grade_omr_image(img, answer_key)

        st.success(f"Total Score: {score}/{len(answer_key)}")

        # Optional: show per-question results
        st.write("Per Question Feedback:")
        for q_num, ans in per_question.items():
            st.write(f"Q{q_num}: {ans}")

else:
    st.info("Please upload at least one OMR image or a ZIP file to start grading.")
