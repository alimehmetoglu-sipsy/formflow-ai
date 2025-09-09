"""
Pydantic schemas for Multi-Form Dashboard API (FA-44)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class MultiFormMappingBase(BaseModel):
    """Base schema for form mapping"""
    form_type: str = Field(..., description="Type of form platform")
    form_external_id: Optional[str] = Field(None, description="External form ID")
    form_title: str = Field(..., description="Form title for display")
    field_mappings: Optional[Dict[str, str]] = Field(default_factory=dict)
    weight: float = Field(1.0, ge=0, le=10, description="Weight for aggregation")
    priority: int = Field(0, ge=0, le=100, description="Priority for conflict resolution")


class MultiFormMappingCreate(MultiFormMappingBase):
    """Schema for creating form mapping"""
    pass


class MultiFormMappingResponse(MultiFormMappingBase):
    """Schema for form mapping response"""
    id: UUID
    dashboard_id: UUID
    is_active: bool
    total_responses: int
    last_response_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CustomMetricBase(BaseModel):
    """Base schema for custom metric"""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    metric_type: str = Field(..., description="calculated, aggregated, or kpi")
    formula: str = Field(..., description="Metric calculation formula")
    unit: Optional[str] = Field(None, description="Metric unit")
    visualization_type: Optional[str] = Field("number", description="Visualization type")
    visualization_config: Optional[Dict[str, Any]] = None
    is_kpi: bool = Field(False)
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    enable_alerts: bool = Field(False)
    alert_config: Optional[Dict[str, Any]] = None


class CustomMetricCreate(CustomMetricBase):
    """Schema for creating custom metric"""
    
    @validator("metric_type")
    def validate_metric_type(cls, v):
        allowed_types = ["calculated", "aggregated", "kpi"]
        if v not in allowed_types:
            raise ValueError(f"metric_type must be one of {allowed_types}")
        return v
    
    @validator("visualization_type")
    def validate_visualization_type(cls, v):
        allowed_types = ["gauge", "line", "bar", "number", "pie", "scatter"]
        if v and v not in allowed_types:
            raise ValueError(f"visualization_type must be one of {allowed_types}")
        return v


class CustomMetricResponse(CustomMetricBase):
    """Schema for custom metric response"""
    id: UUID
    dashboard_id: UUID
    last_calculated_value: Optional[float]
    last_calculated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ScheduledReportBase(BaseModel):
    """Base schema for scheduled report"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_type: str = Field(..., description="daily, weekly, monthly, or custom")
    schedule_config: Dict[str, Any] = Field(..., description="Schedule configuration")
    report_format: str = Field("pdf", description="Report format")
    include_sections: Optional[List[str]] = Field(default_factory=list)
    filter_override: Optional[Dict[str, Any]] = None
    recipients: Dict[str, List[str]] = Field(..., description="Email recipients")
    email_subject: Optional[str] = None
    email_body_template: Optional[str] = None
    is_active: bool = Field(True)


class ScheduledReportCreate(ScheduledReportBase):
    """Schema for creating scheduled report"""
    
    @validator("schedule_type")
    def validate_schedule_type(cls, v):
        allowed_types = ["daily", "weekly", "monthly", "custom"]
        if v not in allowed_types:
            raise ValueError(f"schedule_type must be one of {allowed_types}")
        return v
    
    @validator("report_format")
    def validate_report_format(cls, v):
        allowed_formats = ["pdf", "excel", "csv", "html"]
        if v not in allowed_formats:
            raise ValueError(f"report_format must be one of {allowed_formats}")
        return v


class ScheduledReportResponse(ScheduledReportBase):
    """Schema for scheduled report response"""
    id: UUID
    dashboard_id: UUID
    user_id: UUID
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    next_run_at: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AggregationConfig(BaseModel):
    """Schema for aggregation configuration"""
    aggregation_method: str = Field("union", description="union, intersection, or weighted")
    conflict_resolution: str = Field("latest", description="latest, average, or priority")
    
    @validator("aggregation_method")
    def validate_aggregation_method(cls, v):
        allowed_methods = ["union", "intersection", "weighted"]
        if v not in allowed_methods:
            raise ValueError(f"aggregation_method must be one of {allowed_methods}")
        return v
    
    @validator("conflict_resolution")
    def validate_conflict_resolution(cls, v):
        allowed_methods = ["latest", "average", "priority"]
        if v not in allowed_methods:
            raise ValueError(f"conflict_resolution must be one of {allowed_methods}")
        return v


class AnalyticsConfig(BaseModel):
    """Schema for analytics configuration"""
    metrics: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    kpis: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class FilterConfig(BaseModel):
    """Schema for filter configuration"""
    date_range: Optional[Dict[str, str]] = None
    segments: Optional[List[str]] = Field(default_factory=list)
    custom_filters: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class MultiFormDashboardBase(BaseModel):
    """Base schema for multi-form dashboard"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    aggregation_config: AggregationConfig
    analytics_config: Optional[AnalyticsConfig] = None
    filter_config: Optional[FilterConfig] = None
    is_public: bool = Field(False)


class MultiFormDashboardCreate(MultiFormDashboardBase):
    """Schema for creating multi-form dashboard"""
    form_mappings: List[MultiFormMappingCreate] = Field(..., min_items=1)
    
    @validator("form_mappings")
    def validate_form_mappings(cls, v):
        if len(v) > 10:
            raise ValueError("Cannot add more than 10 form mappings to a dashboard")
        return v


class MultiFormDashboardUpdate(BaseModel):
    """Schema for updating multi-form dashboard"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    aggregation_config: Optional[AggregationConfig] = None
    analytics_config: Optional[AnalyticsConfig] = None
    filter_config: Optional[FilterConfig] = None
    is_public: Optional[bool] = None


class MultiFormDashboardResponse(MultiFormDashboardBase):
    """Schema for multi-form dashboard response"""
    id: UUID
    user_id: UUID
    share_token: Optional[str]
    cached_data: Optional[Dict[str, Any]]
    cache_updated_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    form_mappings: List[MultiFormMappingResponse] = Field(default_factory=list)
    custom_metrics: List[CustomMetricResponse] = Field(default_factory=list)
    scheduled_reports: List[ScheduledReportResponse] = Field(default_factory=list)

    class Config:
        orm_mode = True


class AggregationResultResponse(BaseModel):
    """Schema for aggregation result response"""
    status: str = Field(..., description="completed, processing, or failed")
    message: Optional[str] = None
    job_id: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AggregationJobResponse(BaseModel):
    """Schema for aggregation job response"""
    id: UUID
    dashboard_id: UUID
    job_type: str
    status: str
    total_forms: Optional[int]
    processed_forms: int
    total_records: Optional[int]
    processed_records: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    error_message: Optional[str]
    result_summary: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True