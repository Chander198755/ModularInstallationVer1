import streamlit as st
import os

st.title("🔐 Check Streamlit Secrets")

st.write("FIREBASE_PROJECT_ID:", os.getenv("FIREBASE_PROJECT_ID"))
st.write("FIREBASE_CLIENT_EMAIL:", os.getenv("FIREBASE_CLIENT_EMAIL"))

if not os.getenv("FIREBASE_PRIVATE_KEY"):
    st.error("❌ Firebase Private Key not found in secrets")
else:
    st.success("✅ Firebase Private Key FOUND!")
