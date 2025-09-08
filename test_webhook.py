#!/usr/bin/env python3
"""
Test webhook for FormFlow AI
"""

import requests
import json
from datetime import datetime

# Webhook URL with user_id
webhook_url = "https://8080-cs-6153049b-56ab-43af-abb0-9a07798390f5.cs-europe-west4-fycr.cloudshell.dev/api/v1/webhooks/google-forms"
user_id = "fb6d90e7-a951-4623-b3fe-4be27736d48d"

# Test data simulating Google Forms submission
test_data = {
    "timestamp": datetime.now().isoformat(),
    "formId": f"test-form-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "formTitle": "Customer Satisfaction Survey",
    "responses": [
        {
            "questionId": "q1",
            "question": "What is your name?",
            "answer": "Test User"
        },
        {
            "questionId": "q2",
            "question": "How would you rate our service? (1-10)",
            "answer": "9"
        },
        {
            "questionId": "q3",
            "question": "What features do you like most?",
            "answer": "AI-powered dashboard generation, easy integration with Google Forms, real-time data visualization"
        },
        {
            "questionId": "q4",
            "question": "Any suggestions for improvement?",
            "answer": "Add more chart types, PDF export, team collaboration features"
        },
        {
            "questionId": "q5",
            "question": "Would you recommend us to others?",
            "answer": "Yes, definitely! This tool saves hours of manual work."
        }
    ]
}

# Send webhook request
try:
    print(f"🚀 Sending webhook to: {webhook_url}")
    print(f"📝 User ID: {user_id}")
    
    response = requests.post(
        f"{webhook_url}?user_id={user_id}",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"✅ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✨ Webhook processed successfully!")
        print(f"📊 Response: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n📋 Test completed!")
print("Check your dashboard for the new AI-generated dashboard.")
