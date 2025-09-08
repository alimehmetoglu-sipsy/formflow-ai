#!/usr/bin/env python3
"""
Script to test Typeform webhook integration
Usage: python scripts/test_webhook.py [webhook_url]
"""

import requests
import json
import hmac
import hashlib
import sys
from datetime import datetime

def create_signature(payload: str, secret: str) -> str:
    """Create HMAC signature for webhook"""
    return "sha256=" + hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

def create_test_payload(form_type="diet"):
    """Create test webhook payload for different form types"""
    
    base_payload = {
        "event_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "event_type": "form_response",
        "form_response": {
            "form_id": "test_form_123",
            "token": f"test_token_{datetime.now().strftime('%H%M%S')}",
            "submitted_at": datetime.now().isoformat() + "Z",
            "definition": {
                "title": f"Test {form_type.title()} Form"
            },
            "answers": []
        }
    }
    
    if form_type == "diet":
        base_payload["form_response"]["answers"] = [
            {
                "field": {"id": "1", "title": "What is your primary goal?"},
                "type": "text",
                "text": "Lose weight and build muscle"
            },
            {
                "field": {"id": "2", "title": "Current weight (kg)"},
                "type": "number",
                "number": 75
            },
            {
                "field": {"id": "3", "title": "Target weight (kg)"},
                "type": "number", 
                "number": 68
            },
            {
                "field": {"id": "4", "title": "Dietary preferences"},
                "type": "choices",
                "choices": [
                    {"label": "Vegetarian"},
                    {"label": "Low carb"}
                ]
            },
            {
                "field": {"id": "5", "title": "Activity level"},
                "type": "choice",
                "choice": {"label": "Moderately active"}
            }
        ]
    
    elif form_type == "lead":
        base_payload["form_response"]["answers"] = [
            {
                "field": {"id": "1", "title": "Company name"},
                "type": "text",
                "text": "TechCorp Solutions"
            },
            {
                "field": {"id": "2", "title": "Your role"},
                "type": "text",
                "text": "CTO"
            },
            {
                "field": {"id": "3", "title": "Budget range"},
                "type": "choice",
                "choice": {"label": "$25,000 - $50,000"}
            },
            {
                "field": {"id": "4", "title": "Timeline"},
                "type": "choice",
                "choice": {"label": "Within 3 months"}
            },
            {
                "field": {"id": "5", "title": "Current challenges"},
                "type": "text",
                "text": "Need better analytics and reporting tools for our customer data"
            }
        ]
    
    elif form_type == "event":
        base_payload["form_response"]["answers"] = [
            {
                "field": {"id": "1", "title": "Full name"},
                "type": "text",
                "text": "John Doe"
            },
            {
                "field": {"id": "2", "title": "Email"},
                "type": "email",
                "email": "john.doe@example.com"
            },
            {
                "field": {"id": "3", "title": "Event"},
                "type": "text",
                "text": "FormFlow AI Launch Event"
            },
            {
                "field": {"id": "4", "title": "Will you attend?"},
                "type": "choice",
                "choice": {"label": "Yes, I'll be there!"}
            },
            {
                "field": {"id": "5", "title": "Dietary requirements"},
                "type": "text",
                "text": "Vegetarian"
            }
        ]
    
    return base_payload

def test_webhook(webhook_url, form_type="diet", with_signature=False, webhook_secret=None):
    """Test webhook with different payload types"""
    
    print(f"🧪 Testing webhook: {webhook_url}")
    print(f"📋 Form type: {form_type}")
    print(f"🔐 Signature: {'enabled' if with_signature else 'disabled'}")
    print("-" * 50)
    
    # Create test payload
    payload_data = create_test_payload(form_type)
    payload_json = json.dumps(payload_data, indent=2)
    
    print("📤 Sending payload:")
    print(payload_json[:500] + "..." if len(payload_json) > 500 else payload_json)
    print("-" * 50)
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Typeform-Webhook/1.0"
    }
    
    # Add signature if requested
    if with_signature and webhook_secret:
        signature = create_signature(payload_json, webhook_secret)
        headers["Typeform-Signature"] = signature
        print(f"🔐 Added signature: {signature[:20]}...")
    
    try:
        # Send request
        response = requests.post(
            webhook_url,
            data=payload_json,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print("📥 Response Body:")
            print(json.dumps(response_data, indent=2))
            
            if response.status_code == 200 and "dashboard_url" in response_data:
                print(f"\n✅ Success! Dashboard URL: {response_data['dashboard_url']}")
                
                # Test dashboard access
                dashboard_token = response_data.get("dashboard_url", "").split("/")[-1]
                if dashboard_token:
                    dashboard_url = webhook_url.replace("/api/v1/webhooks/typeform", f"/api/v1/dashboards/view/{dashboard_token}")
                    print(f"🎯 Dashboard direct link: {dashboard_url}")
            
        except json.JSONDecodeError:
            print("📥 Response Body (non-JSON):")
            print(response.text)
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Main function to run webhook tests"""
    
    # Default webhook URL (change this to your ngrok or deployed URL)
    default_url = "http://localhost:8000/api/v1/webhooks/typeform"
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print("🚀 FormFlow AI Webhook Tester")
    print("=" * 50)
    
    # Test different form types
    form_types = ["diet", "lead", "event"]
    
    for form_type in form_types:
        print(f"\n🧪 Testing {form_type} form...")
        success = test_webhook(webhook_url, form_type)
        
        if success:
            print(f"✅ {form_type.title()} form test passed!")
        else:
            print(f"❌ {form_type.title()} form test failed!")
        
        print("-" * 50)
    
    # Test with signature (if secret provided)
    webhook_secret = input("\n🔐 Enter webhook secret for signature test (or press Enter to skip): ").strip()
    if webhook_secret:
        print("\n🔐 Testing with signature verification...")
        success = test_webhook(webhook_url, "diet", with_signature=True, webhook_secret=webhook_secret)
        
        if success:
            print("✅ Signature verification test passed!")
        else:
            print("❌ Signature verification test failed!")
    
    print("\n🎉 Webhook testing completed!")
    print(f"\n💡 Tips:")
    print(f"   - Use ngrok to expose local server: ngrok http 8000")
    print(f"   - Your webhook URL: {webhook_url}")
    print(f"   - Configure this URL in your Typeform webhook settings")
    print(f"   - Check dashboard at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()