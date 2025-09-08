from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class DashboardCreate(BaseModel):
    submission_id: str
    template_type: str
    ai_generated_content: Dict[str, Any]
    html_content: str

class DashboardResponse(BaseModel):
    id: str
    submission_id: str
    template_type: str
    ai_generated_content: Dict[str, Any]
    view_count: int
    created_at: datetime
    dashboard_url: str
    token: Optional[str] = None  # For accessing the dashboard
    
    class Config:
        from_attributes = True