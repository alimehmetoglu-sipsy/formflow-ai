"""
CRM Export Service for FA-48
Service for exporting lead data to various CRM formats
"""

import csv
import json
import io
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID
import pandas as pd

from app.models.form import FormSubmission
from app.models.lead_score import LeadScore


class CRMExportService:
    """Service for exporting lead data to CRM systems"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # CRM field mappings
        self.field_mappings = {
            'salesforce': {
                'FirstName': lambda d: self._extract_first_name(d),
                'LastName': lambda d: self._extract_last_name(d),
                'Email': lambda d: d.get('email', ''),
                'Company': lambda d: d.get('company', d.get('company_name', '')),
                'Phone': lambda d: d.get('phone', d.get('phone_number', '')),
                'Title': lambda d: d.get('role', d.get('job_title', d.get('title', ''))),
                'LeadSource': lambda d: 'FormFlow AI',
                'Industry': lambda d: d.get('industry', ''),
                'NumberOfEmployees': lambda d: self._extract_employee_count(d),
                'AnnualRevenue': lambda d: self._extract_revenue(d),
                'Rating': lambda d, s: self._get_rating(s),
                'Description': lambda d, i: i.get('ai_summary', ''),
                'Website': lambda d: d.get('website', d.get('company_website', '')),
                'Status': lambda d: 'New',
                'Custom_Lead_Score__c': lambda d, s: s.final_score if s else 0,
                'Custom_Score_Category__c': lambda d, s: s.score_category if s else 'unknown',
                'Custom_Timeline__c': lambda d: d.get('timeline', ''),
                'Custom_Budget__c': lambda d: d.get('budget', ''),
                'Custom_Pain_Points__c': lambda d: self._format_list(d.get('pain_points', [])),
                'Custom_Next_Action__c': lambda d, r: r[0]['action'] if r else '',
                'Custom_Competitor__c': lambda d: d.get('current_solution', ''),
                'Custom_Decision_Maker__c': lambda d: 'Yes' if self._is_decision_maker(d) else 'No'
            },
            
            'hubspot': {
                'firstname': lambda d: self._extract_first_name(d),
                'lastname': lambda d: self._extract_last_name(d),
                'email': lambda d: d.get('email', ''),
                'company': lambda d: d.get('company', d.get('company_name', '')),
                'phone': lambda d: d.get('phone', d.get('phone_number', '')),
                'jobtitle': lambda d: d.get('role', d.get('job_title', d.get('title', ''))),
                'website': lambda d: d.get('website', d.get('company_website', '')),
                'numemployees': lambda d: self._extract_employee_count(d),
                'annualrevenue': lambda d: self._extract_revenue(d),
                'industry': lambda d: d.get('industry', ''),
                'lead_status': lambda d: 'New',
                'lifecyclestage': lambda d: 'lead',
                'hs_lead_status': lambda d: 'NEW',
                'formflow_score': lambda d, s: s.final_score if s else 0,
                'formflow_category': lambda d, s: s.score_category if s else 'unknown',
                'formflow_timeline': lambda d: d.get('timeline', ''),
                'formflow_budget': lambda d: d.get('budget', ''),
                'formflow_pain_points': lambda d: self._format_list(d.get('pain_points', [])),
                'formflow_next_action': lambda d, r: r[0]['action'] if r else '',
                'formflow_competitor': lambda d: d.get('current_solution', ''),
                'formflow_insights': lambda d, i: json.dumps(i) if i else ''
            },
            
            'pipedrive': {
                'name': lambda d: d.get('name', d.get('full_name', '')),
                'email': lambda d: d.get('email', ''),
                'phone': lambda d: d.get('phone', d.get('phone_number', '')),
                'org_name': lambda d: d.get('company', d.get('company_name', '')),
                'title': lambda d: f"Lead from {d.get('company', 'FormFlow')}",
                'value': lambda d: self._extract_deal_value(d),
                'currency': lambda d: 'USD',
                'status': lambda d: 'open',
                'visible_to': lambda d: '3',  # Everyone in company
                'add_time': lambda d: datetime.utcnow().isoformat(),
                'custom_fields': {
                    'lead_score': lambda d, s: s.final_score if s else 0,
                    'score_category': lambda d, s: s.score_category if s else 'unknown',
                    'timeline': lambda d: d.get('timeline', ''),
                    'budget': lambda d: d.get('budget', ''),
                    'pain_points': lambda d: self._format_list(d.get('pain_points', [])),
                    'competitor': lambda d: d.get('current_solution', ''),
                    'job_title': lambda d: d.get('role', d.get('job_title', '')),
                    'company_size': lambda d: self._extract_employee_count(d)
                }
            },
            
            'generic': {
                'Name': lambda d: d.get('name', d.get('full_name', '')),
                'Email': lambda d: d.get('email', ''),
                'Phone': lambda d: d.get('phone', d.get('phone_number', '')),
                'Company': lambda d: d.get('company', d.get('company_name', '')),
                'Job_Title': lambda d: d.get('role', d.get('job_title', d.get('title', ''))),
                'Website': lambda d: d.get('website', d.get('company_website', '')),
                'Industry': lambda d: d.get('industry', ''),
                'Company_Size': lambda d: self._extract_employee_count(d),
                'Annual_Revenue': lambda d: self._extract_revenue(d),
                'Lead_Score': lambda d, s: s.final_score if s else 0,
                'Score_Category': lambda d, s: s.score_category if s else 'unknown',
                'Timeline': lambda d: d.get('timeline', ''),
                'Budget': lambda d: d.get('budget', ''),
                'Pain_Points': lambda d: self._format_list(d.get('pain_points', [])),
                'Current_Solution': lambda d: d.get('current_solution', ''),
                'Decision_Maker': lambda d: 'Yes' if self._is_decision_maker(d) else 'No',
                'Source': lambda d: 'FormFlow AI',
                'Created_Date': lambda d: datetime.utcnow().strftime('%Y-%m-%d'),
                'Notes': lambda d: self._generate_notes(d)
            }
        }
    
    def export_to_csv(
        self,
        leads: List[Dict],
        crm_type: str = 'generic',
        include_scores: bool = True,
        include_insights: bool = True,
        include_recommendations: bool = False
    ) -> str:
        """
        Export leads to CSV format for specific CRM
        
        Args:
            leads: List of lead data dictionaries
            crm_type: Type of CRM (salesforce, hubspot, pipedrive, generic)
            include_scores: Include lead scoring data
            include_insights: Include AI insights
            include_recommendations: Include follow-up recommendations
            
        Returns:
            CSV string content
        """
        if crm_type not in self.field_mappings:
            crm_type = 'generic'
        
        mapping = self.field_mappings[crm_type]
        csv_data = []
        
        for lead in leads:
            # Get lead score if available
            lead_score = None
            if include_scores and 'submission_id' in lead:
                lead_score = self.db.query(LeadScore).filter(
                    LeadScore.submission_id == lead['submission_id']
                ).first()
            
            # Get insights and recommendations (would come from services)
            insights = lead.get('insights', {}) if include_insights else {}
            recommendations = lead.get('recommendations', []) if include_recommendations else []
            
            # Map fields according to CRM format
            row = {}
            for crm_field, extractor in mapping.items():
                if crm_field == 'custom_fields' and isinstance(extractor, dict):
                    # Handle Pipedrive custom fields
                    for custom_field, custom_extractor in extractor.items():
                        row[f'custom_{custom_field}'] = self._safe_extract(
                            custom_extractor, lead, lead_score, insights, recommendations
                        )
                else:
                    row[crm_field] = self._safe_extract(
                        extractor, lead, lead_score, insights, recommendations
                    )
            
            csv_data.append(row)
        
        # Generate CSV
        return self._generate_csv(csv_data)
    
    def export_to_json(
        self,
        leads: List[Dict],
        crm_type: str = 'generic',
        include_scores: bool = True
    ) -> str:
        """Export leads to JSON format for API integration"""
        if crm_type not in self.field_mappings:
            crm_type = 'generic'
        
        mapping = self.field_mappings[crm_type]
        json_data = []
        
        for lead in leads:
            # Get lead score if available
            lead_score = None
            if include_scores and 'submission_id' in lead:
                lead_score = self.db.query(LeadScore).filter(
                    LeadScore.submission_id == lead['submission_id']
                ).first()
            
            # Map fields
            record = {}
            for crm_field, extractor in mapping.items():
                if crm_field != 'custom_fields':
                    record[crm_field] = self._safe_extract(
                        extractor, lead, lead_score, {}, []
                    )
            
            json_data.append(record)
        
        return json.dumps(json_data, indent=2, default=str)
    
    def export_to_excel(
        self,
        leads: List[Dict],
        crm_type: str = 'generic'
    ) -> bytes:
        """Export leads to Excel format"""
        # First get CSV data
        csv_content = self.export_to_csv(leads, crm_type)
        
        # Convert to DataFrame
        csv_buffer = io.StringIO(csv_content)
        df = pd.read_csv(csv_buffer)
        
        # Write to Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads', index=False)
            
            # Add metadata sheet
            metadata = pd.DataFrame({
                'Field': ['Export Date', 'CRM Type', 'Total Leads', 'Source'],
                'Value': [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 
                         crm_type.upper(), len(leads), 'FormFlow AI']
            })
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.read()
    
    def _safe_extract(self, extractor, lead_data, lead_score=None, insights=None, recommendations=None):
        """Safely extract value using extractor function"""
        try:
            # Check how many parameters the extractor accepts
            import inspect
            sig = inspect.signature(extractor)
            param_count = len(sig.parameters)
            
            if param_count == 1:
                return extractor(lead_data)
            elif param_count == 2:
                # Could be score, insights, or recommendations
                if 'score' in str(sig):
                    return extractor(lead_data, lead_score)
                elif 'insights' in str(sig) or 'i' in str(sig):
                    return extractor(lead_data, insights)
                else:
                    return extractor(lead_data, recommendations)
            else:
                return extractor(lead_data)
        except:
            return ''
    
    def _extract_first_name(self, data: Dict) -> str:
        """Extract first name from full name"""
        name = data.get('name', data.get('full_name', ''))
        if name:
            parts = name.split()
            return parts[0] if parts else ''
        return ''
    
    def _extract_last_name(self, data: Dict) -> str:
        """Extract last name from full name"""
        name = data.get('name', data.get('full_name', ''))
        if name:
            parts = name.split()
            return parts[-1] if len(parts) > 1 else ''
        return ''
    
    def _extract_employee_count(self, data: Dict) -> str:
        """Extract employee count from various formats"""
        for field in ['employees', 'company_size', 'team_size', 'employee_count']:
            if field in data:
                value = str(data[field])
                # Extract number from strings like "50-100" or "100+"
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    return numbers[0]
        return ''
    
    def _extract_revenue(self, data: Dict) -> str:
        """Extract annual revenue from various formats"""
        for field in ['revenue', 'annual_revenue', 'company_revenue']:
            if field in data:
                return str(data[field])
        return ''
    
    def _extract_deal_value(self, data: Dict) -> float:
        """Extract potential deal value from budget"""
        budget = data.get('budget', '')
        if budget:
            import re
            # Extract numbers from budget string
            numbers = re.findall(r'[\d,]+', budget.replace('$', '').replace('k', '000'))
            if numbers:
                return float(numbers[0].replace(',', ''))
        return 0
    
    def _get_rating(self, lead_score) -> str:
        """Get Salesforce rating based on score"""
        if not lead_score:
            return 'Cold'
        if lead_score.final_score >= 80:
            return 'Hot'
        elif lead_score.final_score >= 60:
            return 'Warm'
        return 'Cold'
    
    def _is_decision_maker(self, data: Dict) -> bool:
        """Check if lead is a decision maker"""
        role = str(data.get('role', data.get('job_title', ''))).lower()
        decision_keywords = ['ceo', 'cto', 'cfo', 'director', 'manager', 'vp', 'president', 'owner', 'founder']
        return any(keyword in role for keyword in decision_keywords)
    
    def _format_list(self, items: List) -> str:
        """Format list as comma-separated string"""
        if isinstance(items, list):
            return ', '.join(str(item) for item in items)
        return str(items)
    
    def _generate_notes(self, data: Dict) -> str:
        """Generate notes field with key information"""
        notes = []
        
        if 'pain_points' in data:
            notes.append(f"Pain Points: {self._format_list(data['pain_points'])}")
        
        if 'current_solution' in data:
            notes.append(f"Current Solution: {data['current_solution']}")
        
        if 'timeline' in data:
            notes.append(f"Timeline: {data['timeline']}")
        
        if 'budget' in data:
            notes.append(f"Budget: {data['budget']}")
        
        return ' | '.join(notes)
    
    def _generate_csv(self, data: List[Dict]) -> str:
        """Generate CSV string from data"""
        if not data:
            return ''
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()