#!/bin/bash

# FormFlow AI - Continue Deployment (APIs already enabled)
# Bu scripti Google Cloud Shell'de çalıştır

set -e

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
DOMAIN="sipsy.ai"

echo "🚀 FormFlow AI Deployment - Continuing..."
echo "======================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Domain: $DOMAIN"
echo ""

# Step 1: Create Terraform backend bucket
echo "1️⃣ Creating Terraform state bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state || echo "Bucket already exists"
gsutil versioning set on gs://${PROJECT_ID}-terraform-state || echo "Versioning already enabled"

# Step 2: Create secrets in Secret Manager
echo "2️⃣ Creating secrets..."

# OpenAI API Key
echo -n "YOUR_OPENAI_API_KEY_HERE" | \
  gcloud secrets create openai-api-key --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

# LemonSqueezy API Key
echo -n "YOUR_LEMONSQUEEZY_API_KEY_HERE" | \
  gcloud secrets create lemonsqueezy-api-key --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

# Resend API Key
echo -n "YOUR_RESEND_API_KEY_HERE" | \
  gcloud secrets create resend-api-key --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

# JWT Secret
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create jwt-secret --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

# Database Password
DB_PASSWORD=$(openssl rand -base64 16)
echo -n "$DB_PASSWORD" | \
  gcloud secrets create db-password --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

echo "✅ Secrets created successfully!"

# Step 3: Create Artifact Registry
echo "3️⃣ Creating Artifact Registry..."
gcloud artifacts repositories create formflow-images \
  --repository-format=docker \
  --location=$REGION \
  --description="FormFlow AI Docker images" \
  --project=$PROJECT_ID || echo "Repository already exists"

# Step 4: Build Docker images using Cloud Build
echo "4️⃣ Building Docker images with Cloud Build..."

# Backend
echo "Building backend image..."
cd backend
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/formflow-images/backend:latest \
  --project=$PROJECT_ID

# Frontend  
echo "Building frontend image..."
cd ../frontend
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/formflow-images/frontend:latest \
  --project=$PROJECT_ID

# Step 5: Deploy to Cloud Run
echo "5️⃣ Deploying to Cloud Run..."

# Get database password from secret
DB_PASSWORD=$(gcloud secrets versions access latest --secret=db-password --project=$PROJECT_ID)

# Backend deployment
gcloud run deploy formflow-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/formflow-images/backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,DATABASE_URL=postgresql://formflow:${DB_PASSWORD}@/formflow_db?host=/cloudsql/${PROJECT_ID}:${REGION}:formflow-db" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,RESEND_API_KEY=resend-api-key:latest,JWT_SECRET=jwt-secret:latest,LEMONSQUEEZY_API_KEY=lemonsqueezy-api-key:latest" \
  --project=$PROJECT_ID

# Frontend deployment
BACKEND_URL=$(gcloud run services describe formflow-backend --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

gcloud run deploy formflow-frontend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/formflow-images/frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}" \
  --project=$PROJECT_ID

# Step 6: Get URLs
echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
FRONTEND_URL=$(gcloud run services describe formflow-frontend --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔌 Backend URL: $BACKEND_URL"
echo ""
echo "🔗 Next Steps:"
echo "1. Visit the Frontend URL to test the application"
echo "2. Configure custom domain at GoDaddy (optional)"
echo "3. Set up Cloud SQL database (if needed)"
echo ""