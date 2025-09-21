import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # ensure these exist

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="OMR Scanner", layout="wide")

# ---------------------- CUSTOM CSS ----------------------
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        .big-title {
            font-size: 42px;
            font-weight: bold;
            color: #00e6e6;
            text-align: center;
            margin-bottom: 20px;
        }
        .instructions {
            background: rgba(0, 0, 0, 0.6);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #00e6e6;
            margin-top: 20px;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #1f1c2c, #928dab);
        }
        .scrolling-text {
            font-size: 28px;
            font-weight: bold;
            color: #ffcc00;
            white-space: nowrap;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------- SESSION STATE ----------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ---------------------- SIGN-IN PAGE ----------------------
def login_page():
    st.markdown('<p class="big-title">🔐 Welcome to OMR Scanner</p>', unsafe_allow_html=True)

    # Logo
    st.image("assets/logo.png", width=180)

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login", type="primary"):
        if username == "admin" and password == "1234":  # replace with real creds
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")

    st.markdown(
        """
        <div class="instructions">
            <h4>ℹ️ Instructions</h4>
            <ul>
                <li>Use your username & password to sign in.</li>
                <li>After login, you can upload answer keys and OMR sheets.</li>
                <li>Contact support if login fails.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------- DASHBOARD ----------------------
def dashboard():
    st.sidebar.title("📌 Navigation")
    choice = st.sidebar.radio("Go to", ["📂 Upload & Process", "ℹ️ About", "📞 Contact"])

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # Logo & Banner
    st.image("assets/logo.png", width=160)
    st.markdown('<p class="big-title">📊 OMR Scanner Dashboard</p>', unsafe_allow_html=True)
    st.image("assets/banner.jpg", use_container_width=True)  # add a cool banner image

    # 🚩 Scrolling marquee text (large size)
    st.markdown(
        """
        <marquee behavior="scroll" direction="left" scrollamount="8">
            <span class="scrolling-text">📢 Welcome to OMR Scanner! Upload your OMR sheets and get results instantly 🚀</span>
        </marquee>
        """,
        unsafe_allow_html=True
    )

    if choice == "📂 Upload & Process":
        st.subheader("📂 Upload OMR Sheets")

        uploaded_files = st.file_uploader(
            "Upload OMR sheet images (JPEG, PNG) or ZIP of images",
            type=["jpg", "jpeg", "png", "zip"],
            accept_multiple_files=True
        )

        answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])

        if uploaded_files and answer_key_path:
            answer_key_file_path = os.path.join("temp", "answer_key.json")
            os.makedirs("temp", exist_ok=True)
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

            st.subheader("📊 Processing Results")
            for img_path in images_to_process:
                img_name = os.path.basename(img_path)
                result = process_omr_image(img_path, answer_key)

                st.write(f"**File:** {img_name}")
                st.write(f"**Score:** {result['score']} / 100")
                st.write("**Answers:**")
                st.json(result['answers'])
                st.image(result['image'], use_container_width=True)

    elif choice == "ℹ️ About":
        st.title("ℹ️ About OMR Scanner")
        st.markdown("""
        This is a smart **OMR Sheet Evaluation Tool** 🎯  
        Features:
        - Upload answer keys in JSON format.  
        - Upload scanned OMR sheets as images or ZIP.  
        - Get **instant results** with score and answers.  
        """)

    elif choice == "📞 Contact":
        st.title("📞 Contact Us")
        st.markdown("""
        - 📧 Email: support@omrscanner.com  
        - 🌐 Website: [www.omrscanner.com](https://www.omrscanner.com)  
        - ☎️ Phone: +91-1234567890  
        """)

# ---------------------- MAIN ----------------------
if not st.session_state["authenticated"]:
    login_page()
else:
    dashboard()
