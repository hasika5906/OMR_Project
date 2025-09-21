import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # logic unchanged

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="OMR Scanner Web App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
    <style>
        body { background-color: #000000; color: #FFFFFF; }
        .stApp { background-color: #000000; }
        h1, h2, h3, h4, h5, h6 { color: #00FFAA !important; }
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
        .scroll-text {
            color: #FFAA00;
            font-weight: bold;
            animation: scroll-left 15s linear infinite;
            white-space: nowrap;
            overflow: hidden;
        }
        @keyframes scroll-left {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .progress-container {
            width: 100%;
            background-color: #333;
            border-radius: 8px;
            margin: 10px 0;
        }
        .progress-bar {
            height: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- APP LOGO ----------------------
st.markdown("<h1 style='text-align:center;'>📝 OMR Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p class='scroll-text'>Welcome to the OMR Scanner App - Fast • Accurate • Interactive</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------- LOGIN PAGE ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔐 Sign In to Continue")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.success("✅ Login successful! Welcome to OMR Scanner.")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")
else:
    # ---------------------- DASHBOARD ----------------------
    menu = ["📤 Upload OMR", "📜 Instructions", "ℹ️ About", "📞 Contact"]
    choice = st.sidebar.radio("📌 Navigate", menu)

    st.sidebar.markdown("---")
    st.sidebar.info("Logged in as **Admin**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # ---------------------- UPLOAD PAGE ----------------------
    if choice == "📤 Upload OMR":
        st.subheader("📤 Upload OMR Sheets")
        uploaded_files = st.file_uploader(
            "Upload OMR sheet images (JPEG, PNG) or ZIP of images",
            type=["jpg", "jpeg", "png", "zip"],
            accept_multiple_files=True
        )
        answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])

        if uploaded_files and answer_key_path:
            os.makedirs("temp", exist_ok=True)
            answer_key_file_path = os.path.join("temp", "answer_key.json")
            with open(answer_key_file_path, "wb") as f:
                f.write(answer_key_path.getbuffer())
            answer_key = load_answer_keys(answer_key_file_path)

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

            st.markdown("## 🚀 Processing Results")
            for img_path in images_to_process:
                img_name = os.path.basename(img_path)
                result = process_omr_image(img_path, answer_key)

                score = result['score']
                percentage = (score / 100) * 100

                # Choose bar color
                if percentage >= 75:
                    bar_color = "#00FF00"  # Green
                elif percentage >= 50:
                    bar_color = "#FFA500"  # Orange
                else:
                    bar_color = "#FF3333"  # Red

                st.markdown(
                    f"""
                    <div class='result-card'>
                        <h3>📄 File: {img_name}</h3>
                        <h4 style='color:#FFAA00;'>🏆 Score: {score} / 100</h4>
                        <div class="progress-container">
                            <div class="progress-bar" style="width:{percentage}%; background-color:{bar_color};">
                                {int(percentage)}%
                            </div>
                        </div>
                        <div class='answers-box'>{result['answers']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.image(result['image'], use_container_width=True)

        else:
            st.info("⬆️ Please upload OMR sheets and an Answer Key JSON to start processing.")

    # ---------------------- INSTRUCTIONS PAGE ----------------------
    elif choice == "📜 Instructions":
        st.subheader("📜 Instructions for Using OMR Scanner")
        st.markdown("""
        1️⃣ Login with valid credentials.  
        2️⃣ Upload your **OMR sheet images (JPEG, PNG, or ZIP)**.  
        3️⃣ Upload the **Answer Key JSON** file.  
        4️⃣ Wait for the results to be processed.  
        5️⃣ View your score and answers visually on screen.  
        """)

    # ---------------------- ABOUT PAGE ----------------------
    elif choice == "ℹ️ About":
        st.subheader("ℹ️ About This Project")
        st.markdown("""
        - **OMR Scanner** is an AI-powered tool for evaluating answer sheets.  
        - Built with **Python + OpenCV + Streamlit**.  
        - Designed for educators, institutes, and competitive exams.  
        """)

    # ---------------------- CONTACT PAGE ----------------------
    elif choice == "📞 Contact":
        st.subheader("📞 Contact Us")
        st.markdown("""
        ✉️ Email: support@omrscanner.ai  
        🌐 Website: [OMR Scanner](https://github.com/)  
        📍 Location: India  
        """)
