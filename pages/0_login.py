import streamlit as st
from backend.firebase_init import init_firestore

st.set_page_config(page_title="Login", layout="centered")

db = init_firestore()

st.title("🔐 Login Access")
st.write("Enter your credentials")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        doc_ref = db.collection("Users").document(email)
        doc = doc_ref.get()

        if doc.exists:
            user = doc.to_dict()

            # Fix password match
            stored_pass = str(user.get("password", "")).replace('"', "").strip()

            if stored_pass == password and user.get("active", False):
                # Save Login State
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.session_state.user_role = user["role"]
                st.session_state.user_cities = user["cities"]
                st.success("Login successful! 🚀")
                st.rerun()
            else:
                st.error("Invalid email or password!")
        else:
            st.error("User not found!")

    except Exception as e:
        st.error(f"Error: {e}")
