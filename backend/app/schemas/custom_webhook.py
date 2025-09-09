from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

# Platform-specific presets for field mappings
PLATFORM_PRESETS = {
    "jotform": {
        "form_title": "$.formTitle",
        "submission_id": "$.submissionID", 
        "submitted_at": "$.createdAt",
        "answers": "$.answers"
    },
    "microsoft_forms": {
        "form_title": "$.title",
        "submission_id": "$.id",
        "submitted_at": "$.submitDate",
        "answers": "$.data"
    },
    "surveymonkey": {
        "form_title": "$.survey_title",
        "submission_id": "$.response_id",
        "submitted_at": "$.date_created",
        "answers": "$.pages[*].questions[*].answers"
    },
    "airtable": {
        "form_title": "$.fields.Form_Name",
        "submission_id": "$.id",
        "submitted_at": "$.createdTime",
        "answers": "$.fields"
    },
    "cognito": {
        "form_title": "$.Form.Name",
        "submission_id": "$.Entry.Number",
        "submitted_at": "$.Entry.DateCreated",
        "answers": "$.Entry"
    },
    "wpforms": {
        "form_title": "$.form_title",
        "submission_id": "$.entry_id",
        "submitted_at": "$.date",
        "answers": "$.fields"
    }
}

class WebhookConfigBase(BaseModel):
    name: str = Field(..., description="Name for this webhook configuration")
    platform: str = Field(default="custom", description="Platform type (jotform, microsoft_forms, etc.)")
    field_mappings: Dict[str, Any] = Field(default={}, description="JSON path mappings for fields")
    signature_secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    is_active: bool = Field(default=True, description="Whether this webhook is active")

class WebhookConfigCreate(WebhookConfigBase):
    pass

class WebhookConfigUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    field_mappings: Optional[Dict[str, Any]] = None
    signature_secret: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookConfigResponse(WebhookConfigBase):
    id: str
    user_id: str
    webhook_token: str
    webhook_url: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WebhookLogResponse(BaseModel):
    id: str
    status: str
    request_body: Optional[Dict[str, Any]]
    response_body: Optional[Dict[str, Any]]
    error_message: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomWebhookPayload(BaseModel):
    """Generic webhook payload that can accept any JSON structure"""
    data: Dict[str, Any] = Field(..., description="The webhook payload data")
    
    class Config:
        extra = "allow"  # Allow additional fields

class WebhookTestRequest(BaseModel):
    """Request for testing a webhook configuration"""
    webhook_config_id: str
    test_data: Dict[str, Any] = Field(..., description="Sample data to test with")

class WebhookTestResponse(BaseModel):
    """Response from webhook test"""
    success: bool
    processed_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    field_mapping_results: Optional[Dict[str, Any]] = None