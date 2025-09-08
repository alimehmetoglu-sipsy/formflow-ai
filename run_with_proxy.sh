#!/bin/bash

# FormFlow AI - Run with Cloud Shell Proxy
# This script runs the application using Cloud Shell proxy for testing

set -e

echo "===========================================" 
echo "🚀 FormFlow AI - Cloud Shell Proxy Setup"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Kill any existing proxy processes
echo ""
echo "1️⃣ Cleaning up existing proxy processes..."
pkill -f "gcloud run services proxy" 2>/dev/null || true
sleep 2

# Start frontend proxy
echo ""
echo "2️⃣ Starting Frontend proxy on port 8080..."
gcloud run services proxy formflow-frontend \
  --region=$REGION \
  --port=8080 &

FRONTEND_PID=$!
echo "Frontend proxy PID: $FRONTEND_PID"

# Wait for frontend to be ready
sleep 5

# Start backend proxy
echo ""
echo "3️⃣ Starting Backend proxy on port 8001..."
gcloud run services proxy formflow-backend \
  --region=$REGION \
  --port=8001 &

BACKEND_PID=$!
echo "Backend proxy PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 5

# Test endpoints
echo ""
echo "4️⃣ Testing endpoints..."

echo "Testing Frontend..."
curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://localhost:8080/ || true

echo "Testing Backend..."
curl -s -o /dev/null -w "Backend HTTP Status: %{http_code}\n" http://localhost:8001/health || true

echo ""
echo "===========================================" 
echo "✅ Proxy Setup Complete!"
echo "==========================================="
echo ""
echo "🌐 Access your application:"
echo ""
echo "📱 Frontend:"
echo "   - Local: http://localhost:8080"
echo "   - Cloud Shell Web Preview: Click 'Web Preview' > 'Preview on port 8080'"
echo ""
echo "🔧 Backend API:"
echo "   - Local: http://localhost:8001"
echo "   - API Docs: http://localhost:8001/docs"
echo "   - Cloud Shell Web Preview: Click 'Web Preview' > 'Change port' > Enter 8001"
echo ""
echo "⚠️  Keep this terminal open to maintain the proxy connection"
echo "📝 Press Ctrl+C to stop the proxies"
echo "==========================================="

# Keep script running
echo ""
echo "Proxies are running. Press Ctrl+C to stop..."

# Trap Ctrl+C to clean up
trap "echo 'Stopping proxies...'; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit" INT

# Wait indefinitely
while true; do
  sleep 1
done