# FormFlow AI - API Endpoints Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "plan_type": "free"
  }
}
```

### Login User  
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com", 
  "password": "securepassword"
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

---

## 🔗 Webhook Endpoints

### Typeform Webhook Receiver
```http
POST /api/v1/webhooks/typeform
Content-Type: application/json
Typeform-Signature: sha256=<signature>

{
  "event_id": "event_123",
  "event_type": "form_response",
  "form_response": {
    "form_id": "form_abc123",
    "token": "response_token_xyz",
    "submitted_at": "2025-01-01T10:00:00Z",
    "definition": {
      "title": "Customer Survey"
    },
    "answers": [
      {
        "field": {"id": "1", "title": "What's your goal?"},
        "type": "text",
        "text": "Lose weight"
      }
    ]
  }
}
```

### Google Forms Webhook Receiver
```http
POST /api/v1/webhooks/google-forms
Content-Type: application/json

{
  "formId": "1a2b3c4d5e",
  "responseId": "response_123", 
  "timestamp": "2025-01-01T10:00:00.000Z",
  "responses": {
    "Question 1": "Answer 1",
    "Question 2": "Answer 2"
  }
}
```

### Custom Webhook Receiver
```http
POST /api/v1/webhooks/custom/{webhook_token}
Content-Type: application/json
X-Signature: <optional_signature>

{
  "id": "sub_12345",
  "form_title": "Contact Form",
  "timestamp": "2024-01-15T12:00:00Z", 
  "data": {
    "name": "Bob Smith",
    "email": "bob@company.com",
    "message": "Interested in your services"
  }
}
```

### List Webhook Configurations
```http
GET /api/v1/webhooks/configs
Authorization: Bearer <token>
```

### Create Webhook Configuration
```http
POST /api/v1/webhooks/configs
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My JotForm Webhook",
  "platform": "jotform",
  "field_mappings": {
    "form_title": "$.form.title",
    "respondent_name": "$.answers.name",
    "respondent_email": "$.answers.email"
  }
}
```

### Get Webhook Logs
```http
GET /api/v1/webhooks/configs/{config_id}/logs?limit=10
Authorization: Bearer <token>
```

---

## 📊 Dashboard Endpoints

### View Public Dashboard
```http
GET /api/v1/dashboards/view/{token}
```
Returns HTML dashboard for public viewing.

### Get Dashboard Data
```http  
GET /api/v1/dashboards/{submission_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "dashboard_uuid",
  "submission_id": "submission_uuid", 
  "template_type": "diet_plan",
  "ai_generated_content": {
    "insights": ["Insight 1", "Insight 2"],
    "recommendations": ["Rec 1", "Rec 2"]
  },
  "view_count": 42,
  "created_at": "2025-01-01T10:00:00Z",
  "dashboard_url": "/dashboard/view/token_xyz"
}
```

### List User Dashboards
```http
GET /api/v1/dashboards/user/me?skip=0&limit=20
Authorization: Bearer <token>
```

### List All Dashboards (Admin)
```http
GET /api/v1/dashboards/?skip=0&limit=10
Authorization: Bearer <admin_token>
```

---

## 🎨 Template Endpoints

### Get Available Templates
```http
GET /api/v1/templates/?category=health&is_premium=false
```

**Response:**
```json
{
  "templates": [
    {
      "id": "template_uuid",
      "name": "Diet Plan",
      "description": "Personalized nutrition dashboard",
      "category": "health", 
      "is_premium": false,
      "preview_image_url": "https://...",
      "usage_count": 1250
    }
  ]
}
```

### Get Template Details
```http
GET /api/v1/templates/{template_id}
```

### Create Custom Template
```http
POST /api/v1/templates/custom
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Custom Template",
  "description": "Custom dashboard template",
  "template_data": {
    "widgets": [
      {"type": "metric", "title": "Total Score"}
    ]
  }
}
```

### List User's Custom Templates
```http
GET /api/v1/templates/custom/my
Authorization: Bearer <token>
```

### Apply Template to Dashboard
```http
POST /api/v1/templates/apply/{dashboard_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": "template_uuid"
}
```

---

## 👤 User Management Endpoints  

### Get User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

### Update User Password
```http
POST /api/v1/users/me/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

### Get User Statistics  
```http
GET /api/v1/users/me/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_dashboards": 15,
  "total_views": 342,
  "forms_connected": 3,
  "plan_type": "pro",
  "usage_this_month": {
    "dashboards_created": 5,
    "api_calls": 150
  }
}
```

### Delete User Account
```http
DELETE /api/v1/users/me
Authorization: Bearer <token>
```

---

## 💳 Payment/Billing Endpoints

### Get Available Plans
```http
GET /api/v1/billing/plans
```

**Response:**
```json
{
  "plans": [
    {
      "name": "free",
      "price": 0,
      "features": ["3 forms", "100 submissions/month"],
      "limits": {
        "forms": 3,
        "submissions_per_month": 100
      }
    },
    {
      "name": "pro", 
      "price": 1700, // cents
      "features": ["Unlimited forms", "1000 submissions/month"],
      "limits": {
        "forms": -1,
        "submissions_per_month": 1000
      }
    }
  ]
}
```

### Create Checkout Session
```http
POST /api/v1/billing/checkout  
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "pro",
  "success_url": "https://yoursite.com/success",
  "cancel_url": "https://yoursite.com/cancel"
}
```

### Get Current Subscription
```http
GET /api/v1/billing/subscription
Authorization: Bearer <token>
```

### Cancel Subscription
```http  
POST /api/v1/billing/cancel-subscription
Authorization: Bearer <token>
```

### LemonSqueezy Webhook (Internal)
```http
POST /api/v1/billing/webhook/lemonsqueezy
Content-Type: application/json
X-Signature: <lemonsqueezy_signature>

{
  "meta": {
    "event_name": "subscription_created"
  },
  "data": {
    "attributes": {
      "customer_id": 123,
      "status": "active"
    }
  }
}
```

---

## 🚀 Onboarding Endpoints

### Get Onboarding Status
```http
GET /api/v1/onboarding/status
Authorization: Bearer <token>
```

### Connect Typeform
```http
POST /api/v1/onboarding/typeform-connect
Authorization: Bearer <token>
Content-Type: application/json

{
  "api_key": "tfp_xxx"
}
```

### Select Template
```http
POST /api/v1/onboarding/select-template
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": "template_uuid"
}
```

### Complete Onboarding
```http
POST /api/v1/onboarding/complete
Authorization: Bearer <token>
```

---

## 🏥 Health & Monitoring

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T10:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### Readiness Check  
```http
GET /api/v1/ready
```

---

## ⚠️ Error Responses

All endpoints return consistent error formats:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "validation_error"
}
```

### Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request / Validation Error
- `401` - Unauthorized / Invalid Token
- `403` - Forbidden / Insufficient Permissions  
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Rate Limited
- `500` - Internal Server Error

---

## 🔒 Rate Limiting

API endpoints are rate limited based on user plan:

- **Free Plan**: 100 requests/hour
- **Pro Plan**: 1000 requests/hour  
- **Business Plan**: 10000 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

---

## 📝 API Versioning

Current API version: **v1**

All endpoints are prefixed with `/api/v1/`

Future versions will be available at `/api/v2/` etc.

---

## 🔧 Development & Testing

### API Documentation (Interactive)
- **Swagger UI**: http://localhost:8000/docs  
- **ReDoc**: http://localhost:8000/redoc

### Webhook Testing
Use tools like ngrok for local webhook testing:
```bash
ngrok http 8000
# Your webhook URL: https://xxx.ngrok.io/api/v1/webhooks/typeform
```