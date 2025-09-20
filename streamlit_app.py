import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # make sure these exist in omr_scanner.py

st.set_page_config(page_title="OMR Scanner", layout="wide")
st.title("OMR Scanner Web App")

# Upload OMR sheet(s)
uploaded_files = st.file_uploader(
    "Upload OMR sheet images (JPEG, PNG) or ZIP of images", 
    type=["jpg", "jpeg", "png", "zip"], 
    accept_multiple_files=True
)

# Select answer key
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
        # Process each image
        result = process_omr_image(img_path, answer_key)  # ensure your function returns a dict with 'score', 'answers', 'image'
        
        st.write(f"**File:** {img_name}")
        st.write(f"**Score:** {result['score']} / 100")
        st.write("**Answers:**")
        st.write(result['answers'])
        st.image(result['image'], use_container_width=True)
