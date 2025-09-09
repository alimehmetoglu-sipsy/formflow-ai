# FormFlow AI - Webhook Specifications

## Overview
FormFlow AI supports three types of webhooks to receive form submissions and automatically generate AI-powered dashboards.

---

## 🔗 Typeform Webhook

### Setup
1. Go to your Typeform → Connect panel
2. Add webhook with URL: `https://yourapi.com/api/v1/webhooks/typeform`
3. Select "Response completed" event
4. Optional: Add webhook secret for signature verification

### Headers
```
Content-Type: application/json
User-Agent: Typeform/1.0
Typeform-Signature: sha256=<hmac_signature>  # if secret configured
```

### Payload Format
```json
{
  "event_id": "LtWXD3crgy",
  "event_type": "form_response", 
  "form_response": {
    "form_id": "lT4Z3j",
    "token": "a3a12ec67a1365927098a606107fbc15",
    "landed_at": "2018-01-01T12:00:00Z",
    "submitted_at": "2018-01-01T12:02:00Z",
    "definition": {
      "id": "lT4Z3j",
      "title": "Satisfaction Survey",
      "fields": [
        {
          "id": "DlXFaesGBpoF",
          "title": "What's your goal?",
          "type": "short_text",
          "ref": "readable_ref_goal"
        }
      ]
    },
    "answers": [
      {
        "type": "text",
        "text": "Lose weight and get fit",
        "field": {
          "id": "DlXFaesGBpoF",
          "type": "short_text",
          "ref": "readable_ref_goal"
        }
      },
      {
        "type": "choice",
        "choice": {
          "label": "Male"
        },
        "field": {
          "id": "SMEUb7VJz92Q",
          "type": "multiple_choice",
          "ref": "readable_ref_gender"
        }
      },
      {
        "type": "number",
        "number": 25,
        "field": {
          "id": "JwWggjAKtOkA",
          "type": "number",
          "ref": "readable_ref_age" 
        }
      },
      {
        "type": "email",
        "email": "test@example.com",
        "field": {
          "id": "KoJxDM3c6x8h",
          "type": "email",
          "ref": "readable_ref_email"
        }
      }
    ]
  }
}
```

### Response Expected
```json
{
  "status": "success",
  "message": "Webhook received and processing started",
  "dashboard_url": "/dashboard/view/a3a12ec67a1365927098a606107fbc15"
}
```

### Common Answer Types
```json
{
  "type": "text", 
  "text": "Free text response"
}

{
  "type": "choice",
  "choice": {
    "label": "Selected Option"
  }
}

{
  "type": "choices", 
  "choices": {
    "labels": ["Option 1", "Option 2"]
  }
}

{
  "type": "number",
  "number": 42
}

{
  "type": "email",
  "email": "user@example.com"
}

{
  "type": "url",
  "url": "https://example.com"
}

{
  "type": "phone_number", 
  "phone_number": "+1234567890"
}

{
  "type": "date",
  "date": "2025-01-01"
}

{
  "type": "boolean",
  "boolean": true
}

{
  "type": "payment",
  "payment": {
    "amount": "15.00",
    "last4": "1234", 
    "name": "John Doe"
  }
}

{
  "type": "file_url",
  "file_url": "https://api.typeform.com/forms/xyz/responses/files/abc/image.jpg"
}
```

---

## 📋 Google Forms Webhook

### Setup (Requires Google Apps Script)
1. Open your Google Form → Script Editor  
2. Add the provided Apps Script code
3. Deploy as web app with access for "Anyone"
4. Copy webhook URL and configure in FormFlow AI

### Apps Script Code
```javascript
function onFormSubmit(e) {
  const form = FormApp.getActiveForm();
  const formResponse = e.response;
  
  // FormFlow AI webhook URL  
  const webhookUrl = 'https://yourapi.com/api/v1/webhooks/google-forms';
  
  // Get form responses
  const itemResponses = formResponse.getItemResponses();
  const responses = {};
  
  itemResponses.forEach(itemResponse => {
    const question = itemResponse.getItem().getTitle();
    const answer = itemResponse.getResponse();
    responses[question] = answer;
  });
  
  // Prepare payload
  const payload = {
    formId: form.getId(),
    formTitle: form.getTitle(),
    responseId: formResponse.getId(),
    timestamp: formResponse.getTimestamp().toISOString(),
    respondentEmail: formResponse.getRespondentEmail(),
    responses: responses
  };
  
  // Send webhook
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(webhookUrl, options);
  } catch (error) {
    console.log('Webhook error:', error);
  }
}
```

### Payload Format  
```json
{
  "formId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "formTitle": "Health & Fitness Survey",
  "responseId": "2_ABaOnu_TZeHJTCjInJa3oKxtg0jw9D8bHBvJHN8QxY",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "respondentEmail": "respondent@example.com",
  "responses": {
    "What is your primary fitness goal?": "Weight loss",
    "Current weight (kg)": "75",
    "Target weight (kg)": "65", 
    "Age": "28",
    "Gender": "Female",
    "Activity level": "Moderately active",
    "Dietary restrictions": "Vegetarian",
    "Email address": "sarah@example.com"
  }
}
```

### Trigger Setup
Add this to your Apps Script to set up the trigger:
```javascript
function createTrigger() {
  const form = FormApp.getActiveForm();
  ScriptApp.newTrigger('onFormSubmit')
    .source(form)
    .onFormSubmit()
    .create();
}
```

---

## 🔧 Custom Webhook (Universal)

### Overview
Custom webhooks allow integration with any form platform using configurable field mapping with JSONPath expressions.

### Supported Platforms (with Presets)
- **JotForm**
- **Microsoft Forms** 
- **SurveyMonkey**
- **Airtable Forms**
- **Cognito Forms**
- **WPForms**
- **Custom** (manual configuration)

### Setup Process
1. Create webhook configuration via API or UI
2. Configure field mappings using JSONPath
3. Get unique webhook URL with token
4. Configure in your form platform

### Webhook URL Format
```
POST https://yourapi.com/api/v1/webhooks/custom/{webhook_token}
```

### Headers (Optional)
```
Content-Type: application/json
X-Signature: <hmac_signature>           # Optional signature verification
X-Hub-Signature-256: <github_style>     # GitHub-style signature  
Signature: <custom_signature>           # Platform-specific signature
```

### Field Mapping Configuration
```json
{
  "webhook_config_id": "config_uuid",
  "name": "JotForm Integration",
  "platform": "jotform",
  "field_mappings": {
    "form_title": "$.formTitle",
    "submission_id": "$.submissionID", 
    "submitted_at": "$.createdAt",
    "respondent_name": "$.answers['3'].answer",
    "respondent_email": "$.answers['5'].answer",
    "respondent_phone": "$.answers['7'].answer",
    "custom_field_1": "$.answers['9'].answer"
  }
}
```

### Platform-Specific Payloads

#### JotForm
```json
{
  "submissionID": "4567890123",
  "formID": "203065495", 
  "ip": "192.168.1.1",
  "createdAt": "2025-01-01 12:00:00",
  "status": "ACTIVE",
  "new": "1",
  "flag": "0", 
  "formTitle": "Contact Form",
  "answers": {
    "3": {
      "name": "name",
      "order": "1",
      "text": "Name",
      "type": "control_textbox",
      "answer": "John Doe"
    },
    "5": {
      "name": "email", 
      "order": "2",
      "text": "Email",
      "type": "control_email",
      "answer": "john@example.com"
    }
  }
}
```

#### Microsoft Forms  
```json
{
  "eventType": "Microsoft.Forms.ResponseAdded",
  "subject": "/forms('abc123')/responses('xyz789')",
  "eventTime": "2025-01-01T12:00:00Z",
  "data": {
    "responseId": "xyz789",
    "formId": "abc123",
    "formName": "Customer Survey",
    "submittedDate": "2025-01-01T12:00:00Z",
    "responses": [
      {
        "questionId": "q1",
        "question": "What is your name?",
        "answer": "Jane Smith"
      },
      {
        "questionId": "q2", 
        "question": "Email address?",
        "answer": "jane@example.com"
      }
    ]
  }
}
```

#### SurveyMonkey
```json
{
  "survey_title": "Customer Satisfaction",
  "response_id": "resp_12345",
  "date_created": "2025-01-01T12:00:00+00:00",
  "date_modified": "2025-01-01T12:00:00+00:00",
  "response_status": "completed", 
  "pages": [
    {
      "id": "page1",
      "questions": [
        {
          "id": "q1",
          "heading": "How satisfied are you?",
          "answers": [
            {
              "choice_id": "1234",
              "simple_text": "Very satisfied"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Custom Platform Example
```json
{
  "id": "sub_12345",
  "form_title": "Lead Generation Form", 
  "timestamp": "2025-01-01T12:00:00Z",
  "source": "website",
  "data": {
    "name": "Mike Johnson",
    "email": "mike@company.com", 
    "company": "TechCorp Inc",
    "phone": "+1-555-0199",
    "budget": "$10,000 - $50,000",
    "timeline": "Within 3 months",
    "message": "Looking for enterprise solution"
  }
}
```

### JSONPath Mapping Examples
```json
{
  "form_title": "$.formTitle",                    // Direct field
  "submission_id": "$.submissionID",             // Direct field  
  "submitted_at": "$.createdAt",                 // Date field
  "respondent_name": "$.answers['3'].answer",    // Nested object by key
  "respondent_email": "$.data.email",            // Nested object
  "budget_range": "$.responses[?(@.question == 'Budget')].answer",  // Filter by condition
  "all_answers": "$.answers.*.answer",           // All answer values
  "question_count": "$.answers.length"           // Array length
}
```

### Response Format
All webhook endpoints return:
```json
{
  "status": "success",
  "message": "Webhook received and processing started", 
  "submission_id": "submission_uuid",
  "dashboard_url": "/dashboard/view/unique_token"
}
```

### Error Responses
```json
{
  "status": "error",
  "message": "Invalid webhook token",
  "code": "WEBHOOK_NOT_FOUND"
}

{
  "status": "error", 
  "message": "Signature verification failed",
  "code": "INVALID_SIGNATURE"
}

{
  "status": "error",
  "message": "Field mapping failed: Invalid JSONPath expression",
  "code": "MAPPING_ERROR" 
}
```

---

## 🔐 Security Features

### Signature Verification
Each platform supports signature verification:

#### Typeform (SHA256 HMAC)
```javascript
const crypto = require('crypto');
const signature = req.headers['typeform-signature'];
const payload = JSON.stringify(req.body);
const expectedSignature = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');
```

#### Custom Webhook (Configurable)
```javascript
// GitHub-style (sha256=)  
const githubSignature = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

// Simple HMAC
const simpleSignature = crypto
  .createHmac('sha256', secret)  
  .update(payload)
  .digest('hex');
```

### IP Allowlisting
Configure allowed IP ranges for webhook sources:
```json
{
  "allowed_ips": [
    "192.168.1.0/24", 
    "10.0.0.0/8",
    "typeform-webhook-ips"
  ]
}
```

### Rate Limiting
Webhooks are rate limited to prevent abuse:
- **Free Plan**: 100 webhooks/hour
- **Pro Plan**: 1000 webhooks/hour  
- **Business Plan**: 10000 webhooks/hour

---

## 📊 Processing Pipeline

1. **Webhook Received** → Verify signature & rate limits
2. **Field Mapping** → Extract data using JSONPath
3. **AI Processing** → GPT-4 analyzes responses  
4. **Template Selection** → Choose best dashboard template
5. **Dashboard Generation** → Create HTML dashboard
6. **Notification** → Send confirmation (optional)

### Processing Time
- **Typical**: 15-45 seconds
- **Complex forms**: 1-2 minutes
- **Timeout**: 5 minutes maximum

---

## 🧪 Testing Webhooks

### Local Development  
Use ngrok for local webhook testing:
```bash
# Start your local server
npm run dev  # or python manage.py runserver

# In another terminal
ngrok http 8000

# Use ngrok URL in form platform:
# https://abc123.ngrok.io/api/v1/webhooks/typeform
```

### Testing Tools
- **Webhook.site** - Capture and inspect webhooks
- **ngrok** - Expose local server to internet  
- **Postman** - Manual webhook testing
- **curl** - Command line testing

### Sample cURL Commands
```bash
# Test Typeform webhook
curl -X POST http://localhost:8000/api/v1/webhooks/typeform \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test123",
    "event_type": "form_response", 
    "form_response": {
      "token": "test_token_123",
      "definition": {"title": "Test Form"},
      "answers": [{"type": "text", "text": "Test answer"}]
    }
  }'

# Test custom webhook  
curl -X POST http://localhost:8000/api/v1/webhooks/custom/your_token \
  -H "Content-Type: application/json" \
  -d '{
    "form_title": "Test Form",
    "data": {"name": "Test User", "email": "test@example.com"}
  }'
```

---

## 📝 Troubleshooting

### Common Issues
1. **Webhook not triggering** → Check URL and form configuration
2. **Signature verification fails** → Verify secret key matches  
3. **Dashboard not generated** → Check logs for AI processing errors
4. **Field mapping errors** → Validate JSONPath expressions
5. **Rate limit exceeded** → Implement exponential backoff

### Debug Checklist
- [ ] Webhook URL is correct and accessible
- [ ] Form platform is configured to send POST requests
- [ ] Content-Type header is `application/json`
- [ ] Payload structure matches expected format
- [ ] Signature verification is working (if enabled)
- [ ] Server logs show incoming requests
- [ ] Database shows form submissions being created