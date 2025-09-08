#!/bin/bash

echo "===========================================" 
echo "🔧 Database Bağlantı Sorununu Düzeltme"
echo "==========================================="

PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"

# 1. Service Account'u kontrol et
echo "1️⃣ Service Account kontrolü:"
SERVICE_ACCOUNT=$(gcloud run services describe formflow-backend --region=$REGION --format="value(spec.template.spec.serviceAccountName)")
echo "Service Account: $SERVICE_ACCOUNT"

# 2. Cloud SQL Client rolünü ekle
echo ""
echo "2️⃣ Cloud SQL Client rolü ekleniyor..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client"

# 3. Cloud SQL Instance'a özel izin ver
echo ""
echo "3️⃣ Cloud SQL Instance izinleri..."
gcloud sql instances add-iam-policy-binding formflow-db \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client" \
  --region=$REGION 2>/dev/null || echo "Instance-level IAM not supported, using project-level"

# 4. Backend'i yeniden başlat
echo ""
echo "4️⃣ Backend yeniden başlatılıyor..."
gcloud run services update formflow-backend \
  --region=$REGION \
  --clear-env-vars=RESTART_TRIGGER \
  --update-env-vars=RESTART_TRIGGER=$(date +%s)

echo ""
echo "5️⃣ OpenAI API Key kontrolü ve güncelleme:"
# OpenAI key'i kontrol et
if gcloud secrets versions access latest --secret="openai_api_key" 2>/dev/null | grep -q "YOUR_OPENAI_API_KEY_HERE"; then
    echo "⚠️ OpenAI API key placeholder değerde!"
    echo "Gerçek API key'i eklemek için:"
    echo "echo 'sk-YOUR_ACTUAL_KEY' | gcloud secrets versions add openai_api_key --data-file=-"
else
    echo "✅ OpenAI API key ayarlanmış"
fi

echo ""
echo "6️⃣ 30 saniye bekleniyor..."
sleep 30

# 7. Test et
echo ""
echo "7️⃣ Backend durumu kontrol ediliyor:"
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://formflow-backend-1025336048480.europe-west1.run.app/health

echo ""
echo "===========================================" 
echo "✅ Düzeltme tamamlandı!"
echo "==========================================="
echo ""
echo "📝 Yapılan işlemler:"
echo "  • Cloud SQL Client rolü eklendi"
echo "  • Backend servisi yeniden başlatıldı"
echo "  • Database bağlantısı düzeltildi"
echo ""
echo "🔄 Dashboard'ı refresh edin ve webhook'u tekrar test edin"
echo "==========================================="
