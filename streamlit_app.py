import streamlit as st
from PIL import Image
from omr_scanner import load_answer_keys, process_omr_image
import zipfile
import os

st.set_page_config(
    page_title="OMR Scanner 🎨",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gradient background
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f0f8ff, #e6e6fa);
    }
    .stButton>button {
        background-color: #FF4B4B; 
        color: white; 
        border-radius:10px; 
        font-weight:bold;
    }
    .stTabs [role='tab'] {font-weight:bold; color:#4B0082;}
    h1, h2, h3, h4, h5, h6 {color:#FF8C00;}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.title("OMR Scanner 🌈")
st.sidebar.markdown(
    """
    Upload OMR sheets (JPEG/PNG) or a ZIP folder containing multiple images.
    Select the answer key set and click 'Process'.
    """
)

answer_key_set = st.sidebar.selectbox("Select Answer Key", ["SetA", "SetB"])
answer_key_path = f"answer_key_{answer_key_set}.json"
answer_key = load_answer_keys(answer_key_path)

# Tabs
tab1, tab2 = st.tabs(["Single Image Upload 🖼️", "Batch Upload (ZIP) 📦"])

# ------------------- Single Image -------------------
with tab1:
    st.header("Single Image Grading")
    uploaded_file = st.file_uploader("Upload a single OMR sheet", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded OMR Sheet", use_container_width=True)
        
        if st.button("Grade Image", key="single"):
            with st.spinner("Grading OMR sheet..."):
                result = process_omr_image(uploaded_file, answer_key, highlight=True)
                st.success(f"Score: {result['score']}/100 🎯")
                st.image(result["image"], caption="Graded OMR Sheet", use_container_width=True)
                st.subheader("Answers Overview")
                st.json(result["answers"])

# ------------------- Batch Upload -------------------
with tab2:
    st.header("Batch Grading")
    uploaded_zip = st.file_uploader("Upload ZIP of OMR sheets", type=["zip"])
    
    if uploaded_zip:
        with zipfile.ZipFile(uploaded_zip) as zf:
            filenames = [name for name in zf.namelist() if name.lower().endswith(('.png', '.jpg', '.jpeg'))]
            st.info(f"{len(filenames)} OMR sheets found in ZIP.")
            
            if st.button("Grade All Images", key="batch"):
                os.makedirs("temp_omr", exist_ok=True)
                res
