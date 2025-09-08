# 🚀 FormFlow AI

Transform any form into an AI-powered dashboard in 60 seconds! FormFlow AI automatically processes form submissions through webhooks, analyzes them with GPT-4, and generates beautiful, intelligent dashboards.

## 🌟 Features

- **🔗 Webhook Integration**: Seamlessly connect with Typeform, Google Forms, and 20+ form builders
- **🤖 AI-Powered Analysis**: GPT-4 analyzes responses and generates intelligent insights
- **📊 Dynamic Dashboards**: Beautiful, responsive dashboards generated automatically
- **🎨 Multiple Templates**: Diet plans, lead scoring, event registration, and more
- **⚡ Real-time Processing**: Dashboards ready in under 60 seconds
- **🔐 Secure Authentication**: Google OAuth and JWT-based authentication
- **💳 Payment Integration**: Subscription management with Lemonsqueezy
- **📈 Analytics**: Track views, engagement, and conversion metrics

## 🛠️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, Redis, SQLAlchemy
- **AI**: OpenAI GPT-4, Jinja2 templates
- **Frontend**: Next.js, Tailwind CSS, Framer Motion (coming soon)
- **Infrastructure**: Docker, Railway/Render
- **Authentication**: Google OAuth, JWT
- **Payments**: Lemonsqueezy

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key (optional, for AI features)
- Typeform account (optional, for webhook testing)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/formflow-ai.git
cd formflow-ai
```

### 2. Set up environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your configuration:

```env
# Required
DATABASE_URL=postgresql://formflow:formflow123@localhost:5432/formflow_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here

# Optional (for full features)
OPENAI_API_KEY=sk-proj-your-key-here
TYPEFORM_WEBHOOK_SECRET=your-webhook-secret
```

### 3. Start the application with Docker

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- FastAPI backend on port 8000

### 4. Verify the installation

Check health endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

View API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Development Setup

### Running without Docker

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis:
```bash
# Using Docker for databases only
docker-compose up -d postgres redis
```

3. Run database migrations:
```bash
cd backend
alembic upgrade head
```

4. Start the development server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## 🔗 Webhook Integration

### Setting up Typeform Webhook

1. Get your webhook URL:
   - Local testing: Use ngrok to expose your local server
   ```bash
   ngrok http 8000
   # Your webhook URL: https://xxx.ngrok.io/api/v1/webhooks/typeform
   ```
   - Production: `https://yourdomain.com/api/v1/webhooks/typeform`

2. Configure in Typeform:
   - Go to your form's Connect panel
   - Add a webhook
   - Enter your webhook URL
   - Set secret (optional) and add to `.env` as `TYPEFORM_WEBHOOK_SECRET`

3. Test the webhook:
   - Submit a test response to your form
   - Check the dashboard at: `http://localhost:8000/api/v1/dashboards/view/{response_token}`

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /api/v1/health
```

#### Webhook Receiver
```http
POST /api/v1/webhooks/typeform
Content-Type: application/json
Typeform-Signature: sha256=xxx (optional)

{
  "event_id": "xxx",
  "event_type": "form_response",
  "form_response": {...}
}
```

#### View Dashboard
```http
GET /api/v1/dashboards/view/{token}
```
Returns HTML dashboard for the given submission token.

#### Get Dashboard Data
```http
GET /api/v1/dashboards/{submission_id}
```
Returns JSON data for the dashboard.

## 🎨 Dashboard Templates

FormFlow AI automatically detects the best template based on form content:

### Diet Plan Template
Triggered by keywords: diet, weight, calories, meal, nutrition
- 7-day meal plan
- Calorie and macro breakdown
- Shopping list
- Personalized tips

### Lead Score Template
Triggered by keywords: lead, company, budget, timeline, business
- Lead score (0-100)
- Score breakdown by criteria
- Recommended actions
- Follow-up timeline

### Event Registration Template
Triggered by keywords: event, registration, attend, ticket
- Registration confirmation
- Ticket number
- Event details
- QR code (coming soon)

### Generic Template
Default template for other form types
- Response summary
- Key insights
- Formatted data display

## 🧪 Testing

### Run tests
```bash
cd backend
pytest tests/ -v
```

### Test webhook locally
```bash
# Send test webhook
curl -X POST http://localhost:8000/api/v1/webhooks/typeform \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test123",
    "event_type": "form_response",
    "form_response": {
      "form_id": "abc123",
      "token": "unique_token_123",
      "submitted_at": "2025-01-01T10:00:00Z",
      "definition": {
        "title": "Test Form"
      },
      "answers": [
        {
          "field": {"id": "1", "title": "What is your goal?"},
          "type": "text",
          "text": "Lose weight"
        }
      ]
    }
  }'
```

## 🚢 Production Deployment

### Using Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add services:
```bash
railway add postgresql
railway add redis
```

4. Deploy:
```bash
railway up
```

### Using Docker

Build production image:
```bash
docker build -t formflow-ai ./backend
```

Run with environment variables:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  -e OPENAI_API_KEY=sk-... \
  formflow-ai
```

## 📈 Monitoring

- Health check: `/api/v1/health`
- Readiness check: `/api/v1/ready`
- Metrics: Configure Sentry and PostHog in `.env`

## 🔒 Security

- Webhook signature verification
- JWT token authentication
- CORS configuration
- Rate limiting (coming soon)
- SQL injection protection via SQLAlchemy ORM
- Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@formflow.ai

## 🎯 Roadmap

- [ ] Frontend dashboard builder
- [ ] More form integrations (Google Forms, JotForm)
- [ ] Custom AI prompts
- [ ] White-label options
- [ ] Advanced analytics
- [ ] Team collaboration features
- [ ] API for developers
- [ ] Mobile app

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Typeform for webhook integration
- FastAPI community
- All contributors

---

Built with ❤️ by the FormFlow AI team