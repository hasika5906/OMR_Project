import streamlit as st
import os
import zipfile
import tempfile
from PIL import Image
import json
from omr_scanner import process_omr_image, load_answer_keys, grade_omr_image  # adjust your function names if needed

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="OMR Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Sidebar -----------------
st.sidebar.image("https://raw.githubusercontent.com/hasika5906/omr_project/main/omr_logo.png", use_container_width=True)
st.sidebar.title("OMR Scanner")
st.sidebar.markdown("""
**Upload your OMR sheets** as images (JPEG, PNG) or a ZIP of multiple images.<br>
Upload an **answer key JSON** if different from default Set A or Set B.
""", unsafe_allow_html=True)

# Select answer key
answer_key_set = st.sidebar.selectbox("Select Answer Key Set", ["A", "B"])
uploaded_key = st.sidebar.file_uploader("Upload Answer Key JSON (Optional)", type=["json"])

# ----------------- Load Answer Key -----------------
if uploaded_key:
    answer_key = json.load(uploaded_key)
else:
    default_path = os.path.join(os.path.dirname(__file__), f"answer_key_Set{answer_key_set}.json")
    if os.path.exists(default_path):
        with open(default_path, "r") as f:
            answer_key = json.load(f)
    else:
        st.error(f"Answer key file not found: {default_path}")
        st.stop()

# ----------------- Upload OMR Images -----------------
uploaded_files = st.file_uploader(
    "Upload OMR images or a ZIP of images",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True
)

if uploaded_files:
    images_to_process = []

    for file in uploaded_files:
        if file.name.endswith(".zip"):
            # Extract ZIP
            with tempfile.TemporaryDirectory() as tmpdirname:
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(tmpdirname)
                    for img_file in os.listdir(tmpdirname):
                        img_path = os.path.join(tmpdirname, img_file)
                        images_to_process.append(img_path)
        else:
            # Save uploaded image temporarily
            temp_file_path = os.path.join(tempfile.gettempdir(), file.name)
            with open(temp_file_path, "wb") as f:
                f.write(file.read())
            images_to_process.append(temp_file_path)

    st.success(f"Found {len(images_to_process)} image(s) for processing!")

    # ----------------- Process Images -----------------
    results = []
    for img_path in images_to_process:
        try:
            grade, feedback = grade_omr_image(img_path, answer_key)  # adjust function names
            results.append({"image": img_path, "score": grade, "feedback": feedback})
        except Exception as e:
            st.warning(f"Failed to process {img_path}: {e}")

    # ----------------- Display Results -----------------
    st.markdown("---")
    st.header("Results")
    for res in results:
        st.subheader(os.path.basename(res["image"]))
        img = Image.open(res["image"])
        st.image(img, use_container_width=True)
        st.markdown(f"**Score:** {res['score']}")
        st.markdown("**Feedback:**")
        st.json(res["feedback"])
