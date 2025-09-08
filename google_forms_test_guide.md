# Google Forms Test Kılavuzu

## ✅ Sistem Durumu
- **Apps Script**: Çalışıyor ✓
- **Webhook URL**: https://moody-actors-sin.loca.lt/api/v1/webhooks/google-forms
- **User ID**: 5316def1-a2a3-4622-9c78-920d88d907fe
- **Backend**: Aktif ✓

## 📝 Test İçin Yapılacaklar:

### 1. Google Form'da Yeni Yanıt Gönderin
- Form'u açın: https://docs.google.com/forms/d/e/1FAIpQLScWsfjdmzpg-YuqjIjc7rjZ3PvurkKV9Nu5Y7GBot_KY6gU_w/viewform
- **Farklı** bir seçenek seçin (Option 2 veya yeni soru ekleyin)
- Submit edin

### 2. Apps Script Konsolu Kontrol Edin
Execution log'da göreceksiniz:
- `Sending webhook data: ...`
- `✅ Webhook response: {"status":"success"...}`

### 3. Dashboard'ı Kontrol Edin
- http://localhost:3000/dashboard
- Yeni submission görünecek

## 🔍 Sorun Giderme

### "already_processed" Mesajı Alıyorsanız:
- Aynı form yanıtı tekrar gönderiliyor
- **Çözüm**: Form'a YENİ bir yanıt gönderin

### Webhook Çalışmıyorsa:
Apps Script'te `testWebhook()` fonksiyonunu çalıştırın:
```javascript
function testWebhook() {
  // Test çalıştır
}
```

### Manuel Test:
Apps Script'te `sendLastResponse()` fonksiyonunu çalıştırın:
```javascript
function sendLastResponse() {
  // Son yanıtı gönder
}
```

## 📊 Başarılı Response Örneği:
```json
{
  "status": "success",
  "dashboard_url": "http://localhost:3000/dashboard/xxxxx",
  "submission_id": "xxxxx",
  "message": "Google Forms submission received and processing started",
  "source": "google_forms"
}
```

## 🎯 Özet:
1. Form'a **YENİ** yanıt gönderin
2. Apps Script log'da **success** görün
3. Dashboard'da yeni submission görün

Sistem tamamen hazır ve çalışıyor!