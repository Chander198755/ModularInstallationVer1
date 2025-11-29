import streamlit as st

# -------------------------------
# 🔥 Firebase Initialization
# -------------------------------
from backend.firebase_init import init_firestore

try:
    db = init_firestore()
    st.success("🔥 Firebase Connected Successfully!")
except Exception as e:
    st.error(f"❌ Firebase Connection Failed: {e}")
    st.stop()

# -------------------------------
# 🧭 Page Config
# -------------------------------
st.set_page_config(
    page_title="Modular Installation Dashboard",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Modular Installation Dashboard")

# -------------------------------
# 📂 Sidebar Navigation
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
# 🔀 Page Routing
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
