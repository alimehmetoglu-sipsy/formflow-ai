#!/usr/bin/env python3
import requests
import json

# Create test user
user_data = {
    "name": "Test User",
    "email": "test@formflow.ai",
    "password": "TestPass123!"
}

url = "http://localhost:8000/api/v1/auth/register"
headers = {"Content-Type": "application/json"}

print("Creating test user...")
print("Email: test@formflow.ai")
print("Password: TestPass123!")

try:
    response = requests.post(url, json=user_data, headers=headers)
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ User created successfully!")
        print(f"Access Token: {result.get('access_token')[:20]}...")
        print(f"User: {json.dumps(result.get('user'), indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")