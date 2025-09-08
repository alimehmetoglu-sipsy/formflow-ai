#!/usr/bin/env python3
import requests
import json

# Test webhook with lead scoring data  
webhook_url = "http://localhost:8000/api/v1/webhooks/typeform"

test_payload = {
    "event_id": "01HQF9AZPEXAMPLE",
    "event_type": "form_response",
    "form_response": {
        "form_id": "form123",
        "token": "lead_test_" + str(hash("lead_test"))[-6:],
        "submitted_at": "2025-01-07T12:00:00Z",
        "definition": {
            "title": "Lead Qualification Form"
        },
        "answers": [
            {
                "field": {"id": "field1", "type": "short_text", "title": "company"},
                "type": "text", 
                "text": "Tech Solutions Inc"
            },
            {
                "field": {"id": "field2", "type": "short_text", "title": "budget"},
                "type": "text",
                "text": "$50,000 - $100,000"
            },
            {
                "field": {"id": "field3", "type": "short_text", "title": "timeline"},
                "type": "text",
                "text": "Need to make a decision within 3 months"
            },
            {
                "field": {"id": "field4", "type": "short_text", "title": "business_need"},
                "type": "text",
                "text": "Looking to purchase new software for our team"
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
        print("✅ Lead scoring webhook processed successfully!")
        dashboard_url = response.json().get('dashboard_url')
        if dashboard_url:
            print(f"Dashboard URL: {dashboard_url}")
    else:
        print("❌ Webhook failed")
        
except Exception as e:
    print(f"Error: {e}")