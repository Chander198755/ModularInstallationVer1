import streamlit as st

# -------------------------------
# 🧭 Page Config
# -------------------------------
st.set_page_config(
    page_title="Modular Installation Dashboard",
    page_icon="🔧",
    layout="wide"
)

# -------------------------------
# 🔐 Login Enforcement
# -------------------------------
company_id = st.session_state.get("company_id")
user_role = st.session_state.get("user_role")
user_email = st.session_state.get("user_email")

if not company_id or not user_email:
    st.error("Please login to continue.")
    st.stop()

# -------------------------------
# 🏷️ Header
# -------------------------------
st.title("🔧 Modular Installation Dashboard")
st.caption(f"Company: {company_id} | User: {user_email} | Role: {user_role}")

# -------------------------------
# 📂 Sidebar Navigation (Role Based)
# -------------------------------
st.sidebar.header("📂 Navigation")

menu_options = []

# OL
if user_role in ["OL", "Admin", "SuperAdmin"]:
    menu_options.append("📤 Submit Request (OL)")

# Installation Manager
if user_role in ["IM", "InstallationManager", "Admin", "SuperAdmin"]:
    menu_options.append("🛠️ Installation Manager")

# Admin / SuperAdmin
if user_role in ["Admin", "SuperAdmin"]:
    menu_options.append("➕ Add PID")
    menu_options.append("👥 Team Registration")

# SuperAdmin only
if user_role == "SuperAdmin":
    menu_options.append("👥 User Management")

page = st.sidebar.radio("Select a page:", menu_options)

# -------------------------------
# 🔀 Page Routing
# -------------------------------
if page == "📤 Submit Request (OL)":
    st.switch_page("pages/1_ol_request.py")

elif page == "🛠️ Installation Manager":
    st.switch_page("pages/2_installation_manager.py")

elif page == "➕ Add PID":
    st.switch_page("pages/3_add_pid.py")

elif page == "👥 Team Registration":
    st.switch_page("pages/5_Team_Registration.py")

elif page == "👥 User Management":
    st.switch_page("pages/user_management.py")
