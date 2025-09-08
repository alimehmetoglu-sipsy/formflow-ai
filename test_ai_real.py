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
print("\n🤖 Testing with REAL OpenAI GPT-4...")

# Diet Plan form submission for AI processing
webhook_payload = {
    "event_id": str(uuid.uuid4()),
    "event_type": "form_response",
    "form_response": {
        "form_id": "ai_diet_test",
        "token": str(uuid.uuid4())[:8],
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "definition": {
            "title": "AI-Powered Personalized Diet Plan"
        },
        "answers": [
            {
                "field": {
                    "id": "field1",
                    "title": "What is your current weight in kg?"
                },
                "type": "number",
                "number": 85
            },
            {
                "field": {
                    "id": "field2",
                    "title": "What is your target weight in kg?"
                },
                "type": "number",
                "number": 75
            },
            {
                "field": {
                    "id": "field3",
                    "title": "What is your height in cm?"
                },
                "type": "number",
                "number": 180
            },
            {
                "field": {
                    "id": "field4",
                    "title": "What are your dietary restrictions?"
                },
                "type": "text",
                "text": "Vegetarian, lactose intolerant, no nuts due to allergy"
            },
            {
                "field": {
                    "id": "field5",
                    "title": "How many meals per day do you prefer?"
                },
                "type": "choice",
                "choice": {
                    "label": "3 main meals + 2 snacks"
                }
            },
            {
                "field": {
                    "id": "field6",
                    "title": "What is your activity level?"
                },
                "type": "choice",
                "choice": {
                    "label": "Moderately active (exercise 3-4 times per week)"
                }
            },
            {
                "field": {
                    "id": "field7",
                    "title": "What are your favorite foods?"
                },
                "type": "text",
                "text": "Mediterranean cuisine, quinoa, tofu, fresh vegetables, fruits"
            },
            {
                "field": {
                    "id": "field8",
                    "title": "Any health conditions?"
                },
                "type": "text",
                "text": "Pre-diabetic, need to control blood sugar levels"
            }
        ]
    }
}

# Send webhook with user_id
url = f"http://localhost:8000/api/v1/webhooks/typeform?user_id={user_id}"
headers = {"Content-Type": "application/json"}

print(f"\n📤 Sending diet plan request to AI processor...")
print("This may take 10-15 seconds for GPT-4 to generate personalized content...")

try:
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"\n✅ Response Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print("\n🎉 AI-Powered Dashboard Created Successfully!")
        print(f"Dashboard URL: {result.get('dashboard_url')}")
        print(f"Token: {result.get('dashboard_url', '').split('/')[-1]}")
        print("\n💡 The AI has generated a personalized diet plan based on:")
        print("   • Weight loss goal: 85kg → 75kg")
        print("   • Dietary restrictions: Vegetarian, lactose intolerant, no nuts")
        print("   • Health condition: Pre-diabetic")
        print("   • Activity level: Moderately active")
        print("\n🔗 Visit the dashboard to see your personalized meal plan!")
except Exception as e:
    print(f"❌ Error: {str(e)}")