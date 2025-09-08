from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.form import Dashboard, FormSubmission
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.api.v1.auth import get_current_user
from typing import List, Optional

router = APIRouter()

@router.get("/view/{token}", response_class=HTMLResponse)
async def get_dashboard(token: str, db: Session = Depends(get_db)):
    """Get dashboard HTML by submission token"""
    
    # Find submission by token
    submission = db.query(FormSubmission).filter_by(response_id=token).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check if dashboard is ready
    if not submission.processed:
        # Return a processing page
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Processing Your Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <meta http-equiv="refresh" content="5">
        </head>
        <body class="bg-gray-50 flex items-center justify-center min-h-screen">
            <div class="text-center">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
                <h1 class="text-2xl font-bold text-gray-800 mb-2">Creating Your Dashboard</h1>
                <p class="text-gray-600">Our AI is analyzing your form responses...</p>
                <p class="text-sm text-gray-500 mt-4">This page will refresh automatically</p>
            </div>
        </body>
        </html>
        """, status_code=200)
    
    # Get dashboard
    dashboard = db.query(Dashboard).filter_by(submission_id=submission.id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard generation failed"
        )
    
    # Increment view count
    dashboard.view_count += 1
    db.commit()
    
    return HTMLResponse(content=dashboard.html_content)

@router.get("/{submission_id}", response_model=DashboardResponse)
async def get_dashboard_data(submission_id: str, db: Session = Depends(get_db)):
    """Get dashboard data (JSON) by submission ID"""
    
    submission = db.query(FormSubmission).filter_by(id=submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    dashboard = db.query(Dashboard).filter_by(submission_id=submission_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    return DashboardResponse(
        id=dashboard.id,
        submission_id=dashboard.submission_id,
        template_type=dashboard.template_type,
        ai_generated_content=dashboard.ai_generated_content,
        view_count=dashboard.view_count,
        created_at=dashboard.created_at,
        dashboard_url=submission.dashboard_url
    )

@router.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all dashboards with pagination"""
    
    dashboards = db.query(Dashboard).offset(skip).limit(limit).all()
    
    result = []
    for dashboard in dashboards:
        submission = db.query(FormSubmission).filter_by(id=dashboard.submission_id).first()
        if submission:
            result.append(DashboardResponse(
                id=dashboard.id,
                submission_id=dashboard.submission_id,
                template_type=dashboard.template_type,
                ai_generated_content=dashboard.ai_generated_content,
                view_count=dashboard.view_count,
                created_at=dashboard.created_at,
                dashboard_url=submission.dashboard_url
            ))
    
    return result

@router.get("/user/me", response_model=List[DashboardResponse])
async def list_user_dashboards(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List dashboards for current authenticated user"""
    
    # Get all submissions for this user
    submissions = db.query(FormSubmission).filter_by(user_id=current_user.id).offset(skip).limit(limit).all()
    
    result = []
    for submission in submissions:
        dashboard = db.query(Dashboard).filter_by(submission_id=submission.id).first()
        if dashboard:
            result.append(DashboardResponse(
                id=dashboard.id,
                submission_id=dashboard.submission_id,
                template_type=dashboard.template_type,
                ai_generated_content=dashboard.ai_generated_content,
                view_count=dashboard.view_count,
                created_at=dashboard.created_at,
                dashboard_url=submission.dashboard_url,
                token=submission.response_id  # Add token for frontend
            ))
    
    return result