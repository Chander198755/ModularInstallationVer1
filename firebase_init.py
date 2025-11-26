import os
import firebase_admin
from firebase_admin import credentials, firestore

def init_firestore():
    if not firebase_admin._apps:

        # Check if running on Streamlit Cloud (uses environment variables)
        if (
            os.getenv("FIREBASE_PROJECT_ID")
            and os.getenv("FIREBASE_PRIVATE_KEY")
            and os.getenv("FIREBASE_CLIENT_EMAIL")
        ):
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "token_uri": "https://oauth2.googleapis.com/token"
            })

        else:
            # LOCAL MODE → use the JSON file
            cred = credentials.Certificate("serviceAccountKey.json")

        firebase_admin.initialize_app(cred)

    return firestore.client()
