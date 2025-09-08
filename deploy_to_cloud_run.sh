#!/bin/bash

# FormFlow AI - Complete Cloud Run Deployment Script
# Run this in Google Cloud Shell after cloning from GitHub

set -e

echo "==========================================="
echo "🚀 FormFlow AI - Cloud Run Deployment"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"

# Set project
echo "1️⃣ Setting project..."
gcloud config set project $PROJECT_ID

# Build Backend Docker Image
echo ""
echo "2️⃣ Building Backend Docker Image..."
cd backend
docker build -t europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/backend:latest .

# Authenticate Docker
echo ""
echo "3️⃣ Authenticating Docker..."
gcloud auth configure-docker europe-west1-docker.pkg.dev

# Push Backend Image
echo ""
echo "4️⃣ Pushing Backend Image..."
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/backend:latest

# Deploy Backend
echo ""
echo "5️⃣ Deploying Backend to Cloud Run..."
gcloud run deploy formflow-backend \
  --image europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,DATABASE_URL=sqlite:///./test.db,LEMONSQUEEZY_API_KEY=dummy_key_not_used" \
  --set-secrets="OPENAI_API_KEY=openai_api_key:latest,RESEND_API_KEY=resend_api_key:latest"

# Add IAM policy for Backend
echo ""
echo "6️⃣ Setting Backend IAM Policy..."
gcloud run services add-iam-policy-binding formflow-backend \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker"

# Get Backend URL
BACKEND_URL=$(gcloud run services describe formflow-backend --region=$REGION --format='value(status.url)')
echo "✅ Backend URL: $BACKEND_URL"

# Build Frontend Docker Image
echo ""
echo "7️⃣ Building Frontend Docker Image..."
cd ../frontend
docker build -t europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/frontend:latest .

# Push Frontend Image
echo ""
echo "8️⃣ Pushing Frontend Image..."
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/frontend:latest

# Deploy Frontend
echo ""
echo "9️⃣ Deploying Frontend to Cloud Run..."
gcloud run deploy formflow-frontend \
  --image europe-west1-docker.pkg.dev/$PROJECT_ID/formflow-images/frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}"

# Add IAM policy for Frontend
echo ""
echo "🔟 Setting Frontend IAM Policy..."
gcloud run services add-iam-policy-binding formflow-frontend \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker"

# Get Frontend URL
FRONTEND_URL=$(gcloud run services describe formflow-frontend --region=$REGION --format='value(status.url)')

# Display Results
echo ""
echo "==========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "==========================================="
echo ""
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔌 Backend URL: $BACKEND_URL"
echo ""
echo "📝 Backend API Docs: $BACKEND_URL/docs"
echo "🧪 Backend Health Check: $BACKEND_URL/health"
echo ""
echo "🎉 Your application is now live!"
echo "==========================================="