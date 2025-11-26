import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("➕ Add New Project (PID)")

# Control flow with session state
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if not st.session_state.form_submitted:
    with st.form("add_pid_form"):
        email = st.text_input("Assigned To (OL Email)", help="Enter the email of the Operations Lead")
        city = st.selectbox("City", ["Okhla", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Other"])
        project_id = st.text_input("Project ID (Numeric)")
        project_name = st.text_input("Project Name")
        address = st.text_area("Full Project Address")
        contact = st.text_input("Point of Contact (Phone/Name)")

        submitted = st.form_submit_button("Add PID")

        if submitted:
            if not (email and city and project_id and project_name and address and contact):
                st.error("Please fill all fields.")
            else:
                db.collection("PID").document(project_id).set({
                    "assigned_to": email.lower(),
                    "city_name": city,
                    "project_id": project_id,
                    "project_name": project_name,
                    "address": address,
                    "contact": contact
                })
                st.session_state.form_submitted = True

# Success message and reset option
if st.session_state.form_submitted:
    st.success("PID added successfully.")
    if st.button("➕ Add Another PID"):
        st.session_state.form_submitted = False
        st.rerun()
