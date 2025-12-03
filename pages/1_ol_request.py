import streamlit as st
from datetime import datetime, timedelta
from backend.firebase_init import init_firestore

db = init_firestore()

st.title("Operations Lead - Request Form")

# Reset flag
if "submitted_once" not in st.session_state:
    st.session_state.submitted_once = False

# ---------------------------
# PROJECT SELECTION (NO LOGIN)
# ---------------------------

# Fetch all PIDs (public access)
docs = db.collection("PID").stream()
project_list = []

for doc in docs:
    data = doc.to_dict()
    project_list.append({
        "display": f"{data.get('project_name', 'Unknown')} (PID: {data.get('project_id', 'N/A')})",
        "pid": data.get("project_id", "N/A"),
        "project_name": data.get("project_name", "Unknown"),
        "city": data.get("city_name", "Unknown City"),
        "address": data.get("address", "Unknown Address")
    })

project_names = ["Select..."] + [item["display"] for item in project_list]
selected_project = st.selectbox("Select Project", project_names)

selected_data = next((i for i in project_list if i["display"] == selected_project), None)

if selected_data and selected_project != "Select...":

    st.markdown(f"**City:** {selected_data['city']}")
    st.markdown(f"**Address:** {selected_data['address']}")

    team_qty = st.selectbox("Team Quantity", ["Select...", 1, 2, 3, 4, 5])
    pref_time = st.selectbox("Preferred Time", ["Select...", "1st Half", "2nd Half", "Full Day"])
    task_type = st.selectbox("Team Required For", [
        "Select...", "Fresh Installation", "WIP", "SNAG", "Alignment", "Additional order",
        "Shifting", "Post sales", "F&D Installation"
    ])

    min_date = datetime.now().date() + timedelta(days=1)
    preferred_date = st.date_input("Preferred Date", value=min_date, min_value=min_date)

    job_description = st.text_area("Job Description")
    categories = ["Kitchen", "Wardrobe", "Storage", "F&D", "Metal Kitchen"]
    selected_categories = st.multiselect("Select Categories", categories)

    if st.button("Submit Request"):

        if all([team_qty != "Select...", pref_time != "Select...", task_type != "Select..."]):

            # Generate Request Number
            fy_code = f"{datetime.now().year % 100}/{(datetime.now().year + 1) % 100}"
            city_code = selected_data["city"][:3].upper()

            existing_reqs = db.collection("Requests").where("city", "==", selected_data["city"]).stream()
            req_count = sum(1 for _ in existing_reqs) + 1

            request_number = f"{city_code}-{req_count:03d}-{fy_code}"

            # Store request
            db.collection("Requests").add({
                "submitted_by": "OL",
                "project_id": selected_data["pid"],
                "project_name": selected_data["project_name"],
                "city": selected_data["city"],
                "address": selected_data["address"],
                "team_qty": team_qty,
                "preferred_time": pref_time,
                "task_type": task_type,
                "preferred_date": preferred_date.strftime("%Y-%m-%d"),
                "request_number": request_number,
                "job_description": job_description,
                "categories": selected_categories,
                "timestamp": datetime.now()
            })

            st.success("✅ Request Submitted Successfully!")

            # Reset page immediately
            st.session_state.submitted_once = True
            st.rerun()

        else:
            st.warning("⚠️ Please fill all fields before submitting.")

# Refresh page after submit
if st.session_state.submitted_once:
    st.session_state.submitted_once = False
    st.rerun()
