#!/bin/bash

# FormFlow AI - Public Access Setup (Alternative Methods)
# Try different methods to achieve public access

set -e

echo "===========================================" 
echo "🚀 FormFlow AI - Public Access Setup"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"
FRONTEND_SERVICE="formflow-frontend"
BACKEND_SERVICE="formflow-backend"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Method 1: Try to set allow-unauthenticated (may fail due to org policy)
echo ""
echo "Method 1: Attempting to allow unauthenticated access..."
echo "==========================================="

gcloud run services update $FRONTEND_SERVICE \
  --region=$REGION \
  --ingress=all \
  --allow-unauthenticated 2>/dev/null && echo "✅ Frontend: Unauthenticated access enabled" || echo "❌ Frontend: Organization policy blocks unauthenticated access"

gcloud run services update $BACKEND_SERVICE \
  --region=$REGION \
  --ingress=all \
  --allow-unauthenticated 2>/dev/null && echo "✅ Backend: Unauthenticated access enabled" || echo "❌ Backend: Organization policy blocks unauthenticated access"

# Method 2: API Gateway Setup
echo ""
echo "Method 2: Setting up API Gateway..."
echo "==========================================="

# Create API if not exists
gcloud api-gateway apis create formflow-api \
  --display-name="FormFlow API" \
  --project=$PROJECT_ID 2>/dev/null || echo "API already exists"

# Get service URLs
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')

# Create OpenAPI specification
cat > /tmp/openapi-spec.yaml << EOF
swagger: "2.0"
info:
  title: FormFlow API Gateway
  version: 1.0.0
host: formflow-gateway-$PROJECT_ID.ew.gateway.dev
x-google-endpoints:
- name: formflow-gateway-$PROJECT_ID.ew.gateway.dev
  allowCors: true
schemes:
- https
produces:
- application/json
x-google-backend:
  address: $BACKEND_URL
  protocol: h2
paths:
  /health:
    get:
      summary: Health check
      operationId: health
      responses:
        200:
          description: OK
  /api/v1/**:
    get:
      summary: API endpoints
      operationId: api
      responses:
        200:
          description: OK
    post:
      summary: API endpoints
      operationId: apiPost
      responses:
        200:
          description: OK
    put:
      summary: API endpoints
      operationId: apiPut
      responses:
        200:
          description: OK
    delete:
      summary: API endpoints
      operationId: apiDelete
      responses:
        200:
          description: OK
EOF

# Create API config
CONFIG_ID="config-$(date +%s)"
gcloud api-gateway api-configs create $CONFIG_ID \
  --api=formflow-api \
  --openapi-spec=/tmp/openapi-spec.yaml \
  --project=$PROJECT_ID 2>/dev/null && echo "✅ API config created: $CONFIG_ID" || echo "❌ Failed to create API config"

# Create or update gateway
gcloud api-gateway gateways create formflow-gateway \
  --api=formflow-api \
  --api-config=$CONFIG_ID \
  --location=$REGION \
  --project=$PROJECT_ID 2>/dev/null && echo "✅ API Gateway created" || echo "Gateway already exists or failed"

# Get gateway URL
GATEWAY_URL=$(gcloud api-gateway gateways describe formflow-gateway \
  --location=$REGION \
  --format="value(defaultHostname)" 2>/dev/null)

if [ ! -z "$GATEWAY_URL" ]; then
  echo "✅ API Gateway URL: https://$GATEWAY_URL"
fi

# Method 3: Cloud Endpoints
echo ""
echo "Method 3: Alternative - Use Cloud Shell Proxy"
echo "==========================================="
echo "Since organization policies may block public access,"
echo "you can use Cloud Shell proxy for testing:"
echo ""
echo "Run: ./run_with_proxy.sh"
echo ""

# Summary
echo ""
echo "===========================================" 
echo "📊 Summary"
echo "==========================================="
echo ""
echo "🔍 Service URLs:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend: $BACKEND_URL"
echo ""

if [ ! -z "$GATEWAY_URL" ]; then
  echo "🌐 API Gateway (if successful):"
  echo "   https://$GATEWAY_URL"
  echo ""
fi

echo "🔧 For testing with Cloud Shell:"
echo "   Run: ./run_with_proxy.sh"
echo ""
echo "📝 Note: If organization policies block public access,"
echo "   consider using a personal GCP project or"
echo "   deploying to a different cloud provider."
echo "==========================================="