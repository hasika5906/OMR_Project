import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # logic unchanged

# Page configuration
st.set_page_config(
    page_title="OMR Scanner", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Sidebar for instructions and branding
st.sidebar.title("OMR Scanner")
st.sidebar.markdown("""
🎯 **Instructions**:
1. Upload OMR sheet images (JPEG, PNG) or a ZIP of multiple images.
2. Upload the answer key JSON file.
3. View results interactively below.
""")
st.sidebar.image("https://img.icons8.com/color/96/000000/checklist.png", use_column_width=True)

# Main header
st.markdown(
    "<h1 style='text-align: center; color: #4B8BBE;'>OMR Scanner Web App</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Upload section with colorful card-style layout
st.markdown("## 📤 Upload Your Files")
uploaded_files = st.file_uploader(
    "Select OMR sheet images (JPEG, PNG) or a ZIP of images", 
    type=["jpg", "jpeg", "png", "zip"], 
    accept_multiple_files=True
)

answer_key_path = st.file_uploader(
    "Upload Answer Key JSON", 
    type=["json"]
)

# Process if both files are uploaded
if uploaded_files and answer_key_path:
    # Save uploaded answer key
    os.makedirs("temp", exist_ok=True)
    answer_key_file_path = os.path.join("temp", "answer_key.json")
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

    # Display results in an attractive layout
    st.markdown("## 📝 Processing Results")
    for img_path in images_to_process:
        img_name = os.path.basename(img_path)
        result = process_omr_image(img_path, answer_key)  # unchanged logic

        # Colorful container for each result
        st.markdown(
            f"""
            <div style='background-color:#E8F0FE; padding:20px; border-radius:10px; margin-bottom:15px;'>
            <h3 style='color:#0F4C81;'>File: {img_name}</h3>
            <h4 style='color:#FF6F61;'>Score: {result['score']} / 100</h4>
            <strong style='color:#2E8B57;'>Answers:</strong>
            <pre style='background-color:#F0F8FF; padding:10px; border-radius:5px;'>{result['answers']}</pre>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.image(result['image'], use_container_width=True)

else:
    st.info("Please upload OMR sheets and an Answer Key JSON to start processing.")
