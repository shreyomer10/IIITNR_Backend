# app/firebase.py
import json
import os
import firebase_admin
from firebase_admin import credentials

def init_firebase():
    service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))
    cred = credentials.Certificate(service_account_info)
    # Initialize Firebase only if not already initialized.
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
