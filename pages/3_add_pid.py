import streamlit as st
from backend.firebase_init import init_firestore

# --- Firestore ---
db = init_firestore()

st.title("➕ Add New Project (PID)")

# ===== SaaS LOGIN CONTEXT =====
company_id = st.session_state.get("company_id")
user_email = st.session_state.get("user_email")
user_role = st.session_state.get("user_role")

if not company_id or not user_email:
    st.error("Session expired. Please login again.")
    st.stop()

# Optional role restriction (recommended)
if user_role not in ["admin", "OL"]:
    st.error("Access denied. Only Admin / OL can add PID.")
    st.stop()

# --- State control ---
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if not st.session_state.form_submitted:
    with st.form("add_pid_form"):

        email = st.text_input(
            "Assigned To (OL Email)",
            value=user_email,
            help="Enter the email of the Operations Lead"
        )

        city = st.selectbox(
            "City",
            ["Okhla", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Other"]
        )

        project_id = st.text_input("Project ID (Numeric)")
        project_name = st.text_input("Project Name")
        address = st.text_area("Full Project Address")
        contact = st.text_input("Point of Contact (Phone/Name)")

        submitted = st.form_submit_button("Add PID")

        if submitted:
            if not (email and city and project_id and project_name and address and contact):
                st.error("Please fill all fields.")
            else:
                (
                    db.collection("companies")
                      .document(company_id)
                      .collection("PID")
                      .document(project_id)
                      .set({
                          "company_id": company_id,
                          "assigned_to": email.lower(),
                          "city_name": city,
                          "project_id": project_id,
                          "project_name": project_name,
                          "address": address,
                          "contact": contact,
                          "created_by": user_email,
                      })
                )

                st.session_state.form_submitted = True

# --- Success & Reset ---
if st.session_state.form_submitted:
    st.success("PID added successfully.")
    if st.button("➕ Add Another PID"):
        st.session_state.form_submitted = False
        st.rerun()
