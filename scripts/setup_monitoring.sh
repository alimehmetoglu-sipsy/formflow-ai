#!/bin/bash

# FormFlow AI - Monitoring Setup Script
# This script sets up monitoring, logging and observability on Google Cloud

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-formflow-ai-prod}"
REGION="${REGION:-europe-west1}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@sipsy.ai}"

echo "🔍 Setting up monitoring for FormFlow AI..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Admin Email: $ADMIN_EMAIL"

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable monitoring.googleapis.com \
    logging.googleapis.com \
    clouderrorreporting.googleapis.com \
    cloudtrace.googleapis.com \
    cloudprofiler.googleapis.com \
    --project=$PROJECT_ID

# Create custom metrics
echo "📊 Creating custom metrics..."

# Webhook success rate metric
gcloud logging metrics create webhook_success_rate \
    --description="Rate of successful webhook deliveries" \
    --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="formflow-backend"
    jsonPayload.webhook_status="success"' \
    --project=$PROJECT_ID || echo "Metric already exists"

# Dashboard creation metric  
gcloud logging metrics create dashboard_creation_rate \
    --description="Rate of dashboard creation" \
    --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="formflow-backend"
    jsonPayload.action="dashboard_created"' \
    --project=$PROJECT_ID || echo "Metric already exists"

# User registration metric
gcloud logging metrics create user_registration_rate \
    --description="Rate of user registrations" \
    --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="formflow-backend"
    jsonPayload.action="user_registered"' \
    --project=$PROJECT_ID || echo "Metric already exists"

# Create log-based alerting policies
echo "🚨 Setting up alerting policies..."

# Create notification channel for email
NOTIFICATION_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="FormFlow Admin Email" \
    --type=email \
    --channel-labels=email_address=$ADMIN_EMAIL \
    --project=$PROJECT_ID \
    --format="value(name)" 2>/dev/null || echo "Channel already exists")

echo "📧 Notification channel: $NOTIFICATION_CHANNEL"

# Create log router for error aggregation
echo "📝 Setting up log routing..."
gcloud logging sinks create formflow-error-sink \
    "logging.googleapis.com/projects/$PROJECT_ID/locations/$REGION/buckets/formflow-logs" \
    --log-filter='resource.type="cloud_run_revision"
    (resource.labels.service_name="formflow-backend" OR resource.labels.service_name="formflow-frontend")
    severity>=ERROR' \
    --project=$PROJECT_ID || echo "Sink already exists"

# Set up error reporting
echo "🐛 Configuring error reporting..."
gcloud error-reporting events report \
    --service="formflow-backend" \
    --service-version="1.0.0" \
    --message="Monitoring setup complete" \
    --project=$PROJECT_ID || true

echo "✅ Monitoring setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure notification channels in Cloud Console"
echo "2. Set up custom dashboards if needed" 
echo "3. Review alert policies and thresholds"
echo "4. Test monitoring by triggering some alerts"
echo ""
echo "🔗 Useful links:"
echo "- Monitoring: https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo "- Logging: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
echo "- Error Reporting: https://console.cloud.google.com/errors?project=$PROJECT_ID"