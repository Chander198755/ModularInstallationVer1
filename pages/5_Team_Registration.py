import streamlit as st
from datetime import datetime
import pandas as pd

from backend.firebase_init import init_firestore

# --- Firestore ---
db = init_firestore()

st.set_page_config(page_title="Team Registration", layout="wide")
st.markdown("## 🛠️ Team Registration Form")

# ===== SaaS LOGIN CONTEXT =====
company_id = st.session_state.get("company_id")
user_role = st.session_state.get("user_role")

if not company_id:
    st.error("Session expired. Please login again.")
    st.stop()

if user_role not in ["admin", "IM"]:
    st.error("Access denied.")
    st.stop()

# --- Fetch Cities (Company Scoped) ---
city_docs = (
    db.collection("companies")
      .document(company_id)
      .collection("Cities")
      .stream()
)

city_map = {}
for doc in city_docs:
    data = doc.to_dict()
    city_map[data.get("Name")] = doc.id

if not city_map:
    st.warning("⚠️ No cities found for this company.")
    st.stop()

city_names = list(city_map.keys())

# ======================
# TEAM REGISTRATION FORM
# ======================
with st.form("team_registration_form"):
    selected_city_display = st.selectbox("Select City", city_names)
    team_type = st.selectbox("Team Type", ["In-house", "Non_GST-Vendor", "Vendor (GST)"])

    if team_type == "In-house":
        team_name = "N/A"
        vendor_code = "N/A"
        contact_number = "N/A"
    else:
        team_name = st.text_input("Vendor Team Name")
        vendor_code = st.text_input("Vendor Code")
        contact_number = st.text_input("Contact Number")

    status = st.selectbox("Status", ["Active", "Inactive"])
    submit = st.form_submit_button("Register Team")

    if submit:
        selected_city_id = city_map[selected_city_display]

        # ---- Validation ----
        if team_type != "In-house":
            if not all([team_name.strip(), vendor_code.strip(), contact_number.strip()]):
                st.error("❌ All fields are required for Vendor teams.")
                st.stop()

            # Prevent duplicate vendor code (company + city level)
            duplicate_vendor = (
                db.collection("companies")
                  .document(company_id)
                  .collection("Teams")
                  .where("city_id", "==", selected_city_id)
                  .where("vendor_code", "==", vendor_code.strip())
                  .stream()
            )
            if any(duplicate_vendor):
                st.error("❌ Vendor Code already registered for this city.")
                st.stop()

        else:
            # Only one in-house team per city (per company)
            existing_inhouse = (
                db.collection("companies")
                  .document(company_id)
                  .collection("Teams")
                  .where("city_id", "==", selected_city_id)
                  .where("team_type", "==", "In-house")
                  .stream()
            )
            if any(existing_inhouse):
                st.error("❌ An In-house team already exists for this city.")
                st.stop()

        # ---- Save Data ----
        team_data = {
            "company_id": company_id,
            "city": selected_city_display,
            "city_id": selected_city_id,
            "team_type": team_type,
            "team_name": team_name,
            "vendor_code": vendor_code,
            "contact_number": contact_number,
            "status": status,
            "timestamp": datetime.now(),
        }

        (
            db.collection("companies")
              .document(company_id)
              .collection("Teams")
              .add(team_data)
        )

        st.success("✅ Team registered successfully.")

# ======================
# SHOW REGISTERED TEAMS
# ======================
st.markdown("---")
st.markdown(f"### 👥 Registered Teams in {selected_city_display}")

teams_query = (
    db.collection("companies")
      .document(company_id)
      .collection("Teams")
      .where("city_id", "==", city_map[selected_city_display])
      .stream()
)

teams = []
for team_doc in teams_query:
    team = team_doc.to_dict()
    teams.append({
        "Team Type": team.get("team_type", ""),
        "Team Name": team.get("team_name", ""),
        "Vendor Code": team.get("vendor_code", ""),
        "Contact No.": team.get("contact_number", ""),
        "Status": team.get("status", ""),
    })

if teams:
    df_teams = pd.DataFrame(teams)
    st.dataframe(df_teams, use_container_width=True)
else:
    st.info("No teams registered yet for this city.")
