#!/bin/bash

# FormFlow AI - Local Deployment to Google Cloud
# Bu script service account key olmadan deployment yapar

set -e

# Export PATH for gcloud
export PATH=$PATH:/home/ali/formflow-ai/google-cloud-sdk/bin

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
DOMAIN="sipsy.ai"

echo "🚀 FormFlow AI Local Deployment Script"
echo "======================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Domain: $DOMAIN"
echo ""

# Step 1: Login and set project
echo "1️⃣ Google Cloud Authentication..."
gcloud auth login --no-launch-browser
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo "2️⃣ Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudsql.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  dns.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

# Step 3: Create Terraform backend bucket
echo "3️⃣ Creating Terraform state bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state || echo "Bucket already exists"
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Step 4: Initialize and apply Terraform
echo "4️⃣ Deploying infrastructure with Terraform..."
cd terraform
terraform init \
  -backend-config="bucket=${PROJECT_ID}-terraform-state" \
  -backend-config="prefix=terraform/state"

terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="domain=$DOMAIN"

echo ""
echo "⚠️  Ready to deploy infrastructure!"
echo "Bu noktadan sonra resources oluşturulmaya başlanacak."
echo "Devam etmek için 'terraform apply' çalıştır."
echo ""
echo "Next commands:"
echo "cd terraform && terraform apply -var=\"project_id=$PROJECT_ID\" -var=\"region=$REGION\" -var=\"domain=$DOMAIN\""