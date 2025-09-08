#!/bin/bash

echo "===========================================" 
echo "🔍 FormFlow AI Backend Kontrolü"
echo "==========================================="

# 1. Backend health check
echo ""
echo "1️⃣ Backend Health Check:"
curl -s http://localhost:8001/health 2>/dev/null || echo "❌ Backend proxy çalışmıyor"

# 2. Cloud Run logs
echo ""
echo "2️⃣ Son Backend Logları (Cloud Run):"
gcloud run logs read formflow-backend \
  --region=europe-west1 \
  --limit=20 \
  --format="value(textPayload)" | grep -E "(ERROR|WARNING|webhook|OpenAI|dashboard)" | head -10

# 3. Database connection test
echo ""
echo "3️⃣ Database Bağlantı Testi:"
gcloud sql instances describe formflow-db \
  --format="get(state)" 2>/dev/null && echo "✅ Cloud SQL aktif" || echo "❌ Cloud SQL erişilemiyor"

# 4. Secret Manager check
echo ""
echo "4️⃣ API Keys Kontrolü:"
gcloud secrets versions access latest --secret="openai_api_key" 2>/dev/null | head -c 10 > /dev/null && echo "✅ OpenAI API key mevcut" || echo "❌ OpenAI API key bulunamadı"
gcloud secrets versions access latest --secret="resend_api_key" 2>/dev/null | head -c 10 > /dev/null && echo "✅ Resend API key mevcut" || echo "❌ Resend API key bulunamadı"

# 5. Test webhook with debug
echo ""
echo "5️⃣ Webhook Debug Testi:"
curl -X POST "http://localhost:8001/api/v1/webhooks/google-forms?user_id=fb6d90e7-a951-4623-b3fe-4be27736d48d" \
  -H "Content-Type: application/json" \
  -d '{"formId":"debug-test","formTitle":"Debug Test","responses":[{"question":"Test","answer":"Test"}]}' \
  -v 2>&1 | grep -E "(< HTTP|< |{)" | head -10

echo ""
echo "==========================================="
echo "✅ Kontrol tamamlandı!"
echo "==========================================="
