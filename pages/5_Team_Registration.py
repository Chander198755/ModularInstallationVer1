import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="Team Registration", layout="wide")
st.markdown("## 🛠️ Team Registration Form")

# Fetch city data from Cities collection
city_docs = db.collection("Cities").stream()
city_map = {}
for doc in city_docs:
    data = doc.to_dict()
    city_map[data.get("Name")] = doc.id

if not city_map:
    st.warning("⚠️ No cities found in the Cities collection.")
    st.stop()

city_names = list(city_map.keys())

# Form UI
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
        selected_city = city_map[selected_city_display]

        # Validation for all non-inhouse fields
        if team_type != "In-house":
            if not all([team_name.strip(), vendor_code.strip(), contact_number.strip()]):
                st.error("❌ All fields are required for Vendor teams.")
                st.stop()
        
            # Prevent duplicate vendor code for same city
            duplicate_check = db.collection("Teams") \
                .where("city_id", "==", selected_city) \
                .where("vendor_code", "==", vendor_code.strip()) \
                .stream()
            if any(duplicate_check):
                st.error("❌ Vendor Code already registered for this city.")
                st.stop()

        else:
            # Allow only one in-house team per city
            existing = db.collection("Teams") \
                .where("city_id", "==", selected_city) \
                .where("team_type", "==", "In-house") \
                .stream()
            if any(existing):
                st.error("❌ An In-house team already exists for this city.")
                st.stop()

        team_data = {
            "city": selected_city_display,
            "city_id": selected_city,
            "team_type": team_type,
            "team_name": team_name,
            "vendor_code": vendor_code,
            "contact_number": contact_number,
            "status": status,
            "timestamp": datetime.now()
        }

        db.collection("Teams").add(team_data)
        st.success("✅ Team registered successfully.")

# --- Show registered teams for the selected city ---
st.markdown("---")
st.markdown(f"### 👥 Registered Teams in {selected_city_display}")

teams_query = db.collection("Teams") \
                .where("city_id", "==", city_map[selected_city_display]) \
                .stream()

teams = []
for team_doc in teams_query:
    team = team_doc.to_dict()
    teams.append({
        "Team Type": team.get("team_type", ""),
        "Team Name": team.get("team_name", ""),
        "Vendor Code": team.get("vendor_code", ""),
        "Contact No.": team.get("contact_number", ""),
        "Status": team.get("status", "")
    })

if teams:
    df_teams = pd.DataFrame(teams)
    st.dataframe(df_teams, use_container_width=True)
else:
    st.info("No teams registered yet for this city.")
