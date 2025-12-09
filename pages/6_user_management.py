import streamlit as st
from backend.firebase_init import init_firestore
import hashlib

db = init_firestore()

st.title("👥 User Management (Super Admin Only)")
st.write("Add and manage all users in the system.")

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
    name = st.text_input("Full Name")  # 👈 Added Name field
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
                "name": name,              # 👈 Added
                "role": role,
                "password": hashed_pwd,
                "cities": cities,
                "active": True
            })
            st.success(f"User **{email}** added successfully!")

st.markdown("---")

# -------------------------------------
# 📝 Manage Existing Users Section
# -------------------------------------
st.subheader("📝 Update / Block Users")

users = db.collection("Users").stream()
user_list = [u.id for u in users]

if len(user_list) == 0:
    st.info("No users found.")
else:
    selected_user = st.selectbox("Select User", user_list)

    if selected_user:
        data = db.collection("Users").document(selected_user).get().to_dict()

        st.write(f"📧 Email: **{data.get('email','N/A')}**")
        st.write(f"👤 Name: **{data.get('name','N/A')}**")

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

        active_status = st.checkbox("Active ?", value=data.get("active", True))

        if st.button("💾 Save Changes"):
            db.collection("Users").document(selected_user).update({
                "role": new_role,
                "cities": new_cities,
                "active": active_status
            })
            st.success("✔ Changes saved!")

        # Block/Unblock Buttons
        if active_status:
            if st.button("🚫 Block User"):
                db.collection("Users").document(selected_user).update({"active": False})
                st.warning("User Blocked!")
        else:
            if st.button("🔓 Unblock User"):
                db.collection("Users").document(selected_user).update({"active": True})
                st.success("User Unblocked!")
