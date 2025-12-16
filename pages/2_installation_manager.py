import streamlit as st
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

from backend.firebase_init import init_firestore

# --- Firebase ---
db = init_firestore()

st.set_page_config(page_title="Installation Manager - Daily Updates", layout="wide")

# --- Styling ---
st.markdown(
    """
    <style>
    .top-header {
        font-size: 20px;
        font-weight: 600;
        margin-top: -10px;
        margin-bottom: 10px;
        text-align: left;
    }
    .block-container {
        padding-top: 1.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="top-header">Installation Manager Portal</div>', unsafe_allow_html=True)

# ===== SaaS LOGIN CONTEXT =====
company_id = st.session_state.get("company_id")
user_email = st.session_state.get("user_email")
user_role = st.session_state.get("user_role")

if not company_id or not user_email:
    st.error("Session expired. Please login again.")
    st.stop()

if user_role != "IM":
    st.error("Access denied. Installation Manager only.")
    st.stop()

# ===== Fetch assigned cities =====
def get_assigned_cities(email):
    doc = (
        db.collection("companies")
          .document(company_id)
          .collection("InstallationManagers")
          .document(email)
          .get()
    )
    if not doc.exists:
        return []
    return doc.to_dict().get("assigned_cities", [])

assigned_cities = get_assigned_cities(user_email)

if not assigned_cities:
    st.error("Access denied. You are not assigned to any city.")
    st.stop()

# --- City Filter ---
cities = ["All Cities"] + assigned_cities
selected_city = st.selectbox("Filter by City", cities)

# --- Fetch Requests ---
def get_requests(city_filter):
    ref = (
        db.collection("companies")
          .document(company_id)
          .collection("Requests")
    )
    if city_filter != "All Cities":
        return ref.where("city", "==", city_filter).stream()
    else:
        return ref.where("city", "in", assigned_cities).stream()

requests = get_requests(selected_city)

# --- Build request data ---
request_data = []
scopes_ol = set()
scopes_im = set()

for req in requests:
    data = req.to_dict()
    data["doc_id"] = req.id
    data["final_scope"] = data.get("Scope_of_Work") or data.get("task_type", "")
    if data.get("Scope_of_Work"):
        scopes_im.add(data["Scope_of_Work"])
    elif data.get("task_type"):
        scopes_ol.add(data["task_type"])
    request_data.append(data)

all_scopes = sorted(scopes_im.union(scopes_ol))
status_list = ["", "Accepted", "Hold", "Cancelled"]

# --- Summary Table ---
pivot = defaultdict(lambda: defaultdict(int))
for row in request_data:
    pivot[row.get("Status", "")][row.get("final_scope", "")] += 1

st.markdown("### 🔍 Daily Update Summary")

table_html = "<table class='summary-table'><tr><th>Status ↓ / Scope →</th>"
for scope in all_scopes:
    table_html += f"<th>{scope}</th>"
table_html += "</tr>"

for status in status_list:
    table_html += f"<tr><td><b>{status or 'Blank'}</b></td>"
    for scope in all_scopes:
        table_html += f"<td>{pivot[status][scope]}</td>"
    table_html += "</tr>"
table_html += "</table>"

st.markdown(table_html, unsafe_allow_html=True)

# --- Convert to DataFrame ---
def convert_to_dataframe(request_data):
    view_data = []
    for row in request_data:
        view_data.append({
            "City": row.get("city"),
            "Project ID": row.get("project_id"),
            "Project Name": row.get("project_name"),
            "Project Address": row.get("address"),
            "Task Type": row.get("task_type"),
            "Request No": row.get("request_number"),
            "Status": row.get("Status", ""),
            "Final Scope": row.get("final_scope", ""),
            "Visit Date": row.get("Installer_Visit_Date"),
            "Slot": row.get("Slot", ""),
            "Team Type": row.get("Team_Type", ""),
            "Team Base": row.get("Team_Base", ""),
            "Team 1": row.get("Team_Name_1", ""),
            "Team 2": row.get("Team_Name_2", ""),
            "Team 3": row.get("Team_Name_3", ""),
            "Team 4": row.get("Team_Name_4", ""),
            "Team 5": row.get("Team_Name_5", ""),
            "Remarks": row.get("Remarks", "")
        })
    return pd.DataFrame(view_data)

df = convert_to_dataframe(request_data)

# --- Editable Grid ---
def edit_and_save_data(df):
    team_names = []
    team_types = []

    teams = (
        db.collection("companies")
          .document(company_id)
          .collection("Teams")
          .stream()
    )

    for t in teams:
        d = t.to_dict()
        if d.get("team_name"):
            team_names.append(d["team_name"])
        if d.get("team_type"):
            team_types.append(d["team_type"])

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn(options=status_list),
            "Final Scope": st.column_config.SelectboxColumn(options=all_scopes),
            "Team Type": st.column_config.SelectboxColumn(options=list(set(team_types))),
            "Team Base": st.column_config.SelectboxColumn(options=list(set(team_names))),
            "Visit Date": st.column_config.DateColumn(),
        },
    )

    if st.button("Save Updates"):
        for i, row in edited.iterrows():
            doc_id = request_data[i]["doc_id"]
            update = {k: v for k, v in row.items() if v not in ["", None]}
            (
                db.collection("companies")
                  .document(company_id)
                  .collection("Requests")
                  .document(doc_id)
                  .update(update)
            )
        st.success("Updates saved")
        st.rerun()

if request_data:
    st.markdown("### 📝 Request Entries")
    edit_and_save_data(df)
else:
    st.warning("No requests found.")
