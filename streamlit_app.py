# -*- coding: utf-8 -*-
import streamlit as st
import os
from omr_scanner import process_omr_folder  # Your scanner function
from PIL import Image

st.set_page_config(page_title="OMR Scanner", layout="centered")

st.title("OMR Scanner Web App")
st.write("""
Upload your OMR sheets here. 
Select the answer key set and get instant scores!
""")

# Sidebar for answer key selection
answer_set = st.sidebar.selectbox("Select Answer Key Set", ["SetA", "SetB"])

# File uploader
uploaded_files = st.file_uploader(
    "Upload OMR sheets (PNG/JPG)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Create a temporary folder to store uploaded images
    temp_folder = "uploaded_omr_sheets"
    os.makedirs(temp_folder, exist_ok=True)
    
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    st.info(f"Processing {len(file_paths)} OMR sheets with {answer_set} answer key...")
    
    # Call your scanner function
    try:
        results = process_omr_folder(file_paths, answer_set)
        
        st.success("Processing Complete!")
        
        # Display results
        for res in results:
            st.subheader(res["filename"])
            st.write(f"Score: {res['score']}/{res['total']}")
            st.table(res["details"])
            
    except Exception as e:
        st.error(f"Error processing OMR sheets: {e}")
