import streamlit as st
from backend.firebase_init import init_firestore

db = init_firestore()

st.title("🔐 Login Access")
st.write("Enter your credentials")

email_input = st.text_input("Email")
password_input = st.text_input("Password", type="password")

if st.button("Login"):
    email = email_input.strip().lower()
    password = password_input.strip()

    user_found = False

    # 🔑 SaaS: iterate companies, then users
    companies_ref = db.collection("companies").stream()

    for company_doc in companies_ref:
        company_id = company_doc.id

        users_ref = (
            db.collection("companies")
              .document(company_id)
              .collection("Users")
              .stream()
        )

        for doc in users_ref:
            user = doc.to_dict()

            if (
                user.get("email", "").strip().lower() == email
                and user.get("password", "") == password
            ):
                # ✅ Login success
                st.session_state.logged_in = True
                st.session_state.company_id = company_id
                st.session_state.user_email = user.get("email")
                st.session_state.user_role = user.get("role", "OL")
                st.session_state.user_cities = user.get("cities", ["ALL"])

                user_found = True
                st.success(f"Welcome {user.get('name', '')} ({company_id})")
                st.switch_page("dashboard.py")
                break

        if user_found:
            break

    if not user_found:
        st.error("Invalid email or password!")
