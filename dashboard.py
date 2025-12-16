import streamlit as st

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Modular Installation Dashboard",
    layout="wide"
)

# ---------------------------------
# Login + SaaS Context (MANDATORY)
# ---------------------------------
logged_in = st.session_state.get("logged_in")
company_id = st.session_state.get("company_id")
user_email = st.session_state.get("user_email")
user_role = st.session_state.get("user_role")

if not logged_in or not company_id or not user_email:
    st.switch_page("pages/0_login.py")
    st.stop()

# ---------------------------------
# Sidebar Header
# ---------------------------------
st.sidebar.success(f"Welcome: {user_email}")
st.sidebar.write(f"Company: **{company_id}**")
st.sidebar.write(f"Role: **{user_role}**")

# ---------------------------------
# Logout
# ---------------------------------
def logout():
    for key in [
        "logged_in",
        "company_id",
        "user_email",
        "user_role",
        "user_cities",
    ]:
        st.session_state.pop(key, None)
    st.rerun()

st.sidebar.button("🚪 Logout", on_click=logout)

# ---------------------------------
# Role-based Navigation
# ---------------------------------
st.sidebar.header("📂 Navigation")
menu = []

if user_role == "SuperAdmin":
    menu += [
        "📤 Submit Request (OL)",
        "🛠️ Installation Manager",
        "➕ Add PID",
        "👥 Team Registration",
        "🔐 User Management",
    ]

elif user_role == "Admin":
    menu += [
        "📤 Submit Request (OL)",
        "🛠️ Installation Manager",
        "➕ Add PID",
        "👥 Team Registration",
    ]

elif user_role in ["InstallationManager", "IM"]:
    menu += ["🛠️ Installation Manager"]

elif user_role == "OL":
    menu += ["📤 Submit Request (OL)"]

else:
    st.error("🚫 Access blocked.")
    st.stop()

choice = st.sidebar.radio("Select page", menu)

# ---------------------------------
# Page Routing
# ---------------------------------
if choice == "📤 Submit Request (OL)":
    st.switch_page("pages/1_ol_request.py")

elif choice == "🛠️ Installation Manager":
    st.switch_page("pages/2_installation_manager.py")

elif choice == "➕ Add PID":
    st.switch_page("pages/3_add_pid.py")

elif choice == "👥 Team Registration":
    st.switch_page("pages/5_Team_Registration.py")

elif choice == "🔐 User Management":
    st.switch_page("pages/6_user_management.py")
