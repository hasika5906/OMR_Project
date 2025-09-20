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

# Apply custom CSS for dark theme
st.markdown("""
    <style>
        body {
            background-color: #000000;
            color: #FFFFFF;
        }
        .stApp {
            background-color: #000000;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00FFAA !important;
        }
        .result-card {
            background-color: #1A1A1A;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #333333;
        }
        .answers-box {
            background-color: #121212;
            color: #00FFAA;
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚡ OMR Scanner")
st.sidebar.markdown("""
📌 **Steps**:
1. Upload OMR sheet images (JPG, PNG) or a ZIP.  
2. Upload the Answer Key JSON.  
3. View the results below.  
""")
st.sidebar.markdown("---")
st.sidebar.success("Dark Mode Active ✅")

# Main header
st.markdown(
    "<h1 style='text-align: center;'>📝 OMR Scanner Web App</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Upload section
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

    # Results section
    st.markdown("## 🚀 Processing Results")
    for img_path in images_to_process:
        img_name = os.path.basename(img_path)
        result = process_omr_image(img_path, answer_key)  # logic unchanged

        st.markdown(
            f"""
            <div class='result-card'>
                <h3>📄 File: {img_name}</h3>
                <h4 style='color:#FFAA00;'>🏆 Score: {result['score']} / 100</h4>
                <div class='answers-box'>{result['answers']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.image(result['image'], use_container_width=True)

else:
    st.info("⬆️ Please upload OMR sheets and an Answer Key JSON to start processing.")
