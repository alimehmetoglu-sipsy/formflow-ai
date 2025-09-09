"""
Pydantic Schemas for CRM Export (FA-48)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class CRMType(str, Enum):
    """Supported CRM types"""
    salesforce = "salesforce"
    hubspot = "hubspot"
    pipedrive = "pipedrive"
    generic = "generic"


class ExportFormat(str, Enum):
    """Export file formats"""
    csv = "csv"
    json = "json"
    excel = "excel"
    xml = "xml"


class CRMExportRequest(BaseModel):
    """Request schema for CRM export"""
    lead_ids: Optional[List[UUID]] = Field(None, description="Specific lead IDs to export")
    crm_type: CRMType = Field(CRMType.generic, description="Target CRM system")
    format: ExportFormat = Field(ExportFormat.csv, description="Export file format")
    include_scores: bool = Field(True, description="Include lead scores")
    include_insights: bool = Field(True, description="Include AI insights")
    include_recommendations: bool = Field(False, description="Include follow-up recommendations")
    date_from: Optional[datetime] = Field(None, description="Export leads from this date")
    date_to: Optional[datetime] = Field(None, description="Export leads until this date")
    custom_field_mapping: Optional[Dict[str, str]] = Field(None, description="Custom field mappings")


class FieldMappingResponse(BaseModel):
    """Response schema for field mappings"""
    crm_type: CRMType
    standard_fields: Dict[str, str] = Field(..., description="Standard CRM fields")
    custom_fields: Dict[str, str] = Field(..., description="Custom fields for FormFlow data")
    total_fields: int


class ExportHistoryResponse(BaseModel):
    """Response schema for export history"""
    id: str
    export_date: datetime
    crm_type: str
    format: str
    lead_count: int
    file_name: str
    status: str = Field(..., description="completed, failed, processing")
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class WebhookConfig(BaseModel):
    """Configuration for CRM webhook integration"""
    crm_type: CRMType
    webhook_url: str = Field(..., description="CRM webhook endpoint")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    secret: Optional[str] = Field(None, description="Webhook secret for verification")
    active: bool = Field(True, description="Whether webhook is active")
    retry_on_failure: bool = Field(True, description="Retry failed webhook calls")
    max_retries: int = Field(3, ge=1, le=10)


class ImportInstructions(BaseModel):
    """Import instructions for specific CRM"""
    title: str
    steps: List[str]
    tips: List[str]
    video_url: Optional[str] = None
    documentation_url: Optional[str] = None