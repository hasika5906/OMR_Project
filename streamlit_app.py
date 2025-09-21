import streamlit as st
import zipfile
import os
from PIL import Image
from omr_scanner import process_omr_image, load_answer_keys  # keep your logic intact

# ===============================
# Page Configuration
# ===============================
st.set_page_config(
    page_title="OMR Scanner Web App",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===============================
# Initialize Session State
# ===============================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ===============================
# CSS for Dark Gradient and Styling
# ===============================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .big-title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        color: #ffdd00;
    }
    .instructions {
        font-size: 18px;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f2027, #203a43);
        color: white;
    }
    .stButton>button {
        background-color: #ffdd00;
        color: black;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# LOGIN PAGE (Option A)
# ===============================
def login_page():
    st.markdown('<p class="big-title">🔐 Welcome to OMR Scanner (Prototype)</p>', unsafe_allow_html=True)

    # Logo (online placeholder)
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Check_green_icon.svg/768px-Check_green_icon.svg.png",
        width=120,
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login", type="primary"):
        # Accept any non-empty username/password
        if username.strip() != "" and password.strip() != "":
            st.session_state["authenticated"] = True
            st.success(f"Logged in as {username} (prototype mode)")
            st.experimental_rerun()
        else:
            st.error("Please enter a username and password (prototype mode accepts any non-empty values).")

    st.markdown(
        """
        <div class="instructions">
            <h4>ℹ️ Prototype Login Instructions</h4>
            <ul>
                <li>Enter any username and password to login.</li>
                <li>This is for demo/prototype only.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===============================
# MAIN APP PAGE
# ===============================
def main_app():
    st.markdown('<p class="big-title">📝 OMR Scanner Dashboard</p>', unsafe_allow_html=True)

    # Sidebar Menu
    menu = ["Upload & Process", "About", "Contact"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "About":
        st.markdown("## About This App")
        st.markdown(
            """
            This OMR Scanner Web App allows you to upload OMR sheets (JPEG, PNG, ZIP) and process them against an answer key.
            <br>Prototype demo with interactive dark UI and gradients.
            """
        )

    elif choice == "Contact":
        st.markdown("## Contact Us")
        st.markdown(
            """
            **Email:** support@example.com  
            **Phone:** +91-XXXXXXXXXX  
            **Address:** 123 Demo Street, Prototype City
            """
        )

    else:
        # ===============================
        # Upload Section
        # ===============================
        uploaded_files = st.file_uploader(
            "Upload OMR sheet images (JPEG, PNG) or ZIP of images",
            type=["jpg", "jpeg", "png", "zip"],
            accept_multiple_files=True,
        )

        answer_key_path = st.file_uploader("Upload Answer Key JSON", type=["json"])

        if uploaded_files and answer_key_path:
            # Save uploaded answer key
            os.makedirs("temp", exist_ok=True)
            answer_key_file_path = os.path.join("temp", "answer_key.json")
            with open(answer_key_file_path, "wb") as f:
                f.write(answer_key_path.getbuffer())

            # Load answer key
            answer_key = load_answer_keys(answer_key_file_path)

            # Prepare images to process
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

            # Display Results
            st.subheader("📊 Processing Results")
            for img_path in images_to_process:
                img_name = os.path.basename(img_path)
                result = process_omr_image(img_path, answer_key)  # your existing function
                st.markdown(f"### File: {img_name}")
                st.markdown(f"**Score:** {result['score']} / 100")
                st.markdown("**Answers:**")
                st.write(result['answers'])
                st.image(result['image'], use_container_width=True)

# ===============================
# App Execution
# ===============================
if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
