#!/usr/bin/env python3
import requests
import json

# Test webhook with diet plan data
webhook_url = "http://localhost:8000/api/v1/webhooks/typeform"

test_payload = {
    "event_id": "01HQF9AZPEXAMPLE",
    "event_type": "form_response",
    "form_response": {
        "form_id": "form123",
        "token": "diet_test_" + str(hash("diet_test"))[-6:],
        "submitted_at": "2025-01-07T12:00:00Z",
        "definition": {
            "title": "Diet and Nutrition Form"
        },
        "answers": [
            {
                "field": {"id": "field1", "type": "short_text", "title": "goal"},
                "type": "text",
                "text": "lose weight and build muscle"
            },
            {
                "field": {"id": "field2", "type": "number", "title": "current_weight"},
                "type": "number",
                "number": 80
            },
            {
                "field": {"id": "field3", "type": "short_text", "title": "diet_preference"},
                "type": "text",
                "text": "vegetarian meals with healthy options"
            },
            {
                "field": {"id": "field4", "type": "number", "title": "target_calories"},
                "type": "number",
                "number": 1800
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
        print("✅ Diet plan webhook processed successfully!")
        dashboard_url = response.json().get('dashboard_url')
        if dashboard_url:
            print(f"Dashboard URL: {dashboard_url}")
    else:
        print("❌ Webhook failed")
        
except Exception as e:
    print(f"Error: {e}")