import streamlit as st
from datetime import datetime, timedelta
from backend.firebase_init import init_firestore

db = init_firestore()

st.set_page_config(layout="wide")

# ------------------------ CUSTOM CSS FOR UI STYLING ------------------------
st.markdown("""
    <style>
        .main-card {
            background-color: #ffffff;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            width: 70%;
            margin-left: auto;
            margin-right: auto;
        }

        .title-center {
            text-align: center;
            font-size: 32px !important;
            font-weight: 600 !important;
            padding-bottom: 20px;
        }

        label {
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border: 1px solid #D3D3D3 !important;
            padding: 6px !important;
        }

        textarea, input {
            border-radius: 8px !important;
            border: 1px solid #D3D3D3 !important;
        }

        .btn-submit {
            background-color: #273c75;
            color: white;
            border-radius: 8px;
            font-size: 18px;
            padding: 10px 30px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------ TITLE ------------------------
st.markdown('<h2 class="title-center">Operations Lead - Request Form</h2>', unsafe_allow_html=True)

# Container for the entire form
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ------------------------ LOAD ALL PIDs ------------------------
    pids = db.collection("PID").stream()
    pid_list = []

    for doc in pids:
        data = doc.to_dict()
        pid_list.append({
            "display": f"{data.get('project_name', 'Unknown')}  |  PID: {data.get('project_id', 'N/A')}",
            "pid": data.get("project_id"),
            "project_name": data.get("project_name", "Unknown"),
            "city": data.get("city_name", "Unknown"),
            "address": data.get("address", "Unknown")
        })

    project_names = ["Select..."] + [item["display"] for item in pid_list]
    selected_project = st.selectbox("Select Project (PID)", project_names)

    selected_data = next((item for item in pid_list if item["display"] == selected_project), None)

    # ------------------------ SHOW PROJECT DETAILS ------------------------
    if selected_data and selected_project != "Select...":
        st.markdown(f"### 📍 **City:** {selected_data['city']}")
        st.markdown(f"### 🏠 **Address:** {selected_data['address']}")

        # ------------------------ FORM ------------------------
        team_qty = st.selectbox("Team Quantity", ["Select...", 1, 2, 3, 4, 5])
        pref_time = st.selectbox("Preferred Time Slot", ["Select...", "1st Half", "2nd Half", "Full Day"])
        task_type = st.selectbox("Team Required For", [
            "Select...", "Fresh Installation", "WIP", "SNAG", "Alignment",
            "Additional order", "Shifting", "Post sales", "F&D Installation"
        ])

        min_date = datetime.now().date() + timedelta(days=1)
        preferred_date = st.date_input("Preferred Visit Date", value=min_date, min_value=min_date)

        job_description = st.text_area("Brief of work to be done on site")

        categories = ["Kitchen", "Wardrobe", "Storage", "F&D", "Metal Kitchen"]
        selected_categories = st.multiselect("Select Categories", categories)

        # ------------------------ SUBMIT BUTTON ------------------------
        if st.button("SUBMIT", key="submit_request", help="Submit request", type="primary"):
            if team_qty == "Select..." or pref_time == "Select..." or task_type == "Select...":
                st.warning("⚠️ Please fill all fields!")
            else:
                # Generate Request Number
                fy_code = f"{datetime.now().year % 100}/{(datetime.now().year + 1) % 100}"
                city_code = selected_data["city"][:3].upper()

                existing_reqs = db.collection("Requests").where("city", "==", selected_data["city"]).stream()
                req_count = sum(1 for _ in existing_reqs) + 1

                request_number = f"{city_code}-{req_count:03d}-{fy_code}"

                # Save Request
                db.collection("Requests").add({
                    "project_id": selected_data["pid"],
                    "project_name": selected_data["project_name"],
                    "city": selected_data["city"],
                    "address": selected_data["address"],
                    "team_qty": team_qty,
                    "preferred_time": pref_time,
                    "task_type": task_type,
                    "preferred_date": preferred_date.strftime("%Y-%m-%d"),
                    "job_description": job_description,
                    "categories": selected_categories,
                    "request_number": request_number,
                    "timestamp": datetime.now()
                })

                # SUCCESS MESSAGE
                st.success(f"✅ Request Submitted Successfully!\n\n**Request Number: {request_number}**")

                # CLEAR FORM AUTOMATICALLY
                st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)
