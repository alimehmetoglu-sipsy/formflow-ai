#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime

# First, login to get the user token
login_data = {
    "email": "test@formflow.ai",
    "password": "TestPass123!"
}

print("Logging in...")
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json=login_data
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

auth_data = login_response.json()
user_id = auth_data['user']['id']

print(f"Logged in as: {auth_data['user']['email']}")

# Lead Score form submission
webhook_payload = {
    "event_id": str(uuid.uuid4()),
    "event_type": "form_response",
    "form_response": {
        "form_id": "lead_form_789",
        "token": str(uuid.uuid4())[:8],
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "definition": {
            "title": "Lead Qualification Survey"
        },
        "answers": [
            {
                "field": {
                    "id": "field1",
                    "title": "Company Name"
                },
                "type": "text",
                "text": "TechCorp Solutions"
            },
            {
                "field": {
                    "id": "field2",
                    "title": "Your Role"
                },
                "type": "choice",
                "choice": {
                    "label": "Chief Technology Officer"
                }
            },
            {
                "field": {
                    "id": "field3",
                    "title": "Company Size"
                },
                "type": "choice",
                "choice": {
                    "label": "100-500 employees"
                }
            },
            {
                "field": {
                    "id": "field4",
                    "title": "Budget Range"
                },
                "type": "choice",
                "choice": {
                    "label": "$50,000 - $100,000"
                }
            },
            {
                "field": {
                    "id": "field5",
                    "title": "Implementation Timeline"
                },
                "type": "choice",
                "choice": {
                    "label": "Within 3 months"
                }
            },
            {
                "field": {
                    "id": "field6",
                    "title": "Main Challenge"
                },
                "type": "text",
                "text": "We need to automate our form processing and generate better insights from customer data"
            }
        ]
    }
}

# Send webhook with user_id
url = f"http://localhost:8000/api/v1/webhooks/typeform?user_id={user_id}"
headers = {"Content-Type": "application/json"}

print(f"\nSending Lead Score webhook...")

try:
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"Response Status: {response.status_code}")
    result = response.json()
    print("\n✅ Lead Score dashboard created!")
    print(f"Dashboard URL: {result.get('dashboard_url')}")
    print(f"Token: {result.get('dashboard_url', '').split('/')[-1]}")
except Exception as e:
    print(f"❌ Error: {str(e)}")