import pytest
from fastapi.testclient import TestClient
import json
import hmac
import hashlib
from unittest.mock import patch, AsyncMock
from app.main import app
from app.config import settings

client = TestClient(app)

def create_signature(payload: str, secret: str) -> str:
    """Create HMAC signature for testing"""
    return "sha256=" + hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

def test_webhook_endpoint_accessible():
    """Test that webhook endpoint is accessible"""
    response = client.get("/api/v1/webhooks/test")
    assert response.status_code == 200
    assert "webhook_url" in response.json()

def test_typeform_webhook_valid_payload():
    """Test webhook with valid Typeform payload"""
    webhook_data = {
        "event_id": "test123",
        "event_type": "form_response",
        "form_response": {
            "form_id": "abc123",
            "token": "unique_token_123",
            "submitted_at": "2025-01-01T10:00:00Z",
            "definition": {
                "title": "Diet Plan Form"
            },
            "answers": [
                {
                    "field": {"id": "1", "title": "What is your goal?"},
                    "type": "text",
                    "text": "Lose 5kg in 2 months"
                },
                {
                    "field": {"id": "2", "title": "Current weight"},
                    "type": "number",
                    "number": 75
                }
            ]
        }
    }
    
    payload = json.dumps(webhook_data)
    
    with patch('app.api.v1.webhooks.process_submission') as mock_process:
        response = client.post(
            "/api/v1/webhooks/typeform",
            content=payload,
            headers={"Content-Type": "application/json"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dashboard_url" in data
    assert "submission_id" in data

def test_typeform_webhook_with_signature():
    """Test webhook with signature verification"""
    webhook_data = {
        "event_id": "test456",
        "event_type": "form_response",
        "form_response": {
            "form_id": "def456",
            "token": "unique_token_456",
            "submitted_at": "2025-01-01T11:00:00Z",
            "definition": {"title": "Test Form"},
            "answers": []
        }
    }
    
    payload = json.dumps(webhook_data)
    secret = "test_secret"
    signature = create_signature(payload, secret)
    
    with patch.object(settings, 'TYPEFORM_WEBHOOK_SECRET', secret):
        with patch('app.api.v1.webhooks.process_submission') as mock_process:
            response = client.post(
                "/api/v1/webhooks/typeform",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "Typeform-Signature": signature
                }
            )
    
    assert response.status_code == 200

def test_typeform_webhook_invalid_signature():
    """Test webhook with invalid signature"""
    webhook_data = {
        "event_id": "test789",
        "event_type": "form_response",
        "form_response": {
            "form_id": "ghi789",
            "token": "unique_token_789",
            "submitted_at": "2025-01-01T12:00:00Z",
            "definition": {"title": "Test Form"},
            "answers": []
        }
    }
    
    payload = json.dumps(webhook_data)
    
    with patch.object(settings, 'TYPEFORM_WEBHOOK_SECRET', "test_secret"):
        response = client.post(
            "/api/v1/webhooks/typeform",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "Typeform-Signature": "sha256=invalid_signature"
            }
        )
    
    assert response.status_code == 401

def test_typeform_webhook_invalid_json():
    """Test webhook with invalid JSON"""
    response = client.post(
        "/api/v1/webhooks/typeform",
        content="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400

def test_typeform_webhook_duplicate_submission():
    """Test webhook with duplicate submission token"""
    webhook_data = {
        "event_id": "test999",
        "event_type": "form_response",
        "form_response": {
            "form_id": "duplicate_test",
            "token": "duplicate_token",
            "submitted_at": "2025-01-01T13:00:00Z",
            "definition": {"title": "Duplicate Test"},
            "answers": []
        }
    }
    
    payload = json.dumps(webhook_data)
    
    with patch('app.api.v1.webhooks.process_submission') as mock_process:
        # First submission
        response1 = client.post(
            "/api/v1/webhooks/typeform",
            content=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Duplicate submission
        response2 = client.post(
            "/api/v1/webhooks/typeform",
            content=payload,
            headers={"Content-Type": "application/json"}
        )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response2.json()["status"] == "already_processed"

def test_template_type_detection():
    """Test automatic template type detection"""
    from app.api.v1.webhooks import detect_template_type
    
    # Test diet plan detection
    diet_answers = {
        "goal": "lose weight",
        "current_weight": 75,
        "preferred_meals": "healthy diet"
    }
    assert detect_template_type(diet_answers) == "diet_plan"
    
    # Test lead score detection
    lead_answers = {
        "company": "Tech Corp",
        "budget": "$10,000",
        "timeline": "Q1 implementation"
    }
    assert detect_template_type(lead_answers) == "lead_score"
    
    # Test event registration detection
    event_answers = {
        "event_name": "Conference 2025",
        "attend": "yes",
        "registration": "confirmed"
    }
    assert detect_template_type(event_answers) == "event_registration"
    
    # Test generic fallback
    generic_answers = {
        "random_field": "random value"
    }
    assert detect_template_type(generic_answers) == "generic"

@pytest.mark.asyncio
async def test_ai_processor_mock_data():
    """Test AI processor with mock data when OpenAI is not configured"""
    from app.services.ai_processor import AIProcessor
    
    processor = AIProcessor()  # Will use mock data without API key
    
    # Test diet plan processing
    diet_answers = {"goal": "weight loss", "current_weight": 70}
    result = await processor.process(diet_answers, "diet_plan")
    
    assert "daily_calories" in result
    assert "meal_plan" in result
    assert "shopping_list" in result
    
    # Test lead scoring
    lead_answers = {"company": "Test Corp", "budget": "50k"}
    result = await processor.process(lead_answers, "lead_score")
    
    assert "lead_score" in result
    assert "lead_category" in result
    assert result["lead_score"] >= 0 and result["lead_score"] <= 100

def test_template_engine_rendering():
    """Test template engine HTML generation"""
    from app.services.template_engine import TemplateEngine
    
    engine = TemplateEngine()
    
    # Test diet plan template
    diet_data = {
        "daily_calories": 2000,
        "macro_breakdown": {"protein": 150, "carbs": 200, "fat": 65},
        "meal_plan": {
            "monday": {
                "breakfast": {"meal": "Oatmeal", "calories": 350},
                "lunch": {"meal": "Salad", "calories": 450},
                "dinner": {"meal": "Chicken", "calories": 550}
            }
        },
        "shopping_list": {
            "proteins": ["Chicken", "Fish"],
            "vegetables": ["Broccoli", "Spinach"]
        }
    }
    
    html = engine.render("diet_plan", diet_data)
    assert "2000" in html  # Daily calories
    assert "Oatmeal" in html  # Meal name
    assert "Chicken" in html  # Shopping list item
    
    # Test lead score template
    lead_data = {
        "lead_score": 85,
        "lead_category": "Hot",
        "key_insights": ["Strong budget fit", "Decision maker identified"],
        "recommended_actions": ["Schedule demo", "Send proposal"]
    }
    
    html = engine.render("lead_score", lead_data)
    assert "85" in html  # Score
    assert "Hot" in html  # Category
    assert "Strong budget fit" in html  # Insight