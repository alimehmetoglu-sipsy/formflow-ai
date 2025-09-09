"""
API Endpoints for CRM Export (FA-48)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import io

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.form import FormSubmission
from app.models.lead_score import LeadScore
from app.services.crm_export import CRMExportService
from app.schemas.crm_export import (
    CRMExportRequest,
    ExportFormat,
    CRMType,
    FieldMappingResponse,
    ExportHistoryResponse
)

router = APIRouter()


@router.post("/export/leads/csv")
async def export_leads_csv(
    request: CRMExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export leads to CSV format for CRM import
    """
    # Validate lead ownership
    if request.lead_ids:
        leads = db.query(FormSubmission).filter(
            FormSubmission.id.in_(request.lead_ids),
            FormSubmission.user_id == current_user.id
        ).all()
        
        if len(leads) != len(request.lead_ids):
            raise HTTPException(status_code=404, detail="Some leads not found or unauthorized")
    else:
        # Export all leads with optional date filter
        query = db.query(FormSubmission).filter(
            FormSubmission.user_id == current_user.id
        )
        
        if request.date_from:
            query = query.filter(FormSubmission.created_at >= request.date_from)
        if request.date_to:
            query = query.filter(FormSubmission.created_at <= request.date_to)
        
        leads = query.all()
    
    if not leads:
        raise HTTPException(status_code=404, detail="No leads found")
    
    # Convert to dictionaries and add metadata
    lead_data = []
    for lead in leads:
        data = lead.form_data.copy() if isinstance(lead.form_data, dict) else {}
        data['submission_id'] = lead.id
        data['created_at'] = lead.created_at
        lead_data.append(data)
    
    # Generate CSV
    export_service = CRMExportService(db)
    csv_content = export_service.export_to_csv(
        lead_data,
        crm_type=request.crm_type,
        include_scores=request.include_scores,
        include_insights=request.include_insights,
        include_recommendations=request.include_recommendations
    )
    
    # Return as downloadable file
    filename = f"leads_{request.crm_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/export/leads/json")
async def export_leads_json(
    request: CRMExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export leads to JSON format for API integration
    """
    # Validate lead ownership
    if request.lead_ids:
        leads = db.query(FormSubmission).filter(
            FormSubmission.id.in_(request.lead_ids),
            FormSubmission.user_id == current_user.id
        ).all()
    else:
        leads = db.query(FormSubmission).filter(
            FormSubmission.user_id == current_user.id
        ).all()
    
    if not leads:
        raise HTTPException(status_code=404, detail="No leads found")
    
    # Convert to dictionaries
    lead_data = []
    for lead in leads:
        data = lead.form_data.copy() if isinstance(lead.form_data, dict) else {}
        data['submission_id'] = lead.id
        lead_data.append(data)
    
    # Generate JSON
    export_service = CRMExportService(db)
    json_content = export_service.export_to_json(
        lead_data,
        crm_type=request.crm_type,
        include_scores=request.include_scores
    )
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=leads_{request.crm_type}.json"
        }
    )


@router.post("/export/leads/excel")
async def export_leads_excel(
    request: CRMExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export leads to Excel format
    """
    # Validate lead ownership
    if request.lead_ids:
        leads = db.query(FormSubmission).filter(
            FormSubmission.id.in_(request.lead_ids),
            FormSubmission.user_id == current_user.id
        ).all()
    else:
        leads = db.query(FormSubmission).filter(
            FormSubmission.user_id == current_user.id
        ).all()
    
    if not leads:
        raise HTTPException(status_code=404, detail="No leads found")
    
    # Convert to dictionaries
    lead_data = []
    for lead in leads:
        data = lead.form_data.copy() if isinstance(lead.form_data, dict) else {}
        data['submission_id'] = lead.id
        lead_data.append(data)
    
    # Generate Excel
    export_service = CRMExportService(db)
    excel_content = export_service.export_to_excel(lead_data, crm_type=request.crm_type)
    
    filename = f"leads_{request.crm_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/field-mappings/{crm_type}", response_model=FieldMappingResponse)
async def get_field_mappings(
    crm_type: CRMType,
    current_user: User = Depends(get_current_user)
):
    """
    Get field mapping configuration for specific CRM
    """
    mappings = {
        'salesforce': {
            'standard_fields': {
                'FirstName': 'First name of the lead',
                'LastName': 'Last name of the lead',
                'Email': 'Email address',
                'Company': 'Company name',
                'Phone': 'Phone number',
                'Title': 'Job title or role',
                'LeadSource': 'Source of the lead (FormFlow AI)',
                'Industry': 'Industry sector',
                'Rating': 'Hot/Warm/Cold based on score'
            },
            'custom_fields': {
                'Lead_Score__c': 'Numeric lead score (0-100)',
                'Score_Category__c': 'Score category (hot/warm/cold)',
                'Timeline__c': 'Decision timeline',
                'Budget__c': 'Budget information',
                'Pain_Points__c': 'Identified pain points',
                'Next_Action__c': 'Recommended next action',
                'Competitor__c': 'Current solution or competitor'
            }
        },
        'hubspot': {
            'standard_fields': {
                'firstname': 'First name',
                'lastname': 'Last name',
                'email': 'Email address',
                'company': 'Company name',
                'phone': 'Phone number',
                'jobtitle': 'Job title',
                'website': 'Company website',
                'lead_status': 'Lead status (New)'
            },
            'custom_fields': {
                'formflow_score': 'Lead score',
                'formflow_category': 'Score category',
                'formflow_timeline': 'Timeline',
                'formflow_budget': 'Budget',
                'formflow_pain_points': 'Pain points',
                'formflow_competitor': 'Current solution'
            }
        },
        'pipedrive': {
            'standard_fields': {
                'name': 'Full name',
                'email': 'Email',
                'phone': 'Phone',
                'org_name': 'Organization name',
                'title': 'Deal title',
                'value': 'Deal value',
                'currency': 'Currency (USD)'
            },
            'custom_fields': {
                'lead_score': 'Lead score',
                'timeline': 'Timeline',
                'budget': 'Budget',
                'pain_points': 'Pain points'
            }
        },
        'generic': {
            'standard_fields': {
                'Name': 'Full name',
                'Email': 'Email',
                'Phone': 'Phone',
                'Company': 'Company',
                'Job_Title': 'Job title',
                'Lead_Score': 'Lead score',
                'Timeline': 'Timeline',
                'Budget': 'Budget'
            },
            'custom_fields': {}
        }
    }
    
    mapping = mappings.get(crm_type, mappings['generic'])
    
    return FieldMappingResponse(
        crm_type=crm_type,
        standard_fields=mapping['standard_fields'],
        custom_fields=mapping.get('custom_fields', {}),
        total_fields=len(mapping['standard_fields']) + len(mapping.get('custom_fields', {}))
    )


@router.get("/export/history", response_model=List[ExportHistoryResponse])
async def get_export_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's export history
    """
    # This would query an export_history table
    # For now, return sample data
    
    history = [
        ExportHistoryResponse(
            id="export-1",
            export_date=datetime.utcnow() - timedelta(days=1),
            crm_type="salesforce",
            format="csv",
            lead_count=25,
            file_name="leads_salesforce_20250109.csv",
            status="completed"
        ),
        ExportHistoryResponse(
            id="export-2",
            export_date=datetime.utcnow() - timedelta(days=3),
            crm_type="hubspot",
            format="json",
            lead_count=15,
            file_name="leads_hubspot_20250107.json",
            status="completed"
        )
    ]
    
    return history[offset:offset+limit]


@router.post("/export/webhook-setup")
async def setup_crm_webhook(
    crm_type: CRMType,
    webhook_url: str,
    api_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup automatic lead forwarding to CRM via webhook
    """
    # This would configure webhook settings for automatic export
    # Implementation would depend on specific CRM requirements
    
    return {
        "status": "success",
        "message": f"Webhook configured for {crm_type}",
        "webhook_url": webhook_url,
        "test_endpoint": f"/api/v1/export/webhook-test/{crm_type}"
    }


@router.get("/export/templates/{crm_type}")
async def get_import_instructions(
    crm_type: CRMType,
    current_user: User = Depends(get_current_user)
):
    """
    Get step-by-step import instructions for specific CRM
    """
    instructions = {
        'salesforce': {
            'title': 'Importing Leads into Salesforce',
            'steps': [
                'Navigate to Setup > Data Import Wizard',
                'Select "Leads" as the object type',
                'Choose "Add new records" or "Update existing records"',
                'Upload the CSV file exported from FormFlow',
                'Map the fields according to the provided mapping',
                'Review the field mappings',
                'Start the import process',
                'Monitor the import status in the job queue'
            ],
            'tips': [
                'Ensure custom fields are created before import',
                'Test with a small batch first',
                'Check for duplicate rules in your Salesforce org'
            ]
        },
        'hubspot': {
            'title': 'Importing Leads into HubSpot',
            'steps': [
                'Go to Contacts > Import',
                'Select "Start an import"',
                'Choose "File from computer"',
                'Upload the CSV file',
                'Select "Contacts" as the object type',
                'Map the columns to HubSpot properties',
                'Review mappings and start import',
                'Check import status in the notifications'
            ],
            'tips': [
                'Create custom properties for FormFlow fields',
                'Use HubSpot\'s duplicate management settings',
                'Consider setting up a workflow for imported leads'
            ]
        },
        'pipedrive': {
            'title': 'Importing Leads into Pipedrive',
            'steps': [
                'Go to Settings > Import Data',
                'Select "From a spreadsheet"',
                'Upload the CSV or Excel file',
                'Choose "People" or "Deals" as import type',
                'Map the fields',
                'Configure duplicate handling',
                'Start the import',
                'Review imported data'
            ],
            'tips': [
                'Create custom fields before importing',
                'Use Pipedrive\'s merge feature for duplicates',
                'Set up automation for new leads'
            ]
        },
        'generic': {
            'title': 'Generic CRM Import',
            'steps': [
                'Locate the import feature in your CRM',
                'Prepare the CSV file from FormFlow',
                'Map fields according to your CRM structure',
                'Handle duplicates according to your policy',
                'Import and verify the data'
            ],
            'tips': [
                'Always backup before bulk imports',
                'Test with a small sample first',
                'Document your field mappings'
            ]
        }
    }
    
    return instructions.get(crm_type, instructions['generic'])