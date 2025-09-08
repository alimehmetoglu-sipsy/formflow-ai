#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime

# Test webhook payload
webhook_payload = {
    "event_id": str(uuid.uuid4()),
    "event_type": "form_response",
    "form_response": {
        "form_id": "test_form_123",
        "token": str(uuid.uuid4())[:8],
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "definition": {
            "title": "Customer Feedback Survey"
        },
        "answers": [
            {
                "field": {
                    "id": "field1",
                    "title": "What is your name?"
                },
                "type": "text",
                "text": "John Doe"
            },
            {
                "field": {
                    "id": "field2",
                    "title": "How satisfied are you with our service?"
                },
                "type": "choice",
                "choice": {
                    "label": "Very Satisfied"
                }
            },
            {
                "field": {
                    "id": "field3",
                    "title": "What features would you like to see?"
                },
                "type": "text",
                "text": "Better dashboard analytics, real-time updates, and more customization options"
            },
            {
                "field": {
                    "id": "field4",
                    "title": "Would you recommend us?"
                },
                "type": "boolean",
                "boolean": True
            },
            {
                "field": {
                    "id": "field5",
                    "title": "Rate our service (1-10)"
                },
                "type": "number",
                "number": 9
            }
        ]
    }
}

# Send webhook to backend
url = "http://localhost:8000/api/v1/webhooks/typeform"
headers = {"Content-Type": "application/json"}

print("Sending test webhook to:", url)
print("Payload:", json.dumps(webhook_payload, indent=2))

try:
    response = requests.post(url, json=webhook_payload, headers=headers)
    print("\nResponse Status:", response.status_code)
    print("Response Body:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Webhook processed successfully!")
        print(f"Dashboard URL: {result.get('dashboard_url')}")
        print(f"Submission ID: {result.get('submission_id')}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")