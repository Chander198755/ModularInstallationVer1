import streamlit as st

# Page settings (Recommended)
st.set_page_config(
    page_title="Modular Installation Dashboard",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Modular Installation Project")
st.subheader("🚀 Welcome to your Streamlit Dashboard")

st.write("""
Left sidebar se pages ko navigate karein.  
You are now ready to connect Firebase & test your data!  
""")

st.info("Use: `Pages → test_firebase.py` to check Firestore connection.")
