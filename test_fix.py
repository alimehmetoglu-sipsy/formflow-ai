#!/usr/bin/env python3
import requests
import json

# Test webhook with event registration data
webhook_url = "http://localhost:8000/api/v1/webhooks/typeform"

test_payload = {
    "event_id": "01HQF9AZPEXAMPLE",
    "event_type": "form_response",
    "form_response": {
        "form_id": "form123",
        "token": "event_test_" + str(hash("test"))[-6:],
        "submitted_at": "2025-01-07T12:00:00Z",
        "definition": {
            "title": "Event Registration Form"
        },
        "answers": [
            {
                "field": {"id": "field1", "type": "short_text", "title": "name"},
                "type": "text",
                "text": "John Doe"
            },
            {
                "field": {"id": "field2", "type": "email", "title": "email"},
                "type": "email",
                "email": "john@example.com"
            },
            {
                "field": {"id": "field3", "type": "short_text", "title": "event_name"},
                "type": "text",
                "text": "FormFlow AI Conference 2025"
            },
            {
                "field": {"id": "field4", "type": "date", "title": "event_date"},
                "type": "date",
                "date": "2025-02-15"
            }
        ]
    }
}

try:
    response = requests.post(
        webhook_url,
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Webhook processed successfully!")
        dashboard_url = response.json().get('dashboard_url')
        if dashboard_url:
            print(f"Dashboard URL: {dashboard_url}")
    else:
        print("❌ Webhook failed")
        
except Exception as e:
    print(f"Error: {e}")