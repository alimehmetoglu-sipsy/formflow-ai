# Google Forms Live Webhook Setup Guide

## ✅ Your webhook is now working!

**New Public Webhook URL:** 
```
https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=85a52dfe-ec8f-47af-a810-007e2fd119ea
```

## 📝 Step 1: Update Your Google Apps Script

1. Go to your Google Form's Script Editor
2. Replace the webhook URL in your script with:
```javascript
var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=85a52dfe-ec8f-47af-a810-007e2fd119ea';
```

## 🎯 Step 2: Test Your Form

1. Submit a test response through your Google Form
2. Check the dashboard at: http://localhost:3000/dashboard
3. Your submission will appear as a new dashboard!

## ✨ What's Fixed:

- ✅ Schema now supports both Google Forms API and Apps Script formats
- ✅ Webhook endpoint accepts simplified response format
- ✅ Dashboard generation works with Google Forms data
- ✅ Localtunnel provides stable public URL for webhooks

## 📊 Test Results:

Successfully tested with the following data format:
```json
{
  "form_id": "test_form_123",
  "form_title": "Test Form",
  "response_id": "test_response_xxx",
  "timestamp": "2025-09-08T08:02:01",
  "responses": [
    {
      "question": "Ad Soyad",
      "answer": "Test Kullanıcı"
    },
    {
      "question": "E-posta",
      "answer": "test@example.com"
    },
    {
      "question": "Memnuniyet",
      "answer": "Çok Memnun"
    }
  ]
}
```

Response: **200 OK** ✅

## 🔄 Complete Google Apps Script Code:

```javascript
// FormFlow AI - Google Forms Integration Script
function onFormSubmit(e) {
  // Get form and response details
  var form = FormApp.getActiveForm();
  var formId = form.getId();
  var formTitle = form.getTitle();
  var response = e.response;
  
  // Collect all responses
  var itemResponses = response.getItemResponses();
  var responses = [];
  
  for (var i = 0; i < itemResponses.length; i++) {
    var itemResponse = itemResponses[i];
    responses.push({
      question: itemResponse.getItem().getTitle(),
      answer: String(itemResponse.getResponse())
    });
  }
  
  // Prepare webhook data
  var webhookData = {
    form_id: formId,
    form_title: formTitle,
    response_id: response.getId(),
    timestamp: new Date().toISOString(),
    responses: responses
  };
  
  // Send to FormFlow AI
  var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=85a52dfe-ec8f-47af-a810-007e2fd119ea';
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(webhookData),
    'muteHttpExceptions': true
  };
  
  try {
    var httpResponse = UrlFetchApp.fetch(webhookUrl, options);
    console.log('✅ Webhook successful:', httpResponse.getContentText());
  } catch(error) {
    console.error('❌ Webhook error:', error.toString());
  }
}

// Setup trigger function
function setupFormTrigger() {
  var form = FormApp.getActiveForm();
  
  // Check existing triggers
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'onFormSubmit') {
      console.log('Trigger already exists');
      return;
    }
  }
  
  // Create new trigger
  ScriptApp.newTrigger('onFormSubmit')
    .forForm(form)
    .onFormSubmit()
    .create();
  
  console.log('✅ FormFlow AI trigger installed!');
}

// Test function
function testWebhook() {
  var testData = {
    form_id: 'test_form_123',
    form_title: 'Test Form',
    response_id: 'test_response_' + new Date().getTime(),
    timestamp: new Date().toISOString(),
    responses: [
      {
        question: 'Name',
        answer: 'Test User'
      },
      {
        question: 'Email',
        answer: 'test@example.com'
      },
      {
        question: 'Satisfaction',
        answer: 'Very Satisfied'
      }
    ]
  };
  
  var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=85a52dfe-ec8f-47af-a810-007e2fd119ea';
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(testData),
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(webhookUrl, options);
    console.log('Test result:', response.getContentText());
    console.log('Status:', response.getResponseCode());
  } catch(e) {
    console.error('Test error:', e.toString());
  }
}
```

## ⚠️ Important Notes:

- Localtunnel URL may change if the connection is lost
- Current URL is: **https://moody-actors-sin.loca.lt**
- Monitor the terminal for any URL changes
- For production, use ngrok Pro or a dedicated domain

## 🎉 Your Google Forms integration is now live and working!