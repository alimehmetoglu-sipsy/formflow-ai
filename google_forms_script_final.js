// FormFlow AI - Google Forms Integration Script
// Bu scripti Google Apps Script Editor'e yapıştırın

function onFormSubmit(e) {
  // Form ve yanıt bilgilerini al
  var form = FormApp.getActiveForm();
  var formId = form.getId();
  var formTitle = form.getTitle();
  var response = e.response;
  
  // Tüm yanıtları topla
  var itemResponses = response.getItemResponses();
  var responses = [];
  
  for (var i = 0; i < itemResponses.length; i++) {
    var itemResponse = itemResponses[i];
    responses.push({
      question: itemResponse.getItem().getTitle(),
      answer: String(itemResponse.getResponse())
    });
  }
  
  // Webhook verisini hazırla
  var webhookData = {
    form_id: formId,
    form_title: formTitle,
    response_id: response.getId(),
    timestamp: new Date().toISOString(),
    responses: responses
  };
  
  // FormFlow AI webhook URL'si - USER ID GÜNCELLENDİ!
  var webhookUrl = 'https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms?user_id=5316def1-a2a3-4622-9c78-920d88d907fe';
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(webhookData),
    'muteHttpExceptions': true
  };
  
  try {
    var httpResponse = UrlFetchApp.fetch(webhookUrl, options);
    console.log('✅ Webhook başarılı:', httpResponse.getContentText());
  } catch(error) {
    console.error('❌ Webhook hatası:', error.toString());
  }
}

// Trigger kurulum fonksiyonu
function setupFormTrigger() {
  var form = FormApp.getActiveForm();
  
  // Mevcut trigger'ları kontrol et
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'onFormSubmit') {
      console.log('Trigger zaten mevcut');
      return;
    }
  }
  
  // Yeni trigger oluştur
  ScriptApp.newTrigger('onFormSubmit')
    .forForm(form)
    .onFormSubmit()
    .create();
  
  console.log('✅ FormFlow AI trigger kuruldu!');
}

// Test fonksiyonu
function testWebhook() {
  // Test verisi
  var testData = {
    form_id: 'test_form_' + new Date().getTime(),
    form_title: 'Test Form',
    response_id: 'test_response_' + new Date().getTime(),
    timestamp: new Date().toISOString(),
    responses: [
      {
        question: 'Ad Soyad',
        answer: 'Test Kullanıcı'
      },
      {
        question: 'E-posta',
        answer: 'test@example.com'
      },
      {
        question: 'Memnuniyet',
        answer: 'Çok Memnun'
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
  
  try {
    var response = UrlFetchApp.fetch(webhookUrl, options);
    console.log('Test sonucu:', response.getContentText());
    console.log('Status:', response.getResponseCode());
    return response.getContentText();
  } catch(e) {
    console.error('Test hatası:', e.toString());
    return e.toString();
  }
}