# FormFlow AI - Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended)
One-click deployment with automatic SSL, custom domains, and managed PostgreSQL.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Option 2: DigitalOcean App Platform
```bash
# Clone and deploy
git clone https://github.com/alimehmetoglu-sipsy/formflow-ai.git
cd formflow-ai
# Push to your repository and connect to DigitalOcean
```

### Option 3: Docker Compose (Self-Hosted)
```bash
# One command deployment
docker-compose up -d --build
```

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Application   │    │    Database     │
│   (Nginx/Proxy)│◄──►│   (Backend +    │◄──►│  (PostgreSQL +  │
│                 │    │    Frontend)    │    │     Redis)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  File Storage   │              │
         └──────────────┤   (Optional)    ├──────────────┘
                        └─────────────────┘
```

---

## 🐳 Docker Deployment

### Prerequisites
- Docker 24.0+
- Docker Compose v2+
- 4GB RAM minimum
- 20GB storage minimum

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/alimehmetoglu-sipsy/formflow-ai.git
cd formflow-ai

# 2. Copy environment files
cp backend/.env.example .env
cp frontend/.env.local.example frontend/.env.local

# 3. Configure environment variables (see Environment Setup section)
nano .env

# 4. Start services
docker-compose up -d --build

# 5. Run database migrations
docker-compose exec backend python -m alembic upgrade head

# 6. Create admin user (optional)
docker-compose exec backend python scripts/create_admin.py

# Your application is now running at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: formflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/formflow
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=http://backend:8000
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_APP_URL=${NEXT_PUBLIC_APP_URL}
    ports:
      - "3000:3000"
    depends_on:
      - backend

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

---

## ☁️ Cloud Platform Deployments

### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Configure environment variables in Railway dashboard
```

**Railway Template Configuration:**
```json
{
  "name": "FormFlow AI",
  "services": {
    "backend": {
      "source": {
        "repo": "alimehmetoglu-sipsy/formflow-ai",
        "rootDirectory": "/backend"
      },
      "build": {
        "buildCommand": "pip install -r requirements.txt"
      },
      "deploy": {
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
      }
    },
    "frontend": {
      "source": {
        "repo": "alimehmetoglu-sipsy/formflow-ai", 
        "rootDirectory": "/frontend"
      }
    }
  },
  "plugins": {
    "postgresql": {},
    "redis": {}
  }
}
```

### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: formflow-ai
services:
- name: backend
  source_dir: /backend
  github:
    repo: alimehmetoglu-sipsy/formflow-ai
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    type: SECRET
  - key: OPENAI_API_KEY
    scope: RUN_TIME
    type: SECRET

- name: frontend
  source_dir: /frontend
  github:
    repo: alimehmetoglu-sipsy/formflow-ai
    branch: main
  build_command: npm run build
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs

databases:
- name: postgres
  engine: PG
  version: "15"
  size: basic-xxs
  
- name: redis
  engine: REDIS
  version: "7"
  size: basic-xxs
```

### AWS ECS/Fargate Deployment
```bash
# Install AWS CLI and configure
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name formflow-ai

# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Deploy using CDK or CloudFormation
cdk deploy FormFlowAIStack
```

### Google Cloud Run
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT_ID/formflow-backend ./backend
gcloud run deploy formflow-backend --image gcr.io/PROJECT_ID/formflow-backend --platform managed

# Build and deploy frontend  
gcloud builds submit --tag gcr.io/PROJECT_ID/formflow-frontend ./frontend
gcloud run deploy formflow-frontend --image gcr.io/PROJECT_ID/formflow-frontend --platform managed
```

---

## 🔧 Environment Configuration

### Backend Environment Variables (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/formflow
REDIS_URL=redis://host:6379/0

# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@formflow.ai

# Payment Integration (LemonSqueezy)
LEMONSQUEEZY_API_KEY=your-lemonsqueezy-api-key
LEMONSQUEEZY_WEBHOOK_SECRET=your-webhook-secret

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=formflow-uploads
AWS_REGION=us-east-1

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Security
ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]
SECURE_SSL_REDIRECT=true
```

### Frontend Environment Variables (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_URL=https://yourdomain.com

# Analytics
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your-analytics-id
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX

# Feature Flags
NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
NEXT_PUBLIC_ENABLE_OAUTH_LOGIN=false

# Third-party Services
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_your_stripe_key
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-sentry-dsn
```

---

## 🔒 SSL/TLS Configuration

### Nginx SSL Configuration
```nginx
# /nginx/nginx.conf
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }
}
```

### Let's Encrypt SSL Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Database Setup & Migrations

### PostgreSQL Setup
```bash
# Using Docker
docker run -d \
  --name formflow-postgres \
  -e POSTGRES_DB=formflow \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Or install locally (Ubuntu)
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb formflow
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

### Database Migrations
```bash
# Initialize Alembic (first time only)
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Database Backup & Restore
```bash
# Backup
docker exec -t formflow-postgres pg_dump -U postgres formflow > backup.sql

# Restore
docker exec -i formflow-postgres psql -U postgres formflow < backup.sql

# Scheduled backups (cron)
0 2 * * * docker exec formflow-postgres pg_dump -U postgres formflow | gzip > /backups/formflow_$(date +\%Y\%m\%d).sql.gz
```

---

## 🔍 Monitoring & Logging

### Health Check Endpoints
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Database connectivity
curl http://localhost:8000/api/v1/ready
```

### Logging Configuration
```python
# backend/logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/formflow.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Docker Logs
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Log rotation
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  your-image
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec backend python -c "from database import engine; print(engine.connect())"

# Fix: Update DATABASE_URL in .env file
```

#### 2. Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Fix: Update REDIS_URL in .env file
```

#### 3. OpenAI API Issues
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check rate limits
# View OpenAI dashboard usage

# Fix: Update OPENAI_API_KEY in .env file
```

#### 4. Frontend Build Issues
```bash
# Clear Next.js cache
rm -rf frontend/.next
rm -rf frontend/node_modules
npm install
npm run build

# Check for TypeScript errors
npm run type-check
```

#### 5. CORS Issues
```bash
# Add your domain to CORS_ORIGINS in .env
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Restart backend
docker-compose restart backend
```

### Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX CONCURRENTLY idx_dashboards_user_created ON dashboards(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_form_submissions_typeform ON form_submissions(typeform_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM dashboards WHERE user_id = 'uuid';
```

#### Backend Optimization
```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600
)
```

#### Frontend Optimization
```bash
# Bundle analysis
npm run build
npm install -g @next/bundle-analyzer
ANALYZE=true npm run build
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        cd backend
        python -m pytest
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Railway
      run: |
        curl -f -X POST https://backboard.railway.app/graphql/v2 \
          -H "Authorization: Bearer ${{ secrets.RAILWAY_TOKEN }}" \
          -H "Content-Type: application/json" \
          -d '{"query": "mutation { projectDeploy(input: {projectId: \"${{ secrets.PROJECT_ID }}\"}) { id } }"}'
```

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates valid
- [ ] Health checks responding
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Domain DNS configured
- [ ] CDN configured (if applicable)

---

## 📋 Production Maintenance

### Regular Tasks
```bash
# Weekly database maintenance
docker-compose exec db psql -U postgres -d formflow -c "VACUUM ANALYZE;"

# Clean old logs
find /var/log/formflow -name "*.log" -mtime +30 -delete

# Update dependencies
docker-compose pull
docker-compose up -d

# Security updates
docker system prune -f
```

### Scaling Considerations
- **Horizontal scaling**: Multiple backend instances behind load balancer
- **Database optimization**: Read replicas for heavy read workloads
- **Caching layer**: Redis cluster for high availability
- **CDN integration**: Static asset delivery optimization
- **Queue system**: Background job processing for dashboard generation

---

This deployment guide covers all major deployment scenarios and should enable successful production deployment of FormFlow AI.