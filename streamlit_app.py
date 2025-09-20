import streamlit as st
import os
import tempfile
from omr_scanner import process_omr_folder, load_answer_keys
import cv2

st.set_page_config(page_title="OMR Scanner", layout="wide")
st.title("📄 OMR Scanner Web App")

# Upload OMR Images
omr_images = st.file_uploader(
    "Upload OMR Images (PNG, JPG, JPEG)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)
answer_json = st.file_uploader("Upload Answer Key JSON", type=["json"])

if omr_images and answer_json:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save images
        image_paths = []
        for img_file in omr_images:
            img_path = os.path.join(tmpdir, img_file.name)
            with open(img_path, "wb") as f:
                f.write(img_file.getbuffer())
            image_paths.append(img_path)

        # Save JSON
        answer_key_path = os.path.join(tmpdir, "answer_key.json")
        with open(answer_key_path, "wb") as f:
            f.write(answer_json.getbuffer())

        # Load answer key
        answer_key = load_answer_keys(answer_key_path)

        st.info("Processing images...")
        results = process_omr_folder(tmpdir, answer_key_path)

        st.success("✅ Grading Complete!")
        st.write("### Scores:")
        st.table(results)

        # Show each image with detected bubbles
        for img_path in image_paths:
            img_name = os.path.basename(img_path)
            img = cv2.imread(img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            bubble_contours = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = w / float(h)
                if 15 < w < 50 and 0.8 < aspect_ratio < 1.2:
                    bubble_contours.append(cnt)

            bubble_contours = sorted(bubble_contours, key=lambda c: cv2.boundingRect(c)[1])

            # Draw bubbles on image
            for cnt in bubble_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            st.write(f"#### {img_name}")
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_column_width=True)
