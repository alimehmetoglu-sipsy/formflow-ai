-- FormFlow AI Database Schema
-- Generated for Claude PM Documentation
-- Last Updated: 2025-09-09

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    plan_type VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'business'
    trial_ends_at TIMESTAMP,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    preferences JSON,
    profile_picture_url VARCHAR(500),
    timezone VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Typeform Integration
    typeform_connected BOOLEAN DEFAULT false,
    typeform_api_key VARCHAR(255)
);

-- =====================================================
-- FORM SUBMISSIONS TABLE  
-- =====================================================
CREATE TABLE form_submissions (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id),
    typeform_id VARCHAR,
    form_title VARCHAR(255),
    response_id VARCHAR UNIQUE NOT NULL, -- Token from form platform
    submitted_at TIMESTAMP,
    answers JSON NOT NULL, -- Complete form response data
    processed BOOLEAN DEFAULT false,
    dashboard_url VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_form_submissions_response_id (response_id),
    INDEX idx_form_submissions_user_id (user_id),
    INDEX idx_form_submissions_typeform_id (typeform_id)
);

-- =====================================================
-- DASHBOARDS TABLE
-- =====================================================  
CREATE TABLE dashboards (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id VARCHAR REFERENCES form_submissions(id),
    template_type VARCHAR(50), -- 'diet_plan', 'lead_score', 'event', 'generic'
    template_id VARCHAR REFERENCES dashboard_templates(id),
    ai_generated_content JSON,
    html_content TEXT,
    widgets JSON, -- Widget configurations for dashboard
    theme JSON,   -- Theme configuration  
    layout JSON,  -- Layout configuration
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_dashboards_submission_id (submission_id),
    INDEX idx_dashboards_template_type (template_type)
);

-- =====================================================
-- DASHBOARD TEMPLATES TABLE
-- =====================================================
CREATE TABLE dashboard_templates (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'health', 'sales', 'events', 'survey'
    template_data JSON NOT NULL,
    preview_image_url VARCHAR(500),
    is_premium BOOLEAN DEFAULT false,
    created_by VARCHAR REFERENCES users(id),
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(2,1) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- CUSTOM TEMPLATES TABLE  
-- =====================================================
CREATE TABLE custom_templates (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_data JSON NOT NULL,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- WIDGET CONFIGURATIONS TABLE
-- =====================================================
CREATE TABLE widget_configurations (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id VARCHAR REFERENCES dashboards(id),
    widget_type VARCHAR(100) NOT NULL, -- 'chart', 'metric', 'table', 'text'
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0, 
    width INTEGER DEFAULT 1,
    height INTEGER DEFAULT 1,
    config JSON NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- WEBHOOK CONFIGURATIONS TABLE
-- =====================================================  
CREATE TABLE webhook_configs (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    webhook_token VARCHAR UNIQUE NOT NULL, -- 'wh_' + secure token
    platform VARCHAR(50) DEFAULT 'custom', -- 'jotform', 'microsoft_forms', 'surveymonkey', 'custom'
    field_mappings JSON DEFAULT '{}',
    signature_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_webhook_configs_user_id (user_id),
    INDEX idx_webhook_configs_token (webhook_token)
);

-- =====================================================
-- WEBHOOK LOGS TABLE
-- =====================================================
CREATE TABLE webhook_logs (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_config_id VARCHAR REFERENCES webhook_configs(id) NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'success', 'error', 'processing'  
    request_body JSON,
    response_body JSON,
    error_message VARCHAR,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_webhook_logs_config_id (webhook_config_id),
    INDEX idx_webhook_logs_created_at (created_at)
);

-- =====================================================
-- SUBSCRIPTIONS TABLE (Payment Integration)
-- =====================================================
CREATE TABLE subscriptions (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id) NOT NULL,
    lemonsqueezy_subscription_id VARCHAR,
    plan_name VARCHAR(50) NOT NULL, -- 'free', 'pro', 'business'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'expired'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT false,
    lemonsqueezy_customer_id VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_subscriptions_user_id (user_id),
    INDEX idx_subscriptions_lemonsqueezy_id (lemonsqueezy_subscription_id)
);

-- =====================================================
-- USAGE TRACKING TABLE
-- =====================================================
CREATE TABLE usage_tracking (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id) NOT NULL,
    resource_type VARCHAR(50) NOT NULL, -- 'dashboard', 'webhook', 'api_call'
    resource_id VARCHAR,
    month_year VARCHAR(7) NOT NULL, -- 'YYYY-MM' format
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, resource_type, month_year),
    INDEX idx_usage_tracking_user_month (user_id, month_year)
);

-- =====================================================
-- INTEGRATIONS TABLE  
-- =====================================================
CREATE TABLE integrations (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR REFERENCES users(id) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'typeform', 'google_forms', 'jotform'
    platform_user_id VARCHAR,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_integrations_user_platform (user_id, platform)
);

-- =====================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =====================================================

-- Insert default dashboard templates
INSERT INTO dashboard_templates (name, description, category, template_data, is_premium) VALUES 
('Diet Plan', 'Personalized nutrition plan with meal recommendations', 'health', '{"widgets": [{"type": "calorie_chart"}, {"type": "meal_list"}]}', false),
('Lead Score', 'Sales lead qualification and scoring dashboard', 'sales', '{"widgets": [{"type": "score_gauge"}, {"type": "action_items"}]}', false),
('Event Registration', 'Event signup confirmation and details', 'events', '{"widgets": [{"type": "ticket_info"}, {"type": "event_details"}]}', false),
('Survey Analysis', 'Form response analysis and insights', 'survey', '{"widgets": [{"type": "response_summary"}, {"type": "insights"}]}', false);

-- Create indexes for performance  
CREATE INDEX CONCURRENTLY idx_dashboards_created_at ON dashboards(created_at DESC);
CREATE INDEX CONCURRENTLY idx_form_submissions_created_at ON form_submissions(created_at DESC);
CREATE INDEX CONCURRENTLY idx_webhook_logs_status ON webhook_logs(status);

-- =====================================================
-- DATABASE VIEWS
-- =====================================================

-- User dashboard statistics view
CREATE VIEW user_dashboard_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.plan_type,
    COUNT(d.id) as total_dashboards,
    SUM(d.view_count) as total_views,
    COUNT(CASE WHEN fs.created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as recent_submissions
FROM users u
LEFT JOIN form_submissions fs ON u.id = fs.user_id
LEFT JOIN dashboards d ON fs.id = d.submission_id
GROUP BY u.id, u.email, u.plan_type;

-- Active webhook configurations view  
CREATE VIEW active_webhooks AS
SELECT 
    wc.*,
    u.email as user_email,
    u.plan_type,
    COUNT(wl.id) as log_count,
    MAX(wl.created_at) as last_activity
FROM webhook_configs wc
JOIN users u ON wc.user_id = u.id
LEFT JOIN webhook_logs wl ON wc.id = wl.webhook_config_id
WHERE wc.is_active = true
GROUP BY wc.id, u.email, u.plan_type;

-- =====================================================
-- FUNCTIONS AND TRIGGERS  
-- =====================================================

-- Function to generate webhook tokens
CREATE OR REPLACE FUNCTION generate_webhook_token()
RETURNS VARCHAR AS $$
BEGIN
    RETURN 'wh_' || encode(gen_random_bytes(32), 'base64url');
END;
$$ LANGUAGE plpgsql;

-- Trigger to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON dashboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_webhook_configs_updated_at BEFORE UPDATE ON webhook_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();