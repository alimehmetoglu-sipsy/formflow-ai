"""
API Endpoints for Multi-Form Dashboard Operations (FA-44)
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.multi_form_dashboard import (
    MultiFormDashboard,
    MultiFormMapping,
    CustomMetric,
    ScheduledReport
)
from app.services.aggregation_engine import AggregationEngine
from app.schemas.multi_form import (
    MultiFormDashboardCreate,
    MultiFormDashboardUpdate,
    MultiFormDashboardResponse,
    MultiFormMappingCreate,
    CustomMetricCreate,
    ScheduledReportCreate,
    AggregationResultResponse
)
from app.core.logging import logger

router = APIRouter()


@router.post("/multi-dashboards", response_model=MultiFormDashboardResponse)
async def create_multi_form_dashboard(
    dashboard_data: MultiFormDashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MultiFormDashboardResponse:
    """
    Create a new multi-form dashboard
    """
    # Check user plan limits
    existing_count = db.query(MultiFormDashboard).filter_by(
        user_id=current_user.id
    ).count()
    
    if current_user.plan_type == "free" and existing_count >= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free plan users can only create 1 multi-form dashboard. Please upgrade to Pro or Business plan."
        )
    
    # Create dashboard
    dashboard = MultiFormDashboard(
        user_id=current_user.id,
        name=dashboard_data.name,
        description=dashboard_data.description,
        aggregation_config=dashboard_data.aggregation_config,
        analytics_config=dashboard_data.analytics_config,
        filter_config=dashboard_data.filter_config,
        is_public=dashboard_data.is_public
    )
    
    # Generate share token if public
    if dashboard.is_public:
        import secrets
        dashboard.share_token = secrets.token_urlsafe(32)
    
    db.add(dashboard)
    
    # Add form mappings
    for mapping_data in dashboard_data.form_mappings:
        mapping = MultiFormMapping(
            dashboard_id=dashboard.id,
            form_type=mapping_data.form_type,
            form_external_id=mapping_data.form_external_id,
            form_title=mapping_data.form_title,
            field_mappings=mapping_data.field_mappings,
            weight=mapping_data.weight,
            priority=mapping_data.priority
        )
        db.add(mapping)
    
    db.commit()
    db.refresh(dashboard)
    
    logger.info(f"Created multi-form dashboard {dashboard.id} for user {current_user.id}")
    
    return MultiFormDashboardResponse.from_orm(dashboard)


@router.get("/multi-dashboards", response_model=List[MultiFormDashboardResponse])
async def list_multi_form_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MultiFormDashboardResponse]:
    """
    List user's multi-form dashboards
    """
    dashboards = db.query(MultiFormDashboard).filter_by(
        user_id=current_user.id
    ).offset(skip).limit(limit).all()
    
    return [MultiFormDashboardResponse.from_orm(d) for d in dashboards]


@router.get("/multi-dashboards/{dashboard_id}", response_model=MultiFormDashboardResponse)
async def get_multi_form_dashboard(
    dashboard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MultiFormDashboardResponse:
    """
    Get a specific multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Update last accessed timestamp
    dashboard.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return MultiFormDashboardResponse.from_orm(dashboard)


@router.put("/multi-dashboards/{dashboard_id}", response_model=MultiFormDashboardResponse)
async def update_multi_form_dashboard(
    dashboard_id: UUID,
    dashboard_update: MultiFormDashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MultiFormDashboardResponse:
    """
    Update a multi-form dashboard configuration
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Update fields
    update_data = dashboard_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)
    
    dashboard.updated_at = datetime.utcnow()
    
    # Clear cache on configuration change
    dashboard.cached_data = None
    dashboard.cache_updated_at = None
    
    db.commit()
    db.refresh(dashboard)
    
    logger.info(f"Updated multi-form dashboard {dashboard_id}")
    
    return MultiFormDashboardResponse.from_orm(dashboard)


@router.delete("/multi-dashboards/{dashboard_id}")
async def delete_multi_form_dashboard(
    dashboard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    db.delete(dashboard)
    db.commit()
    
    logger.info(f"Deleted multi-form dashboard {dashboard_id}")
    
    return {"message": "Dashboard deleted successfully"}


@router.post("/multi-dashboards/{dashboard_id}/aggregate", response_model=AggregationResultResponse)
async def aggregate_dashboard_data(
    dashboard_id: UUID,
    force_refresh: bool = Query(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AggregationResultResponse:
    """
    Trigger data aggregation for a multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check if aggregation is already in progress
    from app.models.multi_form_dashboard import AggregationJob
    active_job = db.query(AggregationJob).filter_by(
        dashboard_id=dashboard_id,
        status="processing"
    ).first()
    
    if active_job:
        return AggregationResultResponse(
            status="processing",
            message="Aggregation already in progress",
            job_id=str(active_job.id)
        )
    
    # Run aggregation
    engine = AggregationEngine(db)
    
    try:
        result = await engine.aggregate_dashboard_data(
            dashboard_id=dashboard_id,
            force_refresh=force_refresh
        )
        
        return AggregationResultResponse(
            status="completed",
            data=result.get("data", []),
            metrics=result.get("metrics", {}),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Aggregation failed for dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aggregation failed: {str(e)}"
        )


@router.post("/multi-dashboards/{dashboard_id}/mappings", response_model=Dict[str, str])
async def add_form_mapping(
    dashboard_id: UUID,
    mapping_data: MultiFormMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Add a new form mapping to a multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check mapping limit for free users
    existing_mappings = db.query(MultiFormMapping).filter_by(
        dashboard_id=dashboard_id
    ).count()
    
    if current_user.plan_type == "free" and existing_mappings >= 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free plan users can only add up to 3 form mappings. Please upgrade to Pro or Business plan."
        )
    
    # Create mapping
    mapping = MultiFormMapping(
        dashboard_id=dashboard_id,
        form_type=mapping_data.form_type,
        form_external_id=mapping_data.form_external_id,
        form_title=mapping_data.form_title,
        field_mappings=mapping_data.field_mappings,
        weight=mapping_data.weight,
        priority=mapping_data.priority
    )
    
    db.add(mapping)
    
    # Clear dashboard cache
    dashboard.cached_data = None
    dashboard.cache_updated_at = None
    
    db.commit()
    
    logger.info(f"Added form mapping to dashboard {dashboard_id}")
    
    return {"message": "Form mapping added successfully", "mapping_id": str(mapping.id)}


@router.delete("/multi-dashboards/{dashboard_id}/mappings/{mapping_id}")
async def remove_form_mapping(
    dashboard_id: UUID,
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Remove a form mapping from a multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    mapping = db.query(MultiFormMapping).filter_by(
        id=mapping_id,
        dashboard_id=dashboard_id
    ).first()
    
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found"
        )
    
    db.delete(mapping)
    
    # Clear dashboard cache
    dashboard.cached_data = None
    dashboard.cache_updated_at = None
    
    db.commit()
    
    logger.info(f"Removed form mapping {mapping_id} from dashboard {dashboard_id}")
    
    return {"message": "Form mapping removed successfully"}


@router.post("/multi-dashboards/{dashboard_id}/metrics", response_model=Dict[str, str])
async def create_custom_metric(
    dashboard_id: UUID,
    metric_data: CustomMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Create a custom metric for a multi-form dashboard
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check metric limit for free users
    existing_metrics = db.query(CustomMetric).filter_by(
        dashboard_id=dashboard_id
    ).count()
    
    if current_user.plan_type == "free" and existing_metrics >= 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free plan users can only create up to 5 custom metrics. Please upgrade to Pro or Business plan."
        )
    
    # Create metric
    metric = CustomMetric(
        dashboard_id=dashboard_id,
        name=metric_data.name,
        display_name=metric_data.display_name,
        description=metric_data.description,
        metric_type=metric_data.metric_type,
        formula=metric_data.formula,
        unit=metric_data.unit,
        visualization_type=metric_data.visualization_type,
        visualization_config=metric_data.visualization_config,
        is_kpi=metric_data.is_kpi,
        target_value=metric_data.target_value,
        threshold_warning=metric_data.threshold_warning,
        threshold_critical=metric_data.threshold_critical,
        enable_alerts=metric_data.enable_alerts,
        alert_config=metric_data.alert_config
    )
    
    db.add(metric)
    db.commit()
    
    logger.info(f"Created custom metric for dashboard {dashboard_id}")
    
    return {"message": "Custom metric created successfully", "metric_id": str(metric.id)}


@router.post("/multi-dashboards/{dashboard_id}/reports", response_model=Dict[str, str])
async def create_scheduled_report(
    dashboard_id: UUID,
    report_data: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Create a scheduled report for a multi-form dashboard
    """
    # Check if user has Business plan
    if current_user.plan_type not in ["business", "custom"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scheduled reports are only available for Business plan users."
        )
    
    dashboard = db.query(MultiFormDashboard).filter_by(
        id=dashboard_id,
        user_id=current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Create scheduled report
    report = ScheduledReport(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
        name=report_data.name,
        description=report_data.description,
        schedule_type=report_data.schedule_type,
        schedule_config=report_data.schedule_config,
        report_format=report_data.report_format,
        include_sections=report_data.include_sections,
        filter_override=report_data.filter_override,
        recipients=report_data.recipients,
        email_subject=report_data.email_subject,
        email_body_template=report_data.email_body_template,
        is_active=report_data.is_active
    )
    
    # Calculate next run time
    from app.services.report_scheduler import calculate_next_run
    report.next_run_at = calculate_next_run(
        report.schedule_type,
        report.schedule_config
    )
    
    db.add(report)
    db.commit()
    
    logger.info(f"Created scheduled report for dashboard {dashboard_id}")
    
    return {"message": "Scheduled report created successfully", "report_id": str(report.id)}


@router.get("/multi-dashboards/public/{share_token}", response_model=AggregationResultResponse)
async def get_public_multi_dashboard(
    share_token: str,
    db: Session = Depends(get_db)
) -> AggregationResultResponse:
    """
    Get public multi-form dashboard by share token
    """
    dashboard = db.query(MultiFormDashboard).filter_by(
        share_token=share_token,
        is_public=True
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found or not public"
        )
    
    # Update last accessed timestamp
    dashboard.last_accessed_at = datetime.utcnow()
    db.commit()
    
    # Return cached data or aggregate
    if dashboard.cached_data:
        return AggregationResultResponse(
            status="completed",
            data=dashboard.cached_data.get("data", []),
            metrics=dashboard.cached_data.get("metrics", {}),
            metadata=dashboard.cached_data.get("metadata", {})
        )
    
    # Trigger aggregation if no cache
    engine = AggregationEngine(db)
    
    try:
        result = await engine.aggregate_dashboard_data(
            dashboard_id=dashboard.id,
            force_refresh=False
        )
        
        return AggregationResultResponse(
            status="completed",
            data=result.get("data", []),
            metrics=result.get("metrics", {}),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Failed to get public dashboard {share_token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data"
        )