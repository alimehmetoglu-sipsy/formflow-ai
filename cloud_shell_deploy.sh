#!/bin/bash

# FormFlow AI - Google Cloud Shell Deployment Script
# Bu scripti Google Cloud Shell'de çalıştır

set -e

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
DOMAIN="sipsy.ai"

echo "🚀 FormFlow AI Cloud Shell Deployment"
echo "======================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Domain: $DOMAIN"
echo ""

# Step 1: Clone repository
echo "1️⃣ Cloning FormFlow AI repository..."
git clone https://github.com/yourusername/formflow-ai.git || echo "Repository already exists"
cd formflow-ai

# Step 2: Set project
echo "2️⃣ Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Step 3: Create project if not exists
echo "3️⃣ Creating project if needed..."
gcloud projects create $PROJECT_ID --name="FormFlow AI" || echo "Project already exists"

# Step 4: Link billing account
echo "4️⃣ Please ensure billing is enabled for project $PROJECT_ID"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "Press enter when billing is enabled..."

# Step 5: Enable required APIs
echo "5️⃣ Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudsql.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  dns.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com

# Step 6: Create Terraform backend bucket
echo "6️⃣ Creating Terraform state bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state || echo "Bucket already exists"
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Step 7: Create secrets in Secret Manager
echo "7️⃣ Creating secrets..."

# OpenAI API Key
echo -n "YOUR_OPENAI_API_KEY_HERE" | \
  gcloud secrets create openai-api-key --data-file=- || echo "Secret already exists"

# LemonSqueezy API Key
echo -n "YOUR_LEMONSQUEEZY_API_KEY_HERE" | \
  gcloud secrets create lemonsqueezy-api-key --data-file=- || echo "Secret already exists"

# Resend API Key
echo -n "YOUR_RESEND_API_KEY_HERE" | \
  gcloud secrets create resend-api-key --data-file=- || echo "Secret already exists"

# JWT Secret
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create jwt-secret --data-file=- || echo "Secret already exists"

# Database Password
DB_PASSWORD=$(openssl rand -base64 16)
echo -n "$DB_PASSWORD" | \
  gcloud secrets create db-password --data-file=- || echo "Secret already exists"

echo "✅ Secrets created successfully!"

# Step 8: Initialize Terraform
echo "8️⃣ Initializing Terraform..."
cd terraform
terraform init \
  -backend-config="bucket=${PROJECT_ID}-terraform-state" \
  -backend-config="prefix=terraform/state"

# Step 9: Create infrastructure
echo "9️⃣ Creating infrastructure..."
terraform plan \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -var="domain=$DOMAIN" \
  -var="admin_email=admin@$DOMAIN"

echo ""
echo "📋 Review the plan above!"
echo "To apply infrastructure run:"
echo ""
echo "terraform apply -auto-approve \\"
echo "  -var=\"project_id=$PROJECT_ID\" \\"
echo "  -var=\"region=$REGION\" \\"
echo "  -var=\"domain=$DOMAIN\" \\"
echo "  -var=\"admin_email=admin@$DOMAIN\""
echo ""
echo "🎯 After infrastructure is created:"
echo "1. Build and deploy Docker images"
echo "2. Configure DNS at GoDaddy"
echo "3. Test the application"