import streamlit as st

st.set_page_config(page_title="Modular Installation Dashboard", layout="wide")

st.title("🔧 Modular Installation Dashboard")

st.sidebar.header("📂 Navigation")
st.sidebar.page_link("pages/1_ol_request.py", label="📤 Submit Request (OL)", icon="📝")
st.sidebar.page_link("pages/2_installation_manager.py", label="🛠️ Installation Manager", icon="📋")
st.sidebar.page_link("pages/3_add_pid.py", label="➕ Add PID", icon="🏗️")
st.sidebar.page_link("pages/4_fix_installation_manager.py", label="👷 Add Manager", icon="➕")
st.sidebar.page_link("pages/5_Team_Registration.py", label="👥 Team Registration", icon="📝")
