// FormFlow AI - Google Forms Integration Script (FIXED)
// Bu scripti Google Apps Script Editor'e yapıştırın

function onFormSubmit(e) {
  try {
    // Form bilgilerini al
    var form = FormApp.getActiveForm();
    var formId = form.getId();
    var formTitle = form.getTitle();
    
    // Response'u al - e.response kontrolü
    var response = e ? e.response : null;
    
    // Eğer response yoksa, son response'u al
    if (!response) {
      var responses = form.getResponses();
      if (responses.length > 0) {
        response = responses[responses.length - 1];
      } else {
        console.error('No responses found');
        return;
      }
    }
    
    // Tüm yanıtları topla
    var itemResponses = response.getItemResponses();
    var formResponses = [];
    
    for (var i = 0; i < itemResponses.length; i++) {
      var itemResponse = itemResponses[i];
      formResponses.push({
        question: itemResponse.getItem().getTitle(),
        answer: String(itemResponse.getResponse())
      });
    }
    
    // Webhook verisini hazırla
    var webhookData = {
      form_id: formId,
      form_title: formTitle,
      response_id: response.getId() || 'response_' + new Date().getTime(),
      timestamp: new Date().toISOString(),
      responses: formResponses
    };
    
    // FormFlow AI webhook URL'si
    var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=5316def1-a2a3-4622-9c78-920d88d907fe';
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(webhookData),
      'muteHttpExceptions': true
    };
    
    console.log('Sending webhook data:', JSON.stringify(webhookData));
    
    var httpResponse = UrlFetchApp.fetch(webhookUrl, options);
    console.log('✅ Webhook response:', httpResponse.getContentText());
    console.log('Status code:', httpResponse.getResponseCode());
    
  } catch(error) {
    console.error('❌ Error in onFormSubmit:', error.toString());
    console.error('Stack:', error.stack);
  }
}

// Manuel test için - son form response'unu gönderir
function sendLastResponse() {
  try {
    var form = FormApp.getActiveForm();
    var responses = form.getResponses();
    
    if (responses.length === 0) {
      console.log('No responses found');
      return;
    }
    
    // Son response'u al
    var response = responses[responses.length - 1];
    
    // onFormSubmit'i manuel çağır
    onFormSubmit({response: response});
    
  } catch(error) {
    console.error('Error in sendLastResponse:', error.toString());
  }
}

// Trigger kurulum fonksiyonu
function setupFormTrigger() {
  try {
    var form = FormApp.getActiveForm();
    
    // Mevcut trigger'ları kontrol et
    var triggers = ScriptApp.getProjectTriggers();
    
    // Eski trigger'ları temizle
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === 'onFormSubmit') {
        ScriptApp.deleteTrigger(triggers[i]);
        console.log('Old trigger removed');
      }
    }
    
    // Yeni trigger oluştur
    ScriptApp.newTrigger('onFormSubmit')
      .forForm(form)
      .onFormSubmit()
      .create();
    
    console.log('✅ FormFlow AI trigger kuruldu!');
    return 'Trigger successfully created';
    
  } catch(error) {
    console.error('Error in setupFormTrigger:', error.toString());
    return error.toString();
  }
}

// Test fonksiyonu
function testWebhook() {
  try {
    // Test verisi
    var testData = {
      form_id: 'test_form_' + new Date().getTime(),
      form_title: 'Test Form',
      response_id: 'test_response_' + new Date().getTime(),
      timestamp: new Date().toISOString(),
      responses: [
        {
          question: 'Test Question',
          answer: 'Test Answer'
        }
      ]
    };
    
    var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=5316def1-a2a3-4622-9c78-920d88d907fe';
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(testData),
      'muteHttpExceptions': true
    };
    
    console.log('Sending test data:', JSON.stringify(testData));
    
    var response = UrlFetchApp.fetch(webhookUrl, options);
    console.log('Test response:', response.getContentText());
    console.log('Status code:', response.getResponseCode());
    
    return response.getContentText();
    
  } catch(error) {
    console.error('Test error:', error.toString());
    return error.toString();
  }
}