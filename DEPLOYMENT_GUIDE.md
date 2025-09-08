# 🚀 FormFlow AI - Google Cloud Production Deployment Guide

## 📋 Overview
Complete production deployment setup for FormFlow AI on Google Cloud Platform with enterprise-grade infrastructure.

## 🏗️ Infrastructure Components

### ✅ Completed Components

#### 1. **Docker Configuration**
- ✅ Backend Dockerfile (multi-stage build, 4 workers)
- ✅ Frontend Dockerfile (Next.js standalone build)
- ✅ Docker Compose for local testing
- ✅ .dockerignore files for optimized builds

#### 2. **GCP Infrastructure (Terraform)**
- ✅ VPC Network & Subnets
- ✅ Cloud SQL PostgreSQL (europe-west1)
- ✅ Redis Memorystore
- ✅ Cloud Storage Buckets (static, uploads, backups)
- ✅ Artifact Registry for Docker images
- ✅ Secret Manager configuration
- ✅ VPC Connector for Cloud Run
- ✅ Network security (NAT, Firewall rules)

#### 3. **CI/CD Pipeline**
- ✅ GitHub Actions workflow
- ✅ Automated testing (backend + frontend)
- ✅ Docker build & push
- ✅ Cloud Run deployment
- ✅ Environment-based deployments (staging/production)

## 📁 Project Structure
```
formflow-ai/
├── backend/
│   ├── Dockerfile              # Backend container
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile              # Frontend container
│   └── .dockerignore
├── terraform/
│   ├── main.tf                 # Terraform main config
│   ├── variables.tf            # Variables (EU region)
│   ├── network.tf              # VPC configuration
│   ├── database.tf             # Cloud SQL & Redis
│   ├── storage.tf              # Cloud Storage buckets
│   ├── secrets.tf              # Secret Manager
│   └── outputs.tf              # Terraform outputs
├── scripts/
│   └── gcp_setup.sh           # GCP project setup script
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── docker-compose.prod.yml     # Local testing
└── DEPLOYMENT_GUIDE.md         # This file
```

## 🚀 Deployment Steps

### Step 1: GCP Project Setup
```bash
# Run the setup script
chmod +x scripts/gcp_setup.sh
./scripts/gcp_setup.sh

# Enter your billing account ID when prompted
```

### Step 2: Terraform Infrastructure
```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply infrastructure
terraform apply -auto-approve
```

### Step 3: Configure Secrets
Add your API keys to Secret Manager:
```bash
# OpenAI API Key
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-

# LemonSqueezy API Key
echo -n "your-lemonsqueezy-key" | gcloud secrets create lemonsqueezy-api-key --data-file=-

# Resend API Key
echo -n "your-resend-key" | gcloud secrets create resend-api-key --data-file=-
```

### Step 4: Build & Push Docker Images
```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker europe-west1-docker.pkg.dev

# Build and push backend
docker build -t europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest ./backend
docker push europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest

# Build and push frontend
docker build -t europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest ./frontend
docker push europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest
```

### Step 5: Deploy to Cloud Run
```bash
# Deploy backend
gcloud run deploy formflow-backend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/backend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --set-cloudsql-instances formflow-ai-prod:europe-west1:formflow-ai-prod-postgres \
  --vpc-connector formflow-connector \
  --service-account formflow-backend@formflow-ai-prod.iam.gserviceaccount.com

# Deploy frontend
gcloud run deploy formflow-frontend \
  --image europe-west1-docker.pkg.dev/formflow-ai-prod/formflow-images/frontend:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated
```

### Step 6: Configure Domain (sipsy.ai)
1. Verify domain ownership in Google Search Console
2. Set up Cloud DNS or update GoDaddy nameservers
3. Configure load balancer with SSL certificates
4. Map subdomains:
   - app.sipsy.ai → Frontend
   - api.sipsy.ai → Backend
   - webhooks.sipsy.ai → Backend webhooks

## 🔧 Environment Variables

### Backend (.env.production)
```env
PROJECT_ID=formflow-ai-prod
REGION=europe-west1
DATABASE_URL=<from-secret-manager>
REDIS_URL=<from-secret-manager>
OPENAI_API_KEY=<from-secret-manager>
LEMONSQUEEZY_API_KEY=<from-secret-manager>
RESEND_API_KEY=<from-secret-manager>
JWT_SECRET_KEY=<from-secret-manager>
FRONTEND_URL=https://app.sipsy.ai
BACKEND_URL=https://api.sipsy.ai
```

### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://api.sipsy.ai
```

## 📊 Monitoring & Observability

### Metrics to Monitor
- Request latency (P50, P95, P99)
- Error rate (<1% target)
- Database connections
- Redis memory usage
- Container CPU/Memory
- SSL certificate expiry

### Alert Policies
- High error rate (>1%)
- High latency (P95 >1s)
- Database connection pool exhaustion
- SSL certificate expiry (<30 days)

## 💰 Cost Optimization

### Estimated Monthly Costs (EUR)
- Cloud Run: €20-50 (auto-scaling)
- Cloud SQL: €30-50 (db-f1-micro)
- Redis: €20-30 (1GB BASIC)
- Storage: €5-10
- Network: €10-20
- **Total: €85-160/month**

### Cost Saving Tips
1. Use committed use discounts
2. Set up budget alerts
3. Use Cloud Scheduler to scale down during off-hours
4. Implement caching aggressively
5. Use Cloud CDN for static assets

## 🔒 Security Best Practices

1. ✅ All secrets in Secret Manager
2. ✅ VPC with private IPs
3. ✅ Cloud Armor DDoS protection
4. ✅ SSL/TLS everywhere
5. ✅ Service accounts with minimal permissions
6. ✅ Automated backups
7. ✅ Audit logging enabled

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check VPC connector
   - Verify Cloud SQL proxy
   - Check IAM permissions

2. **High Latency**
   - Check Redis connection
   - Review Cloud Run concurrency
   - Enable Cloud CDN

3. **Deployment Failed**
   - Check service account permissions
   - Verify Docker image exists
   - Review Cloud Run quotas

## 📝 GitHub Secrets Required

Add these secrets to your GitHub repository:
- `GCP_SA_KEY`: Service account JSON key
- `CODECOV_TOKEN`: For code coverage
- `SLACK_WEBHOOK_URL`: For notifications (optional)

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] Billing account linked
- [ ] APIs enabled
- [ ] Terraform infrastructure deployed
- [ ] Secrets configured
- [ ] Docker images built & pushed
- [ ] Cloud Run services deployed
- [ ] Domain configured
- [ ] SSL certificates active
- [ ] Monitoring configured
- [ ] Backups verified
- [ ] CI/CD pipeline tested

## 🎯 Next Steps

1. Configure custom domain and SSL
2. Set up monitoring dashboards
3. Implement auto-scaling policies
4. Configure backup schedules
5. Set up staging environment
6. Load testing and optimization

## 📞 Support

For issues or questions:
- Check Cloud Run logs: `gcloud run logs read`
- View metrics: Google Cloud Console → Monitoring
- Database issues: Cloud SQL → Logs
- Network issues: VPC → Firewall rules

---

**Last Updated**: September 2025
**Region**: Europe West 1 (Belgium)
**Domain**: sipsy.ai