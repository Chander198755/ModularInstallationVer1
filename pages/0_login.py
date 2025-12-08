import streamlit as st
from backend.firebase_init import init_firestore

st.set_page_config(page_title="Login", layout="centered")
db = init_firestore()

# --- SESSION INITIALIZATION ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None


# --- VALIDATE USER FUNCTION ---
def validate_user(email, password):
    email = email.strip().lower()  # Normalize email

    users = db.collection("Users").where("email", "==", email).stream()
    user = None
    for u in users:
        user = u.to_dict()

    if not user:
        return None, "⚠ User not found!"

    if not user.get("active", False):
        return None, "❌ Account disabled. Contact Admin!"

    # Compare password exactly
    if user.get("password") != password:
        return None, "❌ Incorrect password!"

    return user, None


# --- IF ALREADY LOGGED IN -> REDIRECT ---
if st.session_state.is_logged_in:
    st.success(f"Welcome back {st.session_state.user_info['name']} 👋")
    st.switch_page("dashboard.py")


# --- LOGIN FORM UI ---
st.title("🔐 Modular Installation Portal Login")
st.write("Enter your email & password to continue")

email = st.text_input("Email").strip()
password = st.text_input("Password", type="password")

if st.button("Login", type="primary"):
    if not email or not password:
        st.warning("⚠ Please enter both email and password")
    else:
        user, error = validate_user(email, password)

        if error:
            st.error(error)
        elif user:
            st.session_state.is_logged_in = True
            st.session_state.user_info = user
            st.success("🎯 Login Successful! Redirecting...")
            st.experimental_rerun()
