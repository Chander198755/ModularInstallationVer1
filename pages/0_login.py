import streamlit as st
from backend.firebase_init import init_firestore

db = init_firestore()

st.title("🔐 Login Access")
st.write("Enter your credentials")

email_input = st.text_input("Email")
password_input = st.text_input("Password", type="password")

if st.button("Login"):
    email = email_input.strip().lower()
    password = password_input.strip()

    users_ref = db.collection("Users").stream()
    user_found = False

    for doc in users_ref:
        user = doc.to_dict()
        if user.get("email", "").strip().lower() == email and user.get("password", "") == password:
            st.session_state.logged_in = True
            st.session_state.user_email = user["email"]
            st.session_state.user_role = user.get("role", "OL")
            st.session_state.user_cities = user.get("cities", ["ALL"])
            user_found = True
            st.success(f"Welcome back {user.get('name', '')}!")
            st.switch_page("dashboard.py")
            break

    if not user_found:
        st.error("Invalid email or password!")
