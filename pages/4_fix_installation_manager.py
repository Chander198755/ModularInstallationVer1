import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # path to your service account key
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Define correct document data
manager_email = "chanderwebmail@gmail.com"
assigned_cities = ["Gurugram", "Okhla"]

# Write or overwrite the document
doc_ref = db.collection("InstallationManagers").document(manager_email)
doc_ref.set({
    "email": manager_email,
    "assigned_cities": assigned_cities
})

print(f"✅ Installation Manager '{manager_email}' added with cities: {', '.join(assigned_cities)}")
