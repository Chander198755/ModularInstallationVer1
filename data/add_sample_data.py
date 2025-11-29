import firebase_admin
from firebase_admin import credentials, firestore
import random

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Sample cities
cities = ["Delhi", "Mumbai", "Bangalore"]

# Add sample records
for i in range(1, 6):
    city = random.choice(cities)
    request = {
        "request_id": f"REQ-{1000 + i}",
        "site_name": f"Site {i}",
        "city": city,
        "status": "Pending",
        "requested_by": f"user{i}@example.com",
        "team_type": "Inhouse" if i % 2 == 0 else "Vendor"
    }
    db.collection("SiteRequests").add(request)

print("✅ Sample data added successfully!")
