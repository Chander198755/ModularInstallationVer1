import streamlit as st
import sys
import os

# 🔹 backend folder को path में जोड़ रहे हैं
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.firebase_init import init_firestore

st.title("Firestore Connection Test")

try:
    db = init_firestore()
    docs = db.collection("test").stream()   # change to real collection later
    st.success("🔥 Firestore Connected Successfully!")
    for doc in docs:
        st.write(doc.id, doc.to_dict())
except Exception as e:
    st.error(f"❌ Error connecting to Firebase: {e}")
