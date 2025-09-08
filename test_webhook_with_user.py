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
token = auth_data['access_token']

print(f"Logged in as: {auth_data['user']['email']}")
print(f"User ID: {user_id}")

# Test webhook payload
webhook_payload = {
    "event_id": str(uuid.uuid4()),
    "event_type": "form_response",
    "form_response": {
        "form_id": "diet_form_456",
        "token": str(uuid.uuid4())[:8],
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "definition": {
            "title": "Personalized Diet Plan Survey"
        },
        "answers": [
            {
                "field": {
                    "id": "field1",
                    "title": "What is your current weight?"
                },
                "type": "number",
                "number": 75
            },
            {
                "field": {
                    "id": "field2",
                    "title": "What is your target weight?"
                },
                "type": "number",
                "number": 70
            },
            {
                "field": {
                    "id": "field3",
                    "title": "What are your dietary restrictions?"
                },
                "type": "text",
                "text": "Vegetarian, no gluten"
            },
            {
                "field": {
                    "id": "field4",
                    "title": "How many meals per day?"
                },
                "type": "choice",
                "choice": {
                    "label": "3 meals + 2 snacks"
                }
            },
            {
                "field": {
                    "id": "field5",
                    "title": "Activity level?"
                },
                "type": "choice",
                "choice": {
                    "label": "Moderately active (3-5 days/week)"
                }
            }
        ]
    }
}

# Send webhook with user_id as query parameter
url = f"http://localhost:8000/api/v1/webhooks/typeform?user_id={user_id}"
headers = {"Content-Type": "application/json"}

print(f"\nSending webhook to: {url}")

try:
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"Response Status: {response.status_code}")
    print("Response Body:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Webhook processed successfully!")
        print(f"Dashboard URL: {result.get('dashboard_url')}")
        print(f"Submission ID: {result.get('submission_id')}")
        print("\n🎯 This dashboard should now appear in the user's dashboard list!")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")