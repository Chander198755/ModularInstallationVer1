import streamlit as st
from backend.firebase_init import init_firestore
import hashlib

# Page Config
st.set_page_config(
    page_title="Modular Installation Dashboard",
    layout="wide"
)

# Firebase
db = init_firestore()

# ⭐ Force Login Redirect
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/0_login.py")

# Session State Defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_cities" not in st.session_state:
    st.session_state.user_cities = []

# Login Function
def login_user(email, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    doc = db.collection("Users").document(email).get()

    if doc.exists:
        data = doc.to_dict()
        if data.get("password") == hashed and data.get("active", False):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.user_role = data.get("role")
            st.session_state.user_cities = data.get("cities", [])
            return True
    return False

# Logout Function
def logout():
    for key in ["logged_in", "user_email", "user_role", "user_cities"]:
        st.session_state[key] = None
    st.session_state.logged_in = False
    st.rerun()

# LOGIN SCREEN (when redirected)
if not st.session_state.logged_in:
    st.title("🔐 Login Access")
    st.write("Enter your credentials")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(email, password):
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid email or password!")
    st.stop()

# After Successful Login
st.sidebar.success(f"Welcome: {st.session_state.user_email}")
st.sidebar.write(f"Role: **{st.session_state.user_role}**")
st.sidebar.button("🚪 Logout", on_click=logout)

# Navigation based on role
st.sidebar.header("📂 Navigation")
role = st.session_state.user_role
menu = []

if role in ["SuperAdmin", "Admin"]:
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
    st.error("🚫 Access blocked."); st.stop()

choice = st.sidebar.radio("Select page", menu)

# Page Routing
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
