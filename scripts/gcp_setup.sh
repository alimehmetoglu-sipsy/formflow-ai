#!/bin/bash

# ============================================
# FormFlow AI - Google Cloud Platform Setup Script
# ============================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration Variables
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
ZONE="europe-west1-b"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FormFlow AI - GCP Project Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}gcloud CLI is not installed. Please install it first:${NC}"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get billing account ID
echo -e "\n${YELLOW}Enter your GCP Billing Account ID:${NC}"
read -r BILLING_ACCOUNT_ID

if [ -z "$BILLING_ACCOUNT_ID" ]; then
    echo -e "${RED}Billing Account ID is required${NC}"
    exit 1
fi

# Create project
echo -e "\n${YELLOW}Creating GCP project: $PROJECT_ID${NC}"
if gcloud projects describe $PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Project $PROJECT_ID already exists${NC}"
else
    gcloud projects create $PROJECT_ID --name="FormFlow AI Production"
    echo -e "${GREEN}✅ Project created${NC}"
fi

# Set current project
gcloud config set project $PROJECT_ID

# Link billing account
echo -e "\n${YELLOW}Linking billing account...${NC}"
gcloud beta billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
echo -e "${GREEN}✅ Billing account linked${NC}"

# Enable required APIs
echo -e "\n${YELLOW}Enabling Google Cloud APIs...${NC}"

APIS=(
    "compute.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "redis.googleapis.com"
    "secretmanager.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "servicenetworking.googleapis.com"
    "vpcaccess.googleapis.com"
    "dns.googleapis.com"
    "certificatemanager.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "cloudtrace.googleapis.com"
    "clouderrorreporting.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -e "Enabling $api..."
    gcloud services enable $api --project=$PROJECT_ID
done

echo -e "${GREEN}✅ All APIs enabled${NC}"

# Create service account for deployment
echo -e "\n${YELLOW}Creating service accounts...${NC}"

# Backend service account
gcloud iam service-accounts create formflow-backend \
    --display-name="FormFlow Backend Service Account" \
    --project=$PROJECT_ID 2>/dev/null || echo "Backend service account already exists"

# Deployment service account
gcloud iam service-accounts create formflow-deployer \
    --display-name="FormFlow Deployment Service Account" \
    --project=$PROJECT_ID 2>/dev/null || echo "Deployer service account already exists"

# Grant necessary roles to backend service account
echo -e "\n${YELLOW}Granting IAM roles...${NC}"

BACKEND_SA="formflow-backend@$PROJECT_ID.iam.gserviceaccount.com"
DEPLOYER_SA="formflow-deployer@$PROJECT_ID.iam.gserviceaccount.com"

# Backend service account roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BACKEND_SA" \
    --role="roles/logging.logWriter"

# Deployer service account roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYER_SA" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYER_SA" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYER_SA" \
    --role="roles/run.admin"

echo -e "${GREEN}✅ IAM roles granted${NC}"

# Create Artifact Registry repository
echo -e "\n${YELLOW}Creating Artifact Registry repository...${NC}"

gcloud artifacts repositories create formflow-images \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker images for FormFlow AI" \
    --project=$PROJECT_ID 2>/dev/null || echo "Repository already exists"

echo -e "${GREEN}✅ Artifact Registry configured${NC}"

# Create storage buckets for Terraform state
echo -e "\n${YELLOW}Creating Terraform state bucket...${NC}"

gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://formflow-terraform-state 2>/dev/null || echo "Bucket already exists"
gsutil versioning set on gs://formflow-terraform-state

echo -e "${GREEN}✅ Terraform state bucket created${NC}"

# Generate service account key for CI/CD
echo -e "\n${YELLOW}Creating service account key for CI/CD...${NC}"

KEY_FILE="$HOME/formflow-deployer-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$DEPLOYER_SA \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Service account key created at: $KEY_FILE${NC}"

# Set up default region and zone
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GCP Project Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Project Details:${NC}"
echo -e "  Project ID: ${GREEN}$PROJECT_ID${NC}"
echo -e "  Region: ${GREEN}$REGION${NC}"
echo -e "  Zone: ${GREEN}$ZONE${NC}"
echo -e "\n${YELLOW}Service Accounts:${NC}"
echo -e "  Backend: ${GREEN}$BACKEND_SA${NC}"
echo -e "  Deployer: ${GREEN}$DEPLOYER_SA${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Store the service account key securely"
echo -e "  2. Add the key to GitHub Secrets as GCP_SA_KEY"
echo -e "  3. Run terraform init & apply"
echo -e "  4. Deploy applications to Cloud Run"
echo -e "\n${YELLOW}Important Files:${NC}"
echo -e "  Service Account Key: ${GREEN}$KEY_FILE${NC}"
echo -e "  Terraform State Bucket: ${GREEN}gs://formflow-terraform-state${NC}"