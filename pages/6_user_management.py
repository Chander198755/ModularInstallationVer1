import streamlit as st
import pandas as pd
from backend.firebase_init import init_firestore
import hashlib

# Firestore
db = init_firestore()

# Page Title
st.title("👥 User Management (Super Admin Only)")
st.write("Add, view and manage all system users.")

# Access Restriction
if st.session_state.user_role != "SuperAdmin":
    st.error("🚫 Access Denied — Only SuperAdmin allowed here!")
    st.stop()

st.markdown("---")

# -------------------------------------
# ➕ Add New User Section
# -------------------------------------
st.subheader("➕ Add New User")

with st.form("add_user_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["OL", "InstallationManager", "Admin", "SuperAdmin"])
    password = st.text_input("Password", type="password")
    cities = st.multiselect(
        "Cities Access",
        ["ALL", "Bangalore", "Mumbai", "Delhi", "Pune", "Hyd", "Kolkata", "Chennai"]
    )

    submitted = st.form_submit_button("Add User")
    if submitted:
        if not email or not password or not name:
            st.error("⚠ Name, Email & Password Required!")
        else:
            hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
            db.collection("Users").document(email).set({
                "email": email,
                "name": name,
                "role": role,
                "password": hashed_pwd,
                "cities": cities,
                "active": True
            })
            st.success(f"User **{email}** added successfully!")
            st.rerun()

st.markdown("---")

# -------------------------------------
# 📋 User List + Filters
# -------------------------------------
st.subheader("📋 User List")

# Load all users
user_docs = db.collection("Users").stream()
all_users = [u.to_dict() for u in user_docs]

if not all_users:
    st.info("No users found in system.")
    st.stop()

df = pd.DataFrame(all_users)

# Filter Controls
col1, col2 = st.columns(2)
filter_role = col1.selectbox("Filter by Role", ["All"] + sorted(df["role"].unique().tolist()))
filter_status = col2.selectbox("Filter by Status", ["All", "Active", "Blocked"])

# Apply Filters
if filter_role != "All":
    df = df[df["role"] == filter_role]
if filter_status != "All":
    df = df[df["active"] == (filter_status == "Active")]

st.dataframe(df[["email", "name", "role", "cities", "active"]], use_container_width=True)

st.markdown("---")

# -------------------------------------
# 📝 Update / Block Users
# -------------------------------------
st.subheader("📝 Update / Block User")

user_list = df["email"].tolist()
selected_user = st.selectbox("Select User to Edit", user_list)

if selected_user:
    data = db.collection("Users").document(selected_user).get().to_dict()

    st.write(f"📧 Email: **{data.get('email')}**")
    st.write(f"👤 Name: **{data.get('name')}**")

    new_role = st.selectbox(
        "Update Role",
        ["OL", "InstallationManager", "Admin", "SuperAdmin"],
        index=["OL", "InstallationManager", "Admin", "SuperAdmin"].index(data["role"])
    )

    new_cities = st.multiselect(
        "Update Cities",
        ["ALL", "Bangalore", "Mumbai", "Delhi", "Pune", "Hyd", "Kolkata", "Chennai"],
        default=data.get("cities", [])
    )

    new_status = st.checkbox("Active?", value=data.get("active", True))

    if st.button("💾 Save Changes"):
        db.collection("Users").document(selected_user).update({
            "role": new_role,
            "cities": new_cities,
            "active": new_status
        })
        st.success("✔ Changes Updated!")
        st.rerun()

    # Block / Unblock User
    if new_status:
        if st.button("🚫 Block User"):
            db.collection("Users").document(selected_user).update({"active": False})
            st.warning("User Blocked!")
            st.rerun()
    else:
        if st.button("🔓 Unblock User"):
            db.collection("Users").document(selected_user).update({"active": True})
            st.success("User Unblocked!")
            st.rerun()
