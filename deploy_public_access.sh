#!/bin/bash

# FormFlow AI - Public Access Deployment Script
# This script sets up public access using Firebase Hosting

set -e

echo "===========================================" 
echo "🚀 FormFlow AI - Public Access Setup"
echo "==========================================="

# Configuration
PROJECT_ID="formflow-ai-prod"
REGION="europe-west1"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Update Cloud Run services with ingress settings
echo ""
echo "1️⃣ Configuring Cloud Run services for Load Balancer access..."

gcloud run services update formflow-frontend \
  --region=$REGION \
  --ingress=internal-and-cloud-load-balancing \
  --quiet

gcloud run services update formflow-backend \
  --region=$REGION \
  --ingress=internal-and-cloud-load-balancing \
  --quiet

echo "✅ Cloud Run ingress configured"

# Install Firebase CLI if not exists
echo ""
echo "2️⃣ Installing Firebase CLI..."
if ! command -v firebase &> /dev/null; then
    npm install -g firebase-tools
    echo "✅ Firebase CLI installed"
else
    echo "✅ Firebase CLI already installed"
fi

# Create Firebase configuration
echo ""
echo "3️⃣ Creating Firebase configuration..."

cat > firebase.json << 'EOF'
{
  "hosting": {
    "public": "frontend/.next/static",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "formflow-backend",
          "region": "europe-west1"
        }
      },
      {
        "source": "**",
        "run": {
          "serviceId": "formflow-frontend", 
          "region": "europe-west1"
        }
      }
    ],
    "headers": [
      {
        "source": "**/*.@(jpg|jpeg|gif|png|svg|ico)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=86400"
          }
        ]
      }
    ]
  }
}
EOF

echo "✅ Firebase configuration created"

# Create .firebaserc
cat > .firebaserc << EOF
{
  "projects": {
    "default": "$PROJECT_ID"
  }
}
EOF

# Enable Firebase in the project
echo ""
echo "4️⃣ Enabling Firebase in project..."
firebase projects:addfirebase $PROJECT_ID 2>/dev/null || echo "Firebase already enabled"

# Initialize Firebase (non-interactive)
echo ""
echo "5️⃣ Initializing Firebase..."
firebase use $PROJECT_ID 2>/dev/null || firebase use --add $PROJECT_ID

# Deploy to Firebase Hosting
echo ""
echo "6️⃣ Deploying to Firebase Hosting..."
firebase deploy --only hosting --project $PROJECT_ID --non-interactive

echo ""
echo "===========================================" 
echo "✅ Deployment Complete!"
echo "==========================================="
echo ""
echo "🌐 Your app is now publicly accessible at:"
echo "   https://$PROJECT_ID.web.app"
echo "   https://$PROJECT_ID.firebaseapp.com"
echo ""
echo "📊 Load Balancer URL (backup):"
echo "   http://34.111.91.63"
echo ""
echo "🔧 To add a custom domain:"
echo "   1. Go to Firebase Console > Hosting"
echo "   2. Click 'Add custom domain'"
echo "   3. Follow the DNS setup instructions"
echo "==========================================="