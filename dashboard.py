import streamlit as st
from backend.firebase_init import init_firestore
import hashlib

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Modular Installation Dashboard",
    layout="wide"
)

# ---------------------------------
# Firebase
# ---------------------------------
db = init_firestore()

# ---------------------------------
# Login Redirect (Mandatory)
# ---------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/0_login.py")

# ---------------------------------
# Sidebar Header After Login
# ---------------------------------
st.sidebar.success(f"Welcome: {st.session_state.user_email}")
st.sidebar.write(f"Role: **{st.session_state.user_role}**")


# ---------------------------------
# Logout Button
# ---------------------------------
def logout():
    for key in ["logged_in", "user_email", "user_role", "user_cities"]:
        st.session_state[key] = None
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.button("🚪 Logout", on_click=logout)


# ---------------------------------
# Role-based Navigation
# ---------------------------------
st.sidebar.header("📂 Navigation")
role = st.session_state.user_role
menu = []

if role == "SuperAdmin":
    menu += [
        "📤 Submit Request (OL)",
        "🛠️ Installation Manager",
        "➕ Add PID",
        "👷 Add Manager",
        "👥 Team Registration",
        "🔐 User Management",  # NEW
    ]

elif role == "Admin":
    menu += [
        "📤 Submit Request (OL)",
        "🛠️ Installation Manager",
        "➕ Add PID",
        "👷 Add Manager",
        "👥 Team Registration",
    ]

elif role == "InstallationManager":
    menu += ["🛠️ Installation Manager"]

elif role == "OL":
    menu += ["📤 Submit Request (OL)"]

else:
    st.error("🚫 Access blocked.")
    st.stop()


choice = st.sidebar.radio("Select page", menu)


# ---------------------------------
# Page Routing
# ---------------------------------
if choice == "📤 Submit Request (OL)":
    st.switch_page("pages/1_ol_request.py")

elif choice == "🛠️ Installation Manager":
    st.switch_page("pages/2_installation_manager.py")

elif choice == "➕ Add PID":
    st.switch_page("pages/3_add_pid.py")

elif choice == "👷 Add Manager":
    st.switch_page("pages/4_fix_installation_manager.py")

elif choice == "👥 Team Registration":
    st.switch_page("pages/5_Team_Registration.py")

elif choice == "🔐 User Management":       # NEW 🚀
    st.switch_page("pages/6_user_management.py")
