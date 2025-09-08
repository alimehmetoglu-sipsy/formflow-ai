#!/bin/bash

# FormFlow AI - Create Secrets Script
# Run this ONCE before deployment to create secrets in Google Secret Manager

set -e

echo "==========================================="
echo "🔐 FormFlow AI - Creating Secrets"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# IMPORTANT: Replace these with your actual API keys
OPENAI_KEY="YOUR_OPENAI_API_KEY_HERE"
RESEND_KEY="YOUR_RESEND_API_KEY_HERE"

echo ""
echo "Creating secrets in Google Secret Manager..."

# Create OpenAI API Key secret
echo "1️⃣ Creating openai_api_key..."
echo -n "$OPENAI_KEY" | gcloud secrets create openai_api_key --data-file=- 2>/dev/null || echo "Secret already exists"

# Create Resend API Key secret
echo "2️⃣ Creating resend_api_key..."
echo -n "$RESEND_KEY" | gcloud secrets create resend_api_key --data-file=- 2>/dev/null || echo "Secret already exists"

echo ""
echo "✅ Secrets created/verified successfully!"
echo ""
echo "⚠️  IMPORTANT: Make sure to update the API keys in this script with your actual keys before running!"
echo "==========================================="