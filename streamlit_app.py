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
    </style>
""", unsafe_allow_html=True)

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
        # Change credentials here
        if username == "user" and password == "test123":
            st.session_state.logged_in = True
            st.success("✅ Login successful! Welcome to OMR Scanner.")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")
else:
    # ---------------------- DASHBOARD ----------------------
    menu = ["🏠 Dashboard", "📤 Upload OMR", "📜 Instructions", "ℹ️ About", "📞 Contact"]
    choice = st.sidebar.radio("📌 Navigate", menu)

    st.sidebar.markdown("---")
    st.sidebar.info("Logged in as **User**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # ---------------------- DASHBOARD PAGE ----------------------
    if choice == "🏠 Dashboard":
        st.subheader("📊 Welcome to the OMR Scanner Dashboard")
        st.markdown("""
        ✅ Upload your answer sheets.  
        ✅ Instantly process and view scores.  
        ✅ Explore instructions, about, and contact sections using the menu.  
        """)

    # ---------------------- UPLOAD PAGE ----------------------
    elif choice == "📤 Upload OMR":
        st.subheader("📤 Upload OMR Sheets")
        st.info("Upload OMR images (JPG, PNG, ZIP) and the Answer Key JSON to begin.")
        # (Upload logic here — keep your existing working code)

    # ---------------------- INSTRUCTIONS PAGE ----------------------
    elif choice == "📜 Instructions":
        st.subheader("📜 Instructions")
        st.markdown("""
        1️⃣ Login with your credentials.  
        2️⃣ Upload **OMR sheet images**.  
        3️⃣ Upload the **Answer Key JSON** file.  
        4️⃣ Get instant scores + visual feedback.  
        """)

    # ---------------------- ABOUT PAGE ----------------------
    elif choice == "ℹ️ About":
        st.subheader("ℹ️ About This Project")
        st.markdown("""
        - **OMR Scanner** is an AI-powered web app to evaluate answer sheets.  
        - Built using **Python, OpenCV, Streamlit**.  
        - Developed for educational and exam purposes.  
        """)

    # ---------------------- CONTACT PAGE ----------------------
    elif choice == "📞 Contact":
        st.subheader("📞 Contact Us")
        st.markdown("""
        ✉️ Email: support@omrscanner.ai  
        🌐 Website: [GitHub Repo](https://github.com/)  
        📍 Location: India  
        """)
