# FormFlow AI - API Keys & External Services

## 🔑 Required API Keys & Credentials

This document outlines all external API keys, credentials, and service configurations needed for FormFlow AI deployment and operation.

---

## 🤖 AI & Machine Learning Services

### OpenAI API (Critical)
**Service:** OpenAI GPT-4  
**Purpose:** AI-powered dashboard generation and insights  
**Priority:** 🔴 Critical - Core functionality depends on this  

**Required Credentials:**
- **API Key:** `OPENAI_API_KEY`
- **Organization ID:** `OPENAI_ORG_ID` (optional)

**Setup Instructions:**
1. Create account at https://platform.openai.com/
2. Navigate to API Keys section
3. Create new secret key with appropriate permissions
4. Add to environment variables

**Configuration:**
```bash
# Environment variables
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-4-turbo for better performance
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
```

**Usage Limits & Costs:**
- **Free Tier:** $5 credit (limited time)
- **Pay-as-you-go:** ~$0.03 per dashboard generation
- **Rate Limits:** 3,500 requests/hour (Tier 1)
- **Monthly Cost:** $200-500 for typical usage

**Monitoring:**
- Track token usage in OpenAI dashboard
- Set up usage alerts at 80% of monthly budget
- Monitor API response times and error rates

---

## 💳 Payment Processing

### LemonSqueezy (Critical for Revenue)
**Service:** Subscription billing and payments  
**Purpose:** Handle Pro/Business plan subscriptions  
**Priority:** 🔴 Critical - Required for monetization

**Required Credentials:**
- **API Key:** `LEMONSQUEEZY_API_KEY`
- **Webhook Secret:** `LEMONSQUEEZY_WEBHOOK_SECRET`
- **Store ID:** `LEMONSQUEEZY_STORE_ID`

**Setup Instructions:**
1. Create LemonSqueezy account at https://lemonsqueezy.com/
2. Set up store and products
3. Generate API key from Settings > API
4. Configure webhook endpoints
5. Set webhook secret for security

**Configuration:**
```bash
# Environment variables
LEMONSQUEEZY_API_KEY=your-lemonsqueezy-api-key
LEMONSQUEEZY_WEBHOOK_SECRET=your-webhook-secret
LEMONSQUEEZY_STORE_ID=12345
LEMONSQUEEZY_PRODUCT_PRO=67890
LEMONSQUEEZY_PRODUCT_BUSINESS=54321
```

**Products Setup:**
- **Pro Plan:** $17/month recurring
- **Business Plan:** $47/month recurring  
- **Annual Discount:** 15% off yearly billing

**Testing:**
- Use test mode for development
- Test webhook delivery with ngrok
- Verify subscription lifecycle events

---

## 📧 Email Services

### SMTP Email Service (Critical)
**Service:** Email delivery (Gmail, SendGrid, or Mailgun)  
**Purpose:** User notifications, password resets, dashboard alerts  
**Priority:** 🔴 Critical - User communication depends on this

**Option 1: Gmail SMTP (Simple Setup)**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password  # Not your regular password!
SMTP_USE_TLS=true
FROM_EMAIL=noreply@yourdomain.com
```

**Option 2: SendGrid (Recommended for Production)**
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
SENDGRID_API_KEY=your-sendgrid-api-key
```

**Option 3: Mailgun (Alternative)**
```bash
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=yourdomain.com
FROM_EMAIL=noreply@yourdomain.com
```

**Email Templates Required:**
- Welcome email for new users
- Dashboard ready notifications  
- Password reset instructions
- Subscription confirmations
- Weekly dashboard summaries

---

## 🗄️ Database Services

### PostgreSQL Database (Critical)
**Service:** Primary database  
**Purpose:** User data, dashboards, form submissions  
**Priority:** 🔴 Critical - All data storage

**Configuration Options:**

**Option 1: Railway PostgreSQL (Recommended)**
```bash
# Automatically provided by Railway
DATABASE_URL=postgresql://postgres:password@host:5432/railway
```

**Option 2: Self-hosted/DigitalOcean**
```bash
DATABASE_URL=postgresql://username:password@host:5432/formflow
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=formflow
DB_USER=formflow_user
DB_PASSWORD=secure-database-password
```

**Database Requirements:**
- PostgreSQL 12+ (15+ recommended)
- At least 2GB storage (20GB+ for production)
- Regular automated backups
- Connection pooling support

---

### Redis Cache (Critical)
**Service:** Caching and session storage  
**Purpose:** Performance optimization, user sessions  
**Priority:** 🔴 Critical - Performance depends on this

**Configuration:**
```bash
REDIS_URL=redis://default:password@host:6379/0
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

**Usage:**
- User session storage
- API response caching
- Webhook processing queues
- Rate limiting counters

---

## 📊 Analytics & Monitoring

### Sentry Error Tracking (Highly Recommended)
**Service:** Error tracking and performance monitoring  
**Purpose:** Bug tracking, performance insights  
**Priority:** 🟡 High - Essential for production stability

**Setup:**
1. Create account at https://sentry.io/
2. Create new project for FormFlow AI
3. Get DSN from project settings

**Configuration:**
```bash
SENTRY_DSN=https://your-sentry-dsn@o123456.ingest.sentry.io/1234567
SENTRY_ENVIRONMENT=production  # or development, staging
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Features Used:**
- Automatic error reporting
- Performance monitoring
- Release tracking
- Custom alerts

---

### Vercel Analytics (Optional)
**Service:** Frontend analytics  
**Purpose:** User behavior tracking, performance insights  
**Priority:** 🟢 Nice to have

**Configuration:**
```bash
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your-analytics-id
```

---

## 🔐 Authentication & Security

### JWT Secret Keys (Critical)
**Purpose:** Secure user authentication  
**Priority:** 🔴 Critical - Security depends on this

**Configuration:**
```bash
# Generate a secure random string (32+ characters)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

**Generation Command:**
```bash
# Generate secure secret key
openssl rand -hex 32
```

---

## 🌐 Domain & SSL

### Domain Configuration
**Requirements:**
- Custom domain (e.g., app.yourdomain.com)
- SSL certificate (automated with Railway/Vercel)
- DNS configuration

**DNS Records Required:**
```
# Main application
A    app.yourdomain.com    -> [your-server-ip]
CNAME www.yourdomain.com   -> app.yourdomain.com

# API subdomain (optional)
CNAME api.yourdomain.com   -> app.yourdomain.com
```

---

## 🔧 Development & Testing

### ngrok (Development Only)
**Service:** Local tunnel for webhook testing  
**Purpose:** Test webhooks from external services  
**Priority:** 🟢 Development only

**Setup:**
1. Install ngrok: https://ngrok.com/download
2. Create account and get auth token
3. Configure tunnel for local development

**Usage:**
```bash
# Tunnel local backend to test webhooks
ngrok http 8000

# Use ngrok URL in form platform webhooks:
# https://abc123.ngrok.io/api/v1/webhooks/typeform
```

---

## 📋 Environment-Specific Configurations

### Development Environment
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://localhost:5432/formflow_dev
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-dev-openai-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Staging Environment  
```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=your-staging-db-url
REDIS_URL=your-staging-redis-url
OPENAI_API_KEY=your-staging-openai-key
SENTRY_DSN=your-staging-sentry-dsn
```

### Production Environment
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=your-production-db-url
REDIS_URL=your-production-redis-url
OPENAI_API_KEY=your-production-openai-key
LEMONSQUEEZY_API_KEY=your-production-lemonsqueezy-key
SENTRY_DSN=your-production-sentry-dsn
ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]
SECURE_SSL_REDIRECT=true
```

---

## 🚨 Security Best Practices

### API Key Security
- **Never commit API keys to version control**
- **Use environment variables for all secrets**
- **Rotate keys regularly (quarterly)**
- **Use different keys for different environments**
- **Monitor API key usage for unusual activity**

### Access Management
- **Limit API key permissions to minimum required**
- **Use separate service accounts where possible**
- **Enable 2FA on all service accounts**
- **Regular access audits and key rotation**

### Secret Management
```bash
# Use a secret management service in production
# Examples: AWS Secrets Manager, Azure Key Vault, Railway Variables

# Never do this:
OPENAI_API_KEY=sk-actual-key-in-code  # ❌ WRONG

# Do this instead:
OPENAI_API_KEY=${OPENAI_API_KEY}  # ✅ Environment variable
```

---

## 💰 Cost Estimates

### Monthly Service Costs (Production):

**Critical Services:**
- **OpenAI API:** $200-500/month (based on usage)
- **Database (Railway):** $10-30/month
- **Redis (Railway):** $5-15/month  
- **Email Service:** $10-25/month
- **Domain & SSL:** $10-15/month

**Optional Services:**
- **Sentry:** $0-26/month (free tier available)
- **Analytics:** $0-20/month
- **CDN:** $5-15/month

**Total Estimated Monthly Cost:** $240-646/month

### Cost Optimization Tips:
- Start with free tiers where available
- Monitor usage and set alerts
- Optimize OpenAI API calls (biggest cost)
- Use caching to reduce database load
- Consider reserved instances for stable workloads

---

## ✅ Setup Checklist

### Pre-Deployment Checklist:
- [ ] OpenAI API key obtained and tested
- [ ] LemonSqueezy account set up with products
- [ ] Email service configured and tested  
- [ ] Database provisioned and accessible
- [ ] Redis cache service running
- [ ] JWT secret key generated (secure, 32+ chars)
- [ ] Domain purchased and DNS configured
- [ ] SSL certificate automated or installed
- [ ] Sentry project created for error tracking
- [ ] All environment variables documented
- [ ] API keys stored securely (not in code)
- [ ] Test deployments successful
- [ ] Monitoring and alerts configured

### Post-Deployment Verification:
- [ ] Health check endpoints responding
- [ ] Email notifications working
- [ ] Payment flows functional
- [ ] Dashboard generation working
- [ ] Webhook processing successful
- [ ] Error tracking receiving data
- [ ] Performance metrics within acceptable range

---

## 🆘 Troubleshooting Common Issues

### OpenAI API Issues:
**Problem:** API key invalid or rate limited  
**Solution:** Check key validity, upgrade tier, implement retry logic

### Database Connection Issues:
**Problem:** Connection timeouts or too many connections  
**Solution:** Check connection string, implement connection pooling

### Email Delivery Issues:
**Problem:** Emails not delivered or marked as spam  
**Solution:** Configure SPF/DKIM records, use dedicated email service

### Payment Processing Issues:
**Problem:** Webhooks not received or processed  
**Solution:** Verify webhook URLs, check signature verification

---

## 📞 Support Contacts

### Critical Service Support:
- **OpenAI:** https://help.openai.com/
- **LemonSqueezy:** support@lemonsqueezy.com
- **Railway:** https://help.railway.app/
- **Sentry:** support@sentry.io

### Emergency Contacts:
- **Database Issues:** Escalate to infrastructure team
- **Payment Issues:** Check LemonSqueezy status page
- **Security Incidents:** Rotate all API keys immediately

---

**Last Updated:** January 28, 2025  
**Next Review:** March 1, 2025  
**Document Owner:** DevOps Team

---

⚠️ **Security Notice:** This document contains sensitive information about API requirements. Ensure actual API keys are never committed to version control and are stored securely using environment variables or dedicated secret management services.