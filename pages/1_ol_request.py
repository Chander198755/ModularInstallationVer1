import streamlit as st
from datetime import datetime, timedelta
from backend.firebase_init import init_firestore 

# --- CONFIGURATION ---
st.set_page_config(layout="centered")
db = init_firestore()

st.title("🏡 Modular Installation Request")
st.markdown("---")

# === STATE HANDLING ===
if "form_reset" not in st.session_state:
    st.session_state.form_reset = False
if "selected_pid_data" not in st.session_state:
    st.session_state.selected_pid_data = None

# Reset logic after submit
if st.session_state.form_reset:
    st.session_state.clear()
    st.rerun()

# Center Layout
col_left, col_main, col_right = st.columns([1, 4, 1])

# Helper for aligned input rows
def aligned_row(label, widget_func):
    col1, col2 = st.columns([1.3, 2])
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        widget_func()


# =========== STEP 1: PID SELECTION ===========

with col_main:
    with st.container(border=True):

        pid_docs = db.collection("PID").stream()
        pid_list = []
        for doc in pid_docs:
            d = doc.to_dict()

            city_val = d.get("city_name") or d.get("city") or "Unknown City"
            addr_val = d.get("address") or d.get("Address") or "Unknown Address"

            pid_list.append({
                "display": f"{d.get('project_name','Unknown')} | PID: {d.get('project_id')}",
                "pid": d.get("project_id"),
                "project_name": d.get("project_name", "Unknown"),
                "city": city_val,
                "address": addr_val
            })

        pid_options = ["Select..."] + [i["display"] for i in pid_list]
        pid_choice = st.selectbox("Select Project", pid_options)

        selected_data = next((i for i in pid_list if i["display"] == pid_choice), None)

        if selected_data and pid_choice != "Select...":
            st.session_state.selected_pid_data = selected_data


# =========== STEP 2: FORM ONCE PID SELECTED ===========

if st.session_state.selected_pid_data:
    selected_data = st.session_state.selected_pid_data

    with col_main:
        with st.container(border=True):

            st.markdown(
                f"**Project:** {selected_data['project_name']}  (PID: {selected_data['pid']})  \n"
                f"**City:** {selected_data['city']} | **Address:** {selected_data['address']}"
            )
            st.markdown("---")

            min_date = datetime.now().date() + timedelta(days=1)

            aligned_row("Preferred Visit Date", lambda: st.date_input(
                "Preferred Visit Date", value=min_date,
                min_value=min_date,
                key="preferred_date",
                label_visibility="collapsed"
            ))

            aligned_row("Task Required For", lambda: st.selectbox(
                "Task Required For",
                ["Select...", "Fresh Installation", "WIP", "SNAG", "Alignment",
                 "Additional order", "Shifting", "Post sales", "F&D Installation"],
                key="task_type", label_visibility="collapsed"
            ))

            categories = ["Kitchen", "Wardrobe", "Storage", "F&D", "Metal Kitchen"]
            aligned_row("Select Categories", lambda: st.multiselect(
                "Select Categories", categories,
                key="selected_categories",
                label_visibility="collapsed"
            ))

            aligned_row("Preferred Time Slot", lambda: st.selectbox(
                "Preferred Time Slot", ["Select...", "1st Half", "2nd Half", "Full Day"],
                key="pref_time", label_visibility="collapsed"
            ))

            aligned_row("Team Quantity", lambda: st.selectbox(
                "Team Quantity", ["Select...", 1, 2, 3, 4, 5],
                key="team_qty", label_visibility="collapsed"
            ))

            st.markdown("**Job Description**")
            job_description = st.text_area(
                "Job Description",
                height=80,
                key="job_description",
                label_visibility="collapsed"
            )

        # === Buttons ===
        col_back, col_submit = st.columns([1, 1])

        with col_back:
            if st.button("⬅ BACK"):
                st.session_state.selected_pid_data = None
                st.rerun()

        with col_submit:
            if st.button("SUBMIT REQUEST", type="primary"):
                if (st.session_state.team_qty == "Select..."
                        or st.session_state.pref_time == "Select..."
                        or st.session_state.task_type == "Select..."):
                    st.warning("⚠ Please fill all required fields!")
                else:
                    now = datetime.now()
                    fy = f"{now.year % 100}/{(now.year + 1) % 100}"
                    city_code = selected_data["city"][:3].upper()

                    existing = db.collection("Requests").where(
                        "city", "==", selected_data["city"]).stream()
                    req_count = sum(1 for _ in existing) + 1
                    request_no = f"{city_code}-{req_count:03d}-{fy}"

                    # 🔥 Updated Date Format → 6-Dec-2025
                    formatted_date = st.session_state.preferred_date.strftime("%-d-%b-%Y")

                    db.collection("Requests").add({
                        "project_id": selected_data["pid"],
                        "project_name": selected_data["project_name"],
                        "city": selected_data["city"],
                        "address": selected_data["address"],
                        "team_qty": st.session_state.team_qty,
                        "preferred_time": st.session_state.pref_time,
                        "task_type": st.session_state.task_type,
                        "preferred_date": formatted_date,
                        "job_description": job_description,
                        "categories": st.session_state.selected_categories,
                        "request_number": request_no,
                        "timestamp": now,
                    })

                    st.success(f"🎉 Request Submitted!\n\n### Request Number: `{request_no}`")
                    st.session_state.form_reset = True
