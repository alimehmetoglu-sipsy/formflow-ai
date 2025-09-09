# FormFlow AI - Test Accounts & Demo Data

## 🧪 Test Account Overview

This document contains test accounts, sample data, and demo configurations for development, testing, and demonstration purposes. **⚠️ Never use these accounts in production!**

---

## 👤 User Test Accounts

### Admin Test Account
**Email:** admin@formflow-test.com  
**Password:** AdminTest123!  
**Plan:** Business (Test)  
**Purpose:** Testing admin features, system management, user support scenarios

**Account Details:**
- Full Name: Admin Test User
- Created: October 2024
- Dashboards: 25+ test dashboards
- Role: Super Admin
- API Keys: 2 test keys generated

**Test Scenarios:**
- User management and support
- System health monitoring
- Billing and subscription management
- Analytics and reporting features

---

### Health Coach Test Account
**Email:** sarah@healthcoach-demo.com  
**Password:** HealthCoach123!  
**Plan:** Pro (Test)  
**Purpose:** Health & wellness use case testing

**Account Details:**
- Full Name: Sarah Johnson (Test Health Coach)
- Created: November 2024
- Dashboards: 15 health-focused dashboards
- Typeform Connected: Yes (test form)
- Custom Branding: Enabled

**Sample Dashboards:**
1. "BMI Assessment Dashboard" - 47 views
2. "Nutrition Plan Generator" - 23 views  
3. "Fitness Goal Tracker" - 31 views
4. "Dietary Restrictions Analysis" - 18 views

**Test Data Focus:**
- Health metrics (BMI, weight, fitness levels)
- Dietary preferences and restrictions
- Workout routines and goals
- Progress tracking over time

---

### Sales Manager Test Account
**Email:** marcus@salesteam-demo.com  
**Password:** SalesDemo123!  
**Plan:** Business (Test)  
**Purpose:** B2B sales and lead qualification testing

**Account Details:**
- Full Name: Marcus Rodriguez (Test Sales Manager)
- Created: November 2024
- Dashboards: 12 sales-focused dashboards
- Google Forms Connected: Yes (lead qualification form)
- Team Members: 3 test team members

**Sample Dashboards:**
1. "Lead Qualification Dashboard" - 89 views
2. "Sales Pipeline Analysis" - 56 views
3. "Client Intake Assessment" - 34 views
4. "Product Demo Feedback" - 27 views

**Test Data Focus:**
- Lead qualification scores
- Budget and timeline information
- Decision-maker identification
- Competition analysis

---

### Event Coordinator Test Account
**Email:** david@events-demo.com  
**Password:** EventDemo123!  
**Plan:** Pro (Test)  
**Purpose:** Event management and logistics testing

**Account Details:**
- Full Name: David Chen (Test Event Coordinator)
- Created: December 2024
- Dashboards: 8 event-focused dashboards
- Google Forms Connected: Yes (event registration)

**Sample Dashboards:**
1. "Corporate Event Registration" - 112 views
2. "Dietary Restrictions Summary" - 67 views
3. "Training Session Feedback" - 43 views
4. "Networking Event Analytics" - 29 views

**Test Data Focus:**
- Attendee preferences and requirements
- Dietary restrictions and accessibility needs
- Event feedback and satisfaction
- Logistics and planning data

---

### Free Plan Test Account
**Email:** freemium@test-user.com  
**Password:** FreePlan123!  
**Plan:** Free  
**Purpose:** Testing free plan limitations and upgrade flows

**Account Details:**
- Full Name: Free Plan Test User
- Created: December 2024
- Dashboards: 5/5 (at limit)
- Forms Connected: 3/3 (at limit)
- Submissions This Month: 95/100

**Test Scenarios:**
- Free plan limit enforcement
- Upgrade prompts and flows
- Feature restrictions
- Conversion optimization

---

## 🔗 Test Form Integrations

### Typeform Test Forms

#### Health Assessment Form
**Form ID:** test-health-form-abc123  
**Webhook URL:** `https://api.formflow-test.com/api/v1/webhooks/typeform`  
**Webhook Secret:** `test-webhook-secret-health`

**Sample Fields:**
- Name (short text)
- Age (number)
- Current weight (number)
- Target weight (number)
- Fitness level (multiple choice)
- Dietary restrictions (multiple choice)
- Health goals (long text)
- Email (email)

**Test Responses:** 47 sample responses with realistic health data

---

#### Lead Qualification Form  
**Form ID:** test-lead-form-xyz789  
**Webhook URL:** `https://api.formflow-test.com/api/v1/webhooks/typeform`  
**Webhook Secret:** `test-webhook-secret-sales`

**Sample Fields:**
- Company name (short text)
- Contact person (short text)
- Email (email)
- Phone (phone number)
- Company size (multiple choice)
- Budget range (multiple choice)
- Timeline (multiple choice)
- Current solution (short text)
- Pain points (long text)

**Test Responses:** 34 sample responses with B2B lead data

---

### Google Forms Test Forms

#### Event Registration Form
**Form ID:** test-event-form-456def  
**Apps Script Webhook:** Configured to forward to FormFlow AI
**Webhook URL:** `https://api.formflow-test.com/api/v1/webhooks/google-forms`

**Sample Fields:**
- Full name
- Email address  
- Company/Organization
- Dietary restrictions
- Accessibility needs
- Session preferences
- Networking interests
- Contact preferences

**Test Responses:** 28 sample event registrations

---

### Custom Webhook Test Configurations

#### JotForm Test Webhook
**Webhook Token:** `wh_test_jotform_789xyz`  
**Platform:** jotform  
**Field Mappings:**
```json
{
  "form_title": "$.formTitle",
  "submission_id": "$.submissionID",
  "submitted_at": "$.createdAt",
  "respondent_name": "$.answers['3'].answer",
  "respondent_email": "$.answers['5'].answer",
  "company": "$.answers['7'].answer"
}
```

**Test Payloads:** 15+ sample JotForm webhook payloads

---

## 📊 Sample Dashboard Data

### Health Dashboard Test Data
```json
{
  "dashboard_id": "test-health-dash-001",
  "user_id": "sarah@healthcoach-demo.com",
  "template_type": "health",
  "form_data": {
    "name": "Alex Johnson",
    "age": 32,
    "current_weight": 180,
    "target_weight": 160,
    "height": "5'8\"",
    "fitness_level": "Beginner",
    "goals": ["Weight loss", "Muscle building"],
    "dietary_restrictions": ["Vegetarian", "Gluten-free"],
    "exercise_preference": "Home workouts"
  },
  "ai_insights": {
    "bmi_current": 27.4,
    "bmi_target": 24.3,
    "weight_loss_plan": "Gradual 1-2 lbs per week",
    "recommended_calories": 1800,
    "exercise_frequency": "4-5 times per week"
  },
  "created_at": "2024-12-15T14:30:00Z",
  "view_count": 47
}
```

### Sales Dashboard Test Data  
```json
{
  "dashboard_id": "test-sales-dash-002",
  "user_id": "marcus@salesteam-demo.com", 
  "template_type": "lead_scoring",
  "form_data": {
    "company": "TechCorp Solutions",
    "contact": "Jennifer Martinez",
    "email": "j.martinez@techcorp.com",
    "company_size": "50-200 employees",
    "budget": "$10,000-$50,000",
    "timeline": "Within 3 months",
    "current_solution": "Manual processes",
    "pain_points": "Too much manual data entry, need automation"
  },
  "ai_insights": {
    "lead_score": 85,
    "qualification": "High Priority",
    "recommended_actions": [
      "Schedule demo within 48 hours",
      "Focus on automation ROI",
      "Involve technical stakeholder"
    ],
    "estimated_deal_size": "$25,000"
  },
  "created_at": "2024-12-20T09:15:00Z",
  "view_count": 23
}
```

---

## 🔑 Test API Keys

### Development API Keys
**Note:** These keys only work in development environment

#### Admin Test API Key
**Key:** `test_sk_admin_1234567890abcdef`  
**User:** admin@formflow-test.com  
**Permissions:** Full admin access  
**Rate Limit:** 1000 requests/hour

#### Standard Test API Key  
**Key:** `test_sk_user_abcdef1234567890`  
**User:** sarah@healthcoach-demo.com  
**Permissions:** Standard user access  
**Rate Limit:** 100 requests/hour

#### Limited Test API Key
**Key:** `test_sk_limited_567890abcdef1234`  
**User:** freemium@test-user.com  
**Permissions:** Read-only access  
**Rate Limit:** 50 requests/hour

---

## 🧾 Test Subscription Data

### LemonSqueezy Test Subscriptions

#### Pro Plan Test Subscription
**Subscription ID:** `test_sub_pro_12345`  
**Customer ID:** `test_customer_67890`  
**Plan:** Pro ($17/month)  
**Status:** Active  
**Current Period:** 2024-12-01 to 2025-01-01  
**User:** sarah@healthcoach-demo.com

#### Business Plan Test Subscription  
**Subscription ID:** `test_sub_business_54321`  
**Customer ID:** `test_customer_09876`  
**Plan:** Business ($47/month)  
**Status:** Active  
**Current Period:** 2024-12-15 to 2025-01-15  
**User:** marcus@salesteam-demo.com

#### Cancelled Subscription (Test Scenario)
**Subscription ID:** `test_sub_cancelled_11111`  
**Customer ID:** `test_customer_22222`  
**Plan:** Pro ($17/month)  
**Status:** Cancelled (ends 2025-02-01)  
**User:** cancelled@test-user.com

---

## 📧 Test Email Configurations

### Test Email Accounts
**SMTP Server:** mailtrap.io (development)  
**Username:** test-formflow-123  
**Password:** test-smtp-password

### Sample Email Templates

#### Dashboard Ready Email
**To:** sarah@healthcoach-demo.com  
**Subject:** Your health dashboard is ready! 🎉  
**Template:** `dashboard_ready.html`  
**Variables:**
- `{{user_name}}`: Sarah Johnson  
- `{{dashboard_url}}`: https://test.formflow.ai/dashboard/view/abc123
- `{{form_title}}`: Health Assessment

#### Welcome Email
**To:** new@test-user.com  
**Subject:** Welcome to FormFlow AI!  
**Template:** `welcome.html`  
**Variables:**
- `{{user_name}}`: Test User  
- `{{onboarding_url}}`: https://test.formflow.ai/onboarding

---

## 🧪 Automated Testing Data

### Playwright Test Data

#### End-to-End Test Scenarios
```javascript
// Test user login and dashboard creation
const testUser = {
  email: 'e2e@test-formflow.com',
  password: 'E2ETest123!',
  dashboardName: 'E2E Test Dashboard'
};

// Sample form submission for testing
const testFormSubmission = {
  formId: 'e2e-test-form',
  responses: {
    name: 'E2E Test User',
    email: 'e2e-response@test.com',
    rating: '5',
    feedback: 'This is a test submission for automated testing'
  }
};
```

### Load Testing Data
**Test Users:** 1000 simulated concurrent users  
**Test Duration:** 10 minutes  
**API Endpoints:** All major endpoints included  
**Expected Response Times:** <2s for 95th percentile

---

## 🔧 Development Environment Setup

### Test Database Configuration
```sql
-- Test database: formflow_test
-- Connection: postgresql://test_user:test_password@localhost:5432/formflow_test

-- Sample test data insertion
INSERT INTO users (email, full_name, password_hash, plan_type) VALUES
('admin@formflow-test.com', 'Admin Test User', '$2b$12$...', 'business'),
('sarah@healthcoach-demo.com', 'Sarah Johnson', '$2b$12$...', 'pro'),
('marcus@salesteam-demo.com', 'Marcus Rodriguez', '$2b$12$...', 'business');
```

### Environment Variables for Testing
```bash
# .env.test
DATABASE_URL=postgresql://test_user:test_password@localhost:5432/formflow_test
REDIS_URL=redis://localhost:6379/1
OPENAI_API_KEY=test_openai_key_not_real
JWT_SECRET_KEY=test-jwt-secret-key-not-for-production
ENVIRONMENT=test
DEBUG=true

# Test-specific settings
WEBHOOK_SIGNATURE_VERIFICATION=false
EMAIL_BACKEND=console
RATE_LIMITING_ENABLED=false
```

---

## ⚠️ Security & Best Practices

### Test Account Security
- **Never use test accounts in production**
- **Test passwords are intentionally simple - never use in real environments**
- **Test API keys have no real permissions and don't work in production**
- **All test data should be considered public and non-sensitive**

### Data Cleanup
- Test accounts are reset monthly
- Dashboard data is cleaned every 2 weeks
- API usage logs are purged weekly
- Email test history is cleared daily

### Access Control
- Test accounts are only accessible in development/staging environments
- Production database has no test data
- Test API keys are invalidated in production deployments

---

## 📝 Usage Instructions

### For Developers
1. **Login:** Use any test account credentials above
2. **API Testing:** Use provided API keys with development endpoints
3. **Webhook Testing:** Send payloads to test webhook endpoints
4. **Dashboard Testing:** Create dashboards using sample form data

### For QA Testing
1. **User Flows:** Test complete user journeys with realistic data
2. **Edge Cases:** Use boundary conditions and error scenarios  
3. **Cross-browser:** Test on different devices and browsers
4. **Performance:** Monitor dashboard generation times and UI responsiveness

### For Demo Purposes  
1. **Choose Appropriate Account:** Select account matching demo scenario
2. **Use Realistic Data:** Sample dashboards represent real use cases
3. **Showcase Features:** Demonstrate key platform capabilities
4. **Reset After Demo:** Clear demo-specific data if needed

---

## 🔄 Maintenance & Updates

### Monthly Tasks:
- [ ] Reset test account passwords
- [ ] Update sample dashboard data
- [ ] Refresh webhook test payloads  
- [ ] Clean test database of old records

### Quarterly Tasks:
- [ ] Review and update test scenarios
- [ ] Add new test accounts for new features
- [ ] Update API keys and credentials
- [ ] Refresh demo data with current trends

**Last Updated:** January 28, 2025  
**Next Review:** February 28, 2025  

---

This test account documentation is maintained by the QA team and updated whenever new testing scenarios or demo requirements are identified.