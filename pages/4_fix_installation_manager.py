import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase Init (utility script is OK with serviceAccountKey.json) ---
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ============================
# CONFIG (EDIT ONLY THIS PART)
# ============================
company_id = "MODINTL"   # 🔑 SaaS company code
manager_email = "chanderwebmail@gmail.com"
assigned_cities = ["Gurugram", "Okhla"]

# ============================
# WRITE DATA (SaaS SAFE)
# ============================
doc_ref = (
    db.collection("companies")
      .document(company_id)
      .collection("InstallationManagers")
      .document(manager_email.lower())
)

doc_ref.set({
    "email": manager_email.lower(),
    "assigned_cities": assigned_cities,
    "active": True
})

print(
    f"✅ Installation Manager '{manager_email}' "
    f"added for company '{company_id}' "
    f"with cities: {', '.join(assigned_cities)}"
)
