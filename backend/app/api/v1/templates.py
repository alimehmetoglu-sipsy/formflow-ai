from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.template import DashboardTemplate, CustomTemplate, WidgetConfiguration
from app.models.form import Dashboard
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.template import (
    TemplateResponse,
    TemplateCreate,
    TemplateUpdate,
    CustomTemplateCreate,
    CustomTemplateResponse,
    WidgetConfigurationCreate
)
import uuid

router = APIRouter()

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    is_public: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List available dashboard templates"""
    query = db.query(DashboardTemplate)
    
    if category:
        query = query.filter(DashboardTemplate.category == category)
    
    if is_public:
        query = query.filter(DashboardTemplate.is_public == True)
    
    templates = query.offset(skip).limit(limit).all()
    
    return [TemplateResponse(
        id=t.id,
        name=t.name,
        description=t.description,
        category=t.category,
        icon=t.icon,
        thumbnail_url=t.thumbnail_url,
        widgets=t.widgets,
        theme=t.theme,
        layout=t.layout,
        is_system=t.is_system,
        is_public=t.is_public,
        usage_count=t.usage_count,
        rating=t.rating,
        tags=t.tags,
        created_at=t.created_at
    ) for t in templates]

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    template = db.query(DashboardTemplate).filter_by(id=template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Increment usage count
    template.usage_count += 1
    db.commit()
    
    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        category=template.category,
        icon=template.icon,
        thumbnail_url=template.thumbnail_url,
        widgets=template.widgets,
        theme=template.theme,
        layout=template.layout,
        is_system=template.is_system,
        is_public=template.is_public,
        usage_count=template.usage_count,
        rating=template.rating,
        tags=template.tags,
        created_at=template.created_at
    )

@router.post("/custom", response_model=CustomTemplateResponse)
async def create_custom_template(
    template_data: CustomTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a custom template"""
    
    custom_template = CustomTemplate(
        user_id=current_user.id,
        template_id=template_data.template_id,
        name=template_data.name,
        description=template_data.description,
        widgets=template_data.widgets,
        theme=template_data.theme,
        layout=template_data.layout,
        is_public=template_data.is_public
    )
    
    if template_data.is_public:
        custom_template.share_url = str(uuid.uuid4())
    
    db.add(custom_template)
    db.commit()
    db.refresh(custom_template)
    
    return CustomTemplateResponse(
        id=custom_template.id,
        user_id=custom_template.user_id,
        template_id=custom_template.template_id,
        name=custom_template.name,
        description=custom_template.description,
        widgets=custom_template.widgets,
        theme=custom_template.theme,
        layout=custom_template.layout,
        is_public=custom_template.is_public,
        share_url=custom_template.share_url,
        created_at=custom_template.created_at
    )

@router.get("/custom/my", response_model=List[CustomTemplateResponse])
async def list_my_custom_templates(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List custom templates created by the current user"""
    
    templates = db.query(CustomTemplate).filter_by(
        user_id=current_user.id
    ).offset(skip).limit(limit).all()
    
    return [CustomTemplateResponse(
        id=t.id,
        user_id=t.user_id,
        template_id=t.template_id,
        name=t.name,
        description=t.description,
        widgets=t.widgets,
        theme=t.theme,
        layout=t.layout,
        is_public=t.is_public,
        share_url=t.share_url,
        created_at=t.created_at
    ) for t in templates]

@router.put("/custom/{template_id}", response_model=CustomTemplateResponse)
async def update_custom_template(
    template_id: str,
    template_update: CustomTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a custom template"""
    
    template = db.query(CustomTemplate).filter_by(
        id=template_id,
        user_id=current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission"
        )
    
    template.name = template_update.name
    template.description = template_update.description
    template.widgets = template_update.widgets
    template.theme = template_update.theme
    template.layout = template_update.layout
    template.is_public = template_update.is_public
    
    if template_update.is_public and not template.share_url:
        template.share_url = str(uuid.uuid4())
    elif not template_update.is_public:
        template.share_url = None
    
    db.commit()
    db.refresh(template)
    
    return CustomTemplateResponse(
        id=template.id,
        user_id=template.user_id,
        template_id=template.template_id,
        name=template.name,
        description=template.description,
        widgets=template.widgets,
        theme=template.theme,
        layout=template.layout,
        is_public=template.is_public,
        share_url=template.share_url,
        created_at=template.created_at
    )

@router.delete("/custom/{template_id}")
async def delete_custom_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a custom template"""
    
    template = db.query(CustomTemplate).filter_by(
        id=template_id,
        user_id=current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}

@router.post("/apply/{dashboard_id}")
async def apply_template_to_dashboard(
    dashboard_id: str,
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply a template to an existing dashboard"""
    
    # Get the dashboard
    dashboard = db.query(Dashboard).filter_by(id=dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Get the template
    template = db.query(DashboardTemplate).filter_by(id=template_id).first()
    if not template:
        # Check custom templates
        template = db.query(CustomTemplate).filter_by(id=template_id).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
    
    # Apply template to dashboard
    dashboard.template_id = template_id
    dashboard.widgets = template.widgets
    dashboard.theme = template.theme
    dashboard.layout = template.layout
    
    db.commit()
    
    return {"message": "Template applied successfully", "dashboard_id": dashboard_id}

@router.get("/widgets/library")
async def get_widget_library():
    """Get the widget library with all available widget types"""
    
    widget_library = [
        {
            "type": "chart",
            "name": "Chart",
            "description": "Bar, line, pie, area charts",
            "icon": "📊",
            "defaultSize": "medium",
            "minSize": {"w": 3, "h": 3},
            "maxSize": {"w": 12, "h": 8},
            "configurable": True
        },
        {
            "type": "stats-card",
            "name": "Stats Card",
            "description": "Key metrics display",
            "icon": "📈",
            "defaultSize": "small",
            "minSize": {"w": 3, "h": 2},
            "maxSize": {"w": 6, "h": 4},
            "configurable": True
        },
        {
            "type": "table",
            "name": "Table",
            "description": "Data table with sorting",
            "icon": "📋",
            "defaultSize": "large",
            "minSize": {"w": 4, "h": 3},
            "maxSize": {"w": 12, "h": 8},
            "configurable": True
        },
        {
            "type": "text-block",
            "name": "Text Block",
            "description": "Rich text content",
            "icon": "📝",
            "defaultSize": "medium",
            "minSize": {"w": 3, "h": 2},
            "maxSize": {"w": 12, "h": 6},
            "configurable": True
        },
        {
            "type": "metric",
            "name": "Metric",
            "description": "Single metric with progress",
            "icon": "🎯",
            "defaultSize": "small",
            "minSize": {"w": 3, "h": 2},
            "maxSize": {"w": 6, "h": 4},
            "configurable": True
        },
        {
            "type": "gauge",
            "name": "Gauge",
            "description": "Visual gauge meter",
            "icon": "🌡️",
            "defaultSize": "medium",
            "minSize": {"w": 4, "h": 3},
            "maxSize": {"w": 6, "h": 5},
            "configurable": True
        },
        {
            "type": "list",
            "name": "List",
            "description": "Bullet or numbered list",
            "icon": "📑",
            "defaultSize": "medium",
            "minSize": {"w": 3, "h": 3},
            "maxSize": {"w": 6, "h": 8},
            "configurable": True
        },
        {
            "type": "timeline",
            "name": "Timeline",
            "description": "Event timeline",
            "icon": "📅",
            "defaultSize": "large",
            "minSize": {"w": 4, "h": 4},
            "maxSize": {"w": 12, "h": 8},
            "configurable": True
        }
    ]
    
    return widget_library