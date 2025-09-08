#!/bin/bash

# FormFlow AI - Create Secrets and Deploy to Cloud Run

echo "========================================="
echo "FormFlow AI - Secret Creation & Deployment"
echo "========================================="

# Set project
gcloud config set project formflow-ai-prod

# Create secrets
echo ""
echo "1️⃣ Creating openai_api_key..."
echo -n "YOUR_OPENAI_API_KEY_HERE" | gcloud secrets create openai_api_key --data-file=- || echo "Already exists"

echo ""
echo "2️⃣ Creating lemonsqueezy_api_key..."
echo -n "YOUR_LEMONSQUEEZY_API_KEY_HERE" | gcloud secrets create lemonsqueezy_api_key --data-file=- || echo "Already exists"

echo ""
echo "3️⃣ Creating resend_api_key..."
echo -n "YOUR_RESEND_API_KEY_HERE" | gcloud secrets create resend_api_key --data-file=- || echo "Already exists"

echo ""
echo "✅ All secrets created/verified!"
echo ""
echo "========================================="
echo "4️⃣ Deploying Backend to Cloud Run..."
echo "========================================="

# Deploy backend
gcloud run deploy formflow-backend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,DEBUG=False,APP_NAME=FormFlow_AI,VERSION=1.0.0,DATABASE_URL=postgresql://formflow:formflow123@localhost:5432/formflow_db,REDIS_URL=redis://localhost:6379,SECRET_KEY=your-secret-key-here-change-in-production,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30" \
  --set-secrets="OPENAI_API_KEY=openai_api_key:latest,RESEND_API_KEY=resend_api_key:latest,JWT_SECRET=jwt_secret:latest,LEMONSQUEEZY_API_KEY=lemonsqueezy_api_key:latest"

echo ""
echo "========================================="
echo "5️⃣ Deploying Frontend to Cloud Run..."
echo "========================================="

# Get backend URL
BACKEND_URL=$(gcloud run services describe formflow-backend --region=europe-west1 --format='value(status.url)')

# Deploy frontend
gcloud run deploy formflow-frontend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}"

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""

# Get URLs
FRONTEND_URL=$(gcloud run services describe formflow-frontend --region=europe-west1 --format='value(status.url)')
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔌 Backend URL: $BACKEND_URL"
echo ""
echo "🎯 Test your application at: $FRONTEND_URL"
echo "📚 API Documentation at: $BACKEND_URL/docs"