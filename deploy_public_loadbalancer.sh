#!/bin/bash

# FormFlow AI - Public Access via Load Balancer
# Alternative deployment without Firebase

set -e

echo "===========================================" 
echo "🚀 FormFlow AI - Public Access Setup (Load Balancer)"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
LOAD_BALANCER_IP="34.111.91.63"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Step 1: Update Cloud Run services to allow unauthenticated access from Load Balancer
echo ""
echo "1️⃣ Configuring Cloud Run services..."

# Set ingress to allow Load Balancer traffic
gcloud run services update formflow-frontend \
  --region=$REGION \
  --ingress=all \
  --quiet

gcloud run services update formflow-backend \
  --region=$REGION \
  --ingress=all \
  --quiet

echo "✅ Cloud Run services configured"

# Step 2: Create a special service account for Load Balancer
echo ""
echo "2️⃣ Creating service account for Load Balancer..."

# Create service account if not exists
gcloud iam service-accounts create lb-invoker \
  --display-name="Load Balancer Invoker" 2>/dev/null || echo "Service account already exists"

SA_EMAIL="lb-invoker@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Cloud Run Invoker role
gcloud run services add-iam-policy-binding formflow-frontend \
  --region=$REGION \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --quiet

gcloud run services add-iam-policy-binding formflow-backend \
  --region=$REGION \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --quiet

echo "✅ Service account configured"

# Step 3: Update backend services with proper settings
echo ""
echo "3️⃣ Updating Load Balancer backend services..."

# Note: Serverless NEGs don't need health checks - Cloud Run handles this automatically

# Update backend service for frontend (without health check)
gcloud compute backend-services update formflow-frontend-service \
  --global \
  --timeout=30 \
  --connection-draining-timeout=30 \
  --quiet

# Create backend service for API if not exists
gcloud compute backend-services create formflow-backend-service \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED 2>/dev/null || echo "Backend service already exists"

gcloud compute backend-services add-backend formflow-backend-service \
  --global \
  --network-endpoint-group=formflow-backend-neg \
  --network-endpoint-group-region=$REGION 2>/dev/null || echo "Backend already added"

# Update backend service for API (without health check)
gcloud compute backend-services update formflow-backend-service \
  --global \
  --timeout=30 \
  --connection-draining-timeout=30 \
  --quiet

echo "✅ Backend services updated"

# Step 4: Update URL mapping for proper routing
echo ""
echo "4️⃣ Configuring URL routing..."

# Export current URL map
gcloud compute url-maps export formflow-url-map \
  --destination=url-map.yaml \
  --global \
  --quiet

# Create updated URL map with path rules
cat > url-map-updated.yaml << 'EOF'
defaultService: https://www.googleapis.com/compute/v1/projects/formflow-ai-prod/global/backendServices/formflow-frontend-service
hostRules:
- hosts:
  - '*'
  pathMatcher: path-matcher
name: formflow-url-map
pathMatchers:
- defaultService: https://www.googleapis.com/compute/v1/projects/formflow-ai-prod/global/backendServices/formflow-frontend-service
  name: path-matcher
  pathRules:
  - paths:
    - /api/*
    - /api/v1/*
    - /docs
    - /docs/*
    - /openapi.json
    - /health
    service: https://www.googleapis.com/compute/v1/projects/formflow-ai-prod/global/backendServices/formflow-backend-service
EOF

# Import updated URL map
gcloud compute url-maps import formflow-url-map \
  --source=url-map-updated.yaml \
  --global \
  --quiet

echo "✅ URL routing configured"

# Step 5: Create a new forwarding rule with a static IP
echo ""
echo "5️⃣ Setting up static IP and forwarding rules..."

# Reserve static IP if not exists
gcloud compute addresses create formflow-static-ip \
  --global 2>/dev/null || echo "Static IP already exists"

STATIC_IP=$(gcloud compute addresses describe formflow-static-ip --global --format="value(address)")

# Update forwarding rule to use static IP
gcloud compute forwarding-rules delete formflow-http-rule --global --quiet 2>/dev/null || true
gcloud compute forwarding-rules create formflow-http-rule \
  --address=$STATIC_IP \
  --global \
  --target-http-proxy=formflow-http-proxy \
  --ports=80

echo "✅ Static IP configured: $STATIC_IP"

# Step 6: Test the endpoints
echo ""
echo "6️⃣ Testing endpoints..."

# Wait for Load Balancer to be ready
echo "Waiting for Load Balancer to be ready (this may take 2-3 minutes)..."
sleep 30

# Test frontend
echo "Testing frontend..."
curl -I http://$STATIC_IP/ 2>/dev/null | head -n 1

# Test backend
echo "Testing backend API..."
curl -I http://$STATIC_IP/api/v1/health 2>/dev/null | head -n 1

echo ""
echo "===========================================" 
echo "✅ Deployment Complete!"
echo "==========================================="
echo ""
echo "🌐 Your app is publicly accessible at:"
echo "   http://$STATIC_IP"
echo ""
echo "📱 Frontend: http://$STATIC_IP"
echo "🔧 Backend API: http://$STATIC_IP/api/v1"
echo "📚 API Docs: http://$STATIC_IP/api/v1/docs"
echo ""
echo "⚠️  Note: It may take 5-10 minutes for the Load Balancer to fully activate"
echo ""
echo "🔒 To add HTTPS:"
echo "   1. Get a domain name"
echo "   2. Point it to IP: $STATIC_IP"
echo "   3. Run: gcloud compute ssl-certificates create formflow-cert --domains=yourdomain.com"
echo "==========================================="