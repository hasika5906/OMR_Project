# streamlit_app.py
import streamlit as st
from omr_scanner import process_omr_folder
import os

st.set_page_config(page_title="OMR Scanner", layout="centered")

st.title("OMR Scanner Web App")
st.write("Upload a folder of OMR sheets and get instant scores!")

# Upload answer key
answer_key_file = st.file_uploader("Upload Answer Key JSON", type="json")

# Upload OMR images folder as a zip
omr_zip = st.file_uploader("Upload OMR Sheets (ZIP)", type="zip")

if st.button("Process OMR Sheets"):
    if answer_key_file is None or omr_zip is None:
        st.warning("Please upload both answer key and OMR sheets ZIP.")
    else:
        import zipfile
        import tempfile

        # Save uploaded files to temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_key_path = os.path.join(tmpdir, "answer_key.json")
            with open(answer_key_path, "wb") as f:
                f.write(answer_key_file.read())

            # Extract ZIP
            omr_folder_path = os.path.join(tmpdir, "OMR_Images")
            os.makedirs(omr_folder_path, exist_ok=True)
            with zipfile.ZipFile(omr_zip, "r") as zip_ref:
                zip_ref.extractall(omr_folder_path)

            # Process all images
            st.info("Processing OMR sheets, please wait...")
            results = process_omr_folder(omr_folder_path, answer_key_path)

            if results:
                st.success("Processing Complete!")
                st.write("### Results")
                for file, score in results.items():
                    st.write(f"**{file}** : {score}")
            else:
                st.error("No images found or failed to process.")
