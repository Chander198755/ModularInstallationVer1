import streamlit as st

# -------------------------------
# Page Config MUST be first line
# -------------------------------
st.set_page_config(
    page_title="Modular Installation Dashboard",
    layout="wide"
)

# -------------------------------
# Firebase Initialization (Safe Position)
# -------------------------------
from backend.firebase_init import init_firestore

try:
    db = init_firestore()
    st.sidebar.success("🔥 Firebase Connected")
except Exception as e:
    st.sidebar.error(f"❌ Firebase Error: {e}")
    st.stop()  # Stop execution if Firebase fails

# -------------------------------
# Main Title
# -------------------------------
st.title("🔧 Modular Installation Dashboard")
st.write("Use the sidebar to navigate between modules.")

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.header("📂 Navigation")

page = st.sidebar.radio(
    "Select a page:",
    [
        "📤 Submit Request (OL)",
        "🛠️ Installation Manager",
        "➕ Add PID",
        "👷 Add Manager",
        "👥 Team Registration"
    ]
)

# -------------------------------
# Page Routing Logic
# -------------------------------
if page == "📤 Submit Request (OL)":
    st.switch_page("pages/1_ol_request.py")

elif page == "🛠️ Installation Manager":
    st.switch_page("pages/2_installation_manager.py")

elif page == "➕ Add PID":
    st.switch_page("pages/3_add_pid.py")

elif page == "👷 Add Manager":
    st.switch_page("pages/4_fix_installation_manager.py")

elif page == "👥 Team Registration":
    st.switch_page("pages/5_Team_Registration.py")
