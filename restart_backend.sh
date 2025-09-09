#!/bin/bash

echo "===========================================" 
echo "🔄 Backend Yeniden Başlatma"
echo "==========================================="

# Backend'i yeniden başlat (düzgün komut)
echo "Backend yeniden başlatılıyor..."
gcloud run services update formflow-backend \
  --region=europe-west1 \
  --update-env-vars="RESTART_TIME=$(date +%s)"

echo ""
echo "30 saniye bekleniyor..."
sleep 30

# Backend durumunu kontrol et
echo ""
echo "Backend durumu kontrol ediliyor:"
BACKEND_URL="https://formflow-backend-1025336048480.europe-west1.run.app"

# Health check
echo "Health check:"
curl -s "$BACKEND_URL/health" || echo "Health endpoint erişilemiyor"

echo ""
echo "===========================================" 
echo "✅ Backend yeniden başlatıldı!"
echo "==========================================="
