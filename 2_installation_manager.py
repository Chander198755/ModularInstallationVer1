import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd  # Import Pandas

# --- Firebase Initialization ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(
            f"Error initializing Firebase: {e}.  Please check your serviceAccountKey.json file path and contents."
        )
        st.stop()
db = firestore.client()

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
    .st-aggrid {
        height: 500px;  /* Set a fixed height for the Ag-Grid table */
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="top-header">Installation Manager Portal</div>', unsafe_allow_html=True)

# --- Simulated Login ---
if "email" not in st.session_state or not st.session_state.email:
    st.write("")  # Small spacer
    email_input = st.text_input("Enter your registered email to continue")
    if email_input:
        st.session_state.email = email_input.strip().lower()
        st.rerun()
    st.stop()


# --- Fetch assigned cities ---
def get_assigned_cities(email):
    try:
        doc = db.collection("InstallationManagers").document(email).get()
        if not doc.exists:
            return []
        data = doc.to_dict()
        return data.get("assigned_cities", [])
    except Exception as e:
        st.error(f"Error fetching assigned cities: {e}")
        return []


assigned_cities = get_assigned_cities(st.session_state.email)

if not assigned_cities:
    st.error("Access denied. You are not registered as an Installation Manager.")
    st.stop()


# --- City Filter ---
cities = ["All Cities"] + assigned_cities
col1, col2 = st.columns([2, 6])
with col1:
    selected_city = st.selectbox("Filter by City", cities)


# --- Fetch Requests with City Filter ---
def get_requests(city_filter):
    try:
        if city_filter != "All Cities":
            return (
                db.collection("Requests")
                .where("city", "==", city_filter)
                .order_by("timestamp", direction=firestore.Query.ASCENDING)
                .stream()
            )
        else:
            return (
                db.collection("Requests")
                .where("city", "in", assigned_cities)
                .order_by("timestamp", direction=firestore.Query.ASCENDING)
                .stream()
            )
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []


requests = get_requests(selected_city)


# --- Build request data ---
request_data = []
scopes_ol = set()
scopes_im = set()
all_status = set()

for req in requests:
    try:
        data = req.to_dict()
        data["doc_id"] = req.id
        # Prioritize Scope_of_Work, then fall back to task_type
        data["final_scope"] = data.get("Scope_of_Work") or data.get("task_type", "")

        if data.get("Scope_of_Work"):
            scopes_im.add(data["Scope_of_Work"])
        elif data.get("task_type"):
            scopes_ol.add(data["task_type"])

        request_data.append(data)
        if data.get("Status"):
            all_status.add(data["Status"])
    except Exception as e:
        st.error(f"Error processing request {req.id}: {e}")

all_scopes = sorted(scopes_im.union(scopes_ol))
status_list = ["", "Accepted", "Hold", "Cancelled"]  # Keep this for consistent order


# --- Summary Table Logic ---
pivot = defaultdict(lambda: defaultdict(int))
for row in request_data:
    status = row.get("Status", "")
    scope = row.get("Scope_of_Work") or row.get("task_type", "")
    pivot[status][scope] += 1

# --- Display Summary Table ---
st.markdown("### 🔍 Daily Update Summary")
table_html = """
<style>
    .summary-table {
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
        font-size: 11px;
        text-align: center;
    }
    .summary-table th, .summary-table td {
        border: 1px solid #ccc;
        padding: 2px 4px;
        line-height: 1.2;
        vertical-align: middle;
        word-wrap: break-word;
        max-width: 100px;
        white-space: normal;
    }
    .summary-table th {
        background-color: #f0f2f6;
        font-weight: 600;
    }
    .summary-table td:first-child, .summary-table th:first-child {
        max-width: 80px;
    }
</style>
<table class="summary-table">
<tr>
    <th>Status ↓ / Scope →</th>"""
for scope in all_scopes:
    table_html += f"<th>{scope}</th>"
table_html += "</tr>"

status_colors = {
    "": "#ffcccc",
    "Accepted": "#d4edda",
    "Hold": "#fff3cd",
    "Cancelled": "#f8d7da",
}
for status in status_list:
    color = status_colors.get(status, "#fff")
    table_html += f"<tr style='background-color:{color};'><td><b>{status or 'Blank'}</b></td>"
    for scope in all_scopes:
        count = pivot[status][scope]
        table_html += f"<td>{count}</td>"
    table_html += "</tr>"
table_html += "</table>"""

st.markdown(table_html, unsafe_allow_html=True)


# --- Show Editable Data Table ---
st.markdown("### 📝 Request Entries")


def convert_to_dataframe(request_data):
    """
    Convert request_data to Pandas DataFrame.
    """
    view_data = []
    for row in request_data:
        visit_date = row.get("Installer_Visit_Date")
        # Convert 'Visit Date' to datetime if it's not already None/NaT
        if visit_date and not pd.isna(visit_date):
            if isinstance(visit_date, str):
                try:
                    visit_date = datetime.strptime(visit_date, "%Y-%m-%d")  # First, try isoformat
                except ValueError:
                    try:
                        visit_date = datetime.strptime(visit_date, "%d-%b-%Y")  # Then, try DD-Mon-YYYY
                    except ValueError:
                        st.error(
                            f"Error: Visit Date '{visit_date}' is not in a valid format.  Please use %Y-%m-%d or DD-Mon-YYYY."
                        )
                        visit_date = None  # or handle the error as appropriate

            elif isinstance(visit_date, pd.Timestamp):
                visit_date = visit_date.to_pydatetime()
            # If it is already a datetime, no conversion is needed.

        view_data.append(
            {
                "Timestamp": row.get("timestamp", "N/A"),
                "Submitter Email": row.get("submitter_email", row.get("email", "N/A")),
                "City": row.get("city", "N/A"),
                "Project ID": row.get("project_id", "N/A"),
                "Project Name": row.get("project_name", "N/A"),
                "Project Address": row.get("address", "N/A"),
                "Categories": row.get("categories", "N/A"),
                "Task Type": row.get("task_type", "N/A"),
                "Job Description": row.get("job_description", "N/A"),
                "Preferred Date": row.get("preferred_time", "N/A"),
                "Preferred Time": row.get("preferred_time", "N/A"),
                "Team Quantity": row.get("team_quantity", "N/A"),
                "Request No": row.get("request_number", "N/A"),
                "Status": row.get("Status", ""),
                "Cancelled Reason Bin": row.get("Cancelled_Reason_Bin", ""),
                "Cancelled Reason": row.get("Cancelled_Reason_2", ""),
                "Final Scope": row.get("final_scope", ""),  # Use the calculated final_scope
                "Visit Date": visit_date,
                "Slot": row.get("Slot", ""),
                "Team Type": row.get("Team_Type", ""),
                "Team Base": row.get("Team_Base", ""),
                "Team 1": row.get("Team_Name_1", ""),
                "Team 2": row.get("Team_Name_2", ""),
                "Team 3": row.get("Team_Name_3", ""),
                "Team 4": row.get("Team_Name_4", ""),
                "Team 5": row.get("Team_Name_5", ""),
                "Project Status": row.get("Project_Status", ""),
                "Remarks": row.get("Remarks", ""),
            }
        )
    df = pd.DataFrame(view_data)
    if "Visit Date" in df.columns:
        df["Visit Date"] = pd.to_datetime(df["Visit Date"])
    return df



df = convert_to_dataframe(request_data)


def edit_and_save_data(df, selected_city):
    """
    Display the editable table and save updated data to Firestore.
    """
    # Fetch team names (team_name) based on the selected city.
    team_names = []
    team_types = []
    try:
        teams_ref = db.collection("Teams").where("city", "==", selected_city)
        team_docs = teams_ref.stream()
        for team_doc in team_docs:
            team_data = team_doc.to_dict()
            team_name = team_data.get("team_name")  # Fetch team_name
            team_type = team_data.get("team_type")
            if team_name:
                team_names.append(team_name)  # Collect team_names
            if team_type:
                team_types.append(team_type)
        # Remove duplicate
        team_names = list(set(team_names))
        team_types = list(set(team_types))
        if not team_names:
            team_names = [""]  # Ensure it's not empty
        if not team_types:
            team_types = [""]
    except Exception as e:
        st.error(f"Error fetching team data: {e}")
        team_names = [""]
        team_types = [""]

    # Calculate the minimum date (today + 1 day)
    min_date = datetime.now() + timedelta(days=1)

    # Use the correctly fetched team_types and team_names
    column_config = {
        "Status": st.column_config.SelectboxColumn(options=status_list),
        "Cancelled Reason Bin": st.column_config.SelectboxColumn(
            options=["", "Site Issues", "Cancelled by C", "Wrong PID/In"]
        ),
        "Cancelled Reason": st.column_config.SelectboxColumn(
            options=["", "Multiple Request", "Wrong PID / Invalid Request", "Site Issues",
                     "Entry Issues - Key/pass", "PIV Issues", "Week off and holidays", "HONS Done",
                     "Site Completed", "Material not delivered", "Late request filled", "Approval Not received"]
        ),
        "Team Type": st.column_config.SelectboxColumn(options=team_types),
        "Slot": st.column_config.SelectboxColumn(options=["", "Full Day", "1st Half", "2nd Half"]),
        "Final Scope": st.column_config.SelectboxColumn(
            options=all_scopes
        ),
        "Project Status": st.column_config.SelectboxColumn(
            options=[""]
        ),
        "Team Base": st.column_config.SelectboxColumn(options=team_names),  # Use team_names here
        "Team 1": st.column_config.Column(),
        "Team 2": st.column_config.Column(),
        "Team 3": st.column_config.Column(),
        "Team 4": st.column_config.Column(),
        "Team 5": st.column_config.Column(),
        "Visit Date": st.column_config.DateColumn(
            min_value=min_date.date(), format="DD-MM-YY",
        ),
        "Preferred Date": st.column_config.Column(
            label="Preferred Date",
        ),
    }

    edited_data = st.data_editor(df, num_rows="dynamic", column_config=column_config)
    if st.button("Save Updates"):
        for index, row in edited_data.iterrows():
            # Check if this row was added by the user (new row) or existed before.
            if index < len(request_data):
                doc_id = request_data[index]["doc_id"]  # Get the document ID
                try:
                    # Prepare a dictionary with the updated values, handling potential None values
                    updated_data = {
                        "Status": row["Status"],
                        "Cancelled_Reason_Bin": row["Cancelled Reason Bin"],
                        "Cancelled_Reason_2": row["Cancelled Reason"],
                        "Scope_of_Work": row["Final Scope"],  # Use value from data editor
                        "Installer_Visit_Date": row["Visit Date"],
                        "Slot": row["Slot"],
                        "Team_Type": row["Team Type"],
                        "Team_Base": row["Team Base"],  # Use Team Base
                        "Team_Name_1": row["Team 1"],
                        "Team_Name_2": row["Team 2"],
                        "Team_Name_3": row["Team 3"],
                        "Team_Name_4": row["Team 4"],
                        "Team_Name_5": row["Team 5"],
                        "Project_Status": row["Project Status"],
                        "Remarks": row["Remarks"],
                    }

                    # Remove keys with empty values before updating. Important for partial updates.
                    updated_data = {k: v for k, v in updated_data.items() if v != "" and not pd.isna(v)}
                    db.collection("Requests").document(doc_id).update(updated_data)
                    st.success(f"Document {doc_id} updated successfully!")

                except Exception as e:
                    st.error(f"Error updating document {doc_id}: {e}")
            else:
                # New row: Add a new document to Firestore
                try:
                    # Prepare a dictionary with the data for the new document.
                    new_data = {
                        "timestamp": datetime.now(),  # Add a timestamp
                        "submitter_email": st.session_state.email,  # get the email from session
                        "city": selected_city,  # Or get it from the form if the user can edit it
                        "project_id": row["Project ID"],
                        "project_name": row["Project Name"],
                        "address": row["Project Address"],
                        "categories": row["Categories"],
                        "task_type": row["Task Type"],
                        "job_description": row["Job Description"],
                        "preferred_time": row["Preferred Time"],
                        "preferred_date": row["Preferred Date"],
                        "team_quantity": row["Team Quantity"],
                        "request_number": "N/A",  # Or generate a new request number
                        "Status": row["Status"],
                        "Cancelled_Reason_Bin": row["Cancelled Reason Bin"],
                        "Cancelled_Reason_2": row["Cancelled Reason"],
                        "Scope_of_Work": row["Final Scope"],  # Use value from data editor
                        "Installer_Visit_Date": row["Visit Date"],
                        "Slot": row["Slot"],
                        "Team_Type": row["Team Type"],
                        "Team_Base": row["Team Base"],  # Use Team Base
                        "Team_Name_1": row["Team 1"],
                        "Team_Name_2": row["Team 2"],
                        "Team_Name_3": row["Team 3"],
                        "Team_Name_4": row["Team 4"],
                        "Team_Name_5": row["Team 5"],
                        "Project_Status": row["Project Status"],
                        "Remarks": row["Remarks"],
                    }

                    # Remove keys with empty values before creating.
                    new_data = {k: v for k, v in new_data.items() if v != "" and not pd.isna(v)}

                    # Add the new document to the "Requests" collection.
                    _, ref = db.collection("Requests").add(new_data)
                    st.success(f"New document added with ID: {ref.id}")
                except Exception as e:
                    st.error(f"Error adding new document: {e}")
        st.rerun()  # rerun to reflect the updated data.



if not request_data:
    st.warning("No requests found.")
else:
    edit_and_save_data(df, selected_city)
