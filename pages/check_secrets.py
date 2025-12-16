import streamlit as st

st.title("🔐 Check Streamlit Secrets")

try:
    st.write("FIREBASE_PROJECT_ID:", st.secrets["firebase"]["project_id"])
    st.write("FIREBASE_CLIENT_EMAIL:", st.secrets["firebase"]["client_email"])

    if st.secrets["firebase"].get("private_key"):
        st.success("✅ Firebase Private Key FOUND!")
    else:
        st.error("❌ Firebase Private Key missing")

except Exception as e:
    st.error("❌ Firebase secrets not accessible")
    st.code(str(e))
