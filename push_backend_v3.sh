#!/bin/bash

# FormFlow AI - Push Backend Docker Image v3

echo "🚀 Pushing Backend Docker Image v3 to Artifact Registry"
echo "========================================"

# Authenticate Docker with GCP
echo "1️⃣ Authenticating Docker with GCP..."
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin europe-west1-docker.pkg.dev

# Push the image
echo "2️⃣ Pushing backend:v3..."
docker push europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:v3

# Deploy to Cloud Run
echo "3️⃣ Deploying backend v3 to Cloud Run..."
gcloud run deploy formflow-backend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:v3 \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,DEBUG=False,APP_NAME=FormFlow_AI,VERSION=1.0.0,DATABASE_URL=postgresql://formflow:formflow123@localhost:5432/formflow_db,REDIS_URL=redis://localhost:6379,SECRET_KEY=your-secret-key-here-change-in-production,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30" \
  --set-secrets="OPENAI_API_KEY=openai_api_key:latest,RESEND_API_KEY=resend_api_key:latest,LEMONSQUEEZY_API_KEY=lemonsqueezy_api_key:latest"

echo ""
echo "✅ Done! Check the deployment status."