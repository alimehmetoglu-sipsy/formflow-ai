# 🚀 FormFlow AI - Google Cloud Shell Deployment Guide

## Adım 1: Google Cloud Shell'i Aç
1. Tarayıcıda şu adrese git: https://shell.cloud.google.com
2. Google hesabınla giriş yap

## Adım 2: Dosyaları Upload Et
Cloud Shell açıldığında, dosyaları upload etmek için 2 yöntem var:

### Yöntem A: Upload butonu ile (Kolay)
1. Cloud Shell'de sağ üstte "⋮" menüsüne tıkla
2. "Upload" seçeneğini seç
3. `cloud_shell_deploy.sh` dosyasını yükle
4. Terraform klasörünü zip'leyip yükle

### Yöntem B: Git ile (Önerilen)
```bash
# Önce GitHub'a kodları push et, sonra:
git clone https://github.com/yourusername/formflow-ai.git
cd formflow-ai
```

## Adım 3: Deployment Script'ini Çalıştır
```bash
# Script'i executable yap
chmod +x cloud_shell_deploy.sh

# Script'i çalıştır
./cloud_shell_deploy.sh
```

## Adım 4: Terraform Infrastructure Deploy Et
Script tamamlandıktan sonra:

```bash
cd terraform

# Infrastructure'ı deploy et
terraform apply -auto-approve \
  -var="project_id=formflow-ai-prod" \
  -var="region=europe-west1" \
  -var="domain=sipsy.ai" \
  -var="admin_email=admin@sipsy.ai"
```

## Adım 5: Docker Images Build & Deploy
Infrastructure hazır olunca:

```bash
# Backend Docker image
cd ../backend
gcloud builds submit --tag europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest

# Frontend Docker image  
cd ../frontend
gcloud builds submit --tag europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest

# Deploy to Cloud Run
gcloud run deploy formflow-backend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,RESEND_API_KEY=resend-api-key:latest"

gcloud run deploy formflow-frontend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated
```

## Adım 6: DNS Konfigürasyonu
Terraform çıktısından nameserver'ları al:

```bash
terraform output nameservers
```

GoDaddy'de:
1. sipsy.ai domain'ine git
2. DNS Management'a tıkla
3. Nameservers'ı Google Cloud DNS'e değiştir

## 🎯 Kontrol Listesi
- [ ] Google Cloud Shell açıldı
- [ ] Dosyalar upload edildi
- [ ] cloud_shell_deploy.sh çalıştırıldı
- [ ] Terraform infrastructure deploy edildi
- [ ] Docker images build edildi
- [ ] Cloud Run'a deploy edildi
- [ ] DNS nameservers güncellendi

## 📧 API Keys (Script'te otomatik ekleniyor)
- OpenAI API Key ✅
- LemonSqueezy API Key ✅
- Resend API Key ✅

## 🔗 Önemli URL'ler
- Cloud Console: https://console.cloud.google.com
- Cloud Shell: https://shell.cloud.google.com
- Cloud Run: https://console.cloud.google.com/run?project=formflow-ai-prod
- DNS Zone: https://console.cloud.google.com/net-services/dns?project=formflow-ai-prod