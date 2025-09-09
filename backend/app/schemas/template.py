from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    widgets: List[Dict[str, Any]] = []
    theme: Dict[str, Any] = {}
    layout: Dict[str, Any] = {}
    tags: Optional[List[str]] = []

class TemplateCreate(TemplateBase):
    is_public: bool = False

class TemplateUpdate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: str
    thumbnail_url: Optional[str] = None
    is_system: bool = False
    is_public: bool = False
    usage_count: int = 0
    rating: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[str] = None
    widgets: List[Dict[str, Any]] = []
    theme: Dict[str, Any] = {}
    layout: Dict[str, Any] = {}
    is_public: bool = False

class CustomTemplateCreate(CustomTemplateBase):
    pass

class CustomTemplateResponse(CustomTemplateBase):
    id: str
    user_id: str
    share_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class WidgetConfigurationBase(BaseModel):
    widget_type: str
    position: Dict[str, int]  # {x, y, w, h}
    size: str  # small, medium, large, full-width
    title: Optional[str] = None
    description: Optional[str] = None
    data_source: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class WidgetConfigurationCreate(WidgetConfigurationBase):
    dashboard_id: str

class WidgetConfigurationResponse(WidgetConfigurationBase):
    id: str
    dashboard_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True