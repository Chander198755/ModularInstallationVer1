import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from backend.firebase_init import init_firestore
import traceback

st.title("🔥 Firestore Connection Test")

try:
    st.write("⏳ Connecting to Firebase...")
    db = init_firestore()
    st.success("🎉 Successfully connected to Firestore!")

    st.write("🔍 Fetching sample data...")
    docs = db.collection("PID").limit(3).stream()

    for doc in docs:
        st.write(doc.id, doc.to_dict())

except Exception as e:
    st.error(f"❌ Error found: {e}")
    st.code(traceback.format_exc())
