"""
Template Selection Service for FA-46
Automatically selects the appropriate dashboard template based on form data
"""

from typing import Dict, List, Optional
import re
import json

class TemplateSelector:
    """Service for selecting dashboard templates based on form content"""
    
    def __init__(self):
        # Define template criteria
        self.template_criteria = {
            'sales_lead': {
                'keywords': ['budget', 'company', 'timeline', 'solution', 'purchase', 
                            'decision', 'pricing', 'cost', 'investment', 'roi', 'demo',
                            'competitor', 'evaluation', 'vendor', 'proposal'],
                'required_fields': ['email', 'company'],
                'min_keyword_matches': 3,
                'priority': 1
            },
            'health_assessment': {
                'keywords': ['health', 'wellness', 'symptoms', 'medical', 'diagnosis',
                            'treatment', 'medication', 'condition', 'pain', 'therapy',
                            'exercise', 'nutrition', 'mental', 'physical'],
                'required_fields': [],
                'min_keyword_matches': 3,
                'priority': 2
            },
            'event_registration': {
                'keywords': ['event', 'registration', 'attend', 'conference', 'workshop',
                            'seminar', 'webinar', 'session', 'ticket', 'venue', 'date',
                            'schedule', 'speaker', 'agenda'],
                'required_fields': ['name', 'email'],
                'min_keyword_matches': 3,
                'priority': 3
            },
            'survey_feedback': {
                'keywords': ['satisfaction', 'feedback', 'rating', 'experience', 'opinion',
                            'improve', 'recommend', 'service', 'quality', 'suggestion'],
                'required_fields': [],
                'min_keyword_matches': 2,
                'priority': 4
            },
            'generic': {
                'keywords': [],
                'required_fields': [],
                'min_keyword_matches': 0,
                'priority': 99
            }
        }
        
        # Sales-specific field patterns
        self.sales_patterns = {
            'budget': [
                r'\$[\d,]+',
                r'\d+k\b',
                r'\d+K\b',
                r'\d+m\b',
                r'\d+M\b',
                r'budget.*\d+',
                r'invest.*\d+',
                r'spend.*\d+'
            ],
            'timeline': [
                r'q[1-4]\s*202\d',
                r'quarter',
                r'immediate',
                r'asap',
                r'urgent',
                r'this\s+(month|week|year)',
                r'next\s+(month|week|year)',
                r'\d+\s*(days?|weeks?|months?)'
            ],
            'company_size': [
                r'\d+\s*employees?',
                r'\d+\s*people',
                r'enterprise',
                r'startup',
                r'small\s*business',
                r'mid-?market',
                r'fortune\s*\d+'
            ],
            'decision_authority': [
                r'\b(ceo|cto|cfo|coo|vp|director|manager|head\s+of)\b',
                r'decision\s*maker',
                r'budget\s*authority',
                r'final\s*approval'
            ]
        }
    
    def select_template(self, form_data: Dict) -> Dict:
        """
        Select the most appropriate template based on form data
        
        Returns:
            Dict with template name and confidence score
        """
        # Convert form data to searchable text
        form_text = json.dumps(form_data).lower()
        
        # Track scores for each template
        template_scores = {}
        
        for template_name, criteria in self.template_criteria.items():
            if template_name == 'generic':
                continue
                
            score = 0
            
            # Check keyword matches
            keyword_matches = sum(
                1 for keyword in criteria['keywords'] 
                if keyword in form_text
            )
            
            # Check required fields
            has_required_fields = all(
                field in form_data 
                for field in criteria['required_fields']
            )
            
            if not has_required_fields:
                continue
            
            # Calculate score
            if keyword_matches >= criteria['min_keyword_matches']:
                score = keyword_matches * 10
                
                # Bonus for priority templates
                score += (10 - criteria['priority']) * 5
                
                # Additional scoring for sales template
                if template_name == 'sales_lead':
                    score += self._calculate_sales_score(form_data, form_text)
                
                template_scores[template_name] = score
        
        # Select template with highest score
        if template_scores:
            best_template = max(template_scores.items(), key=lambda x: x[1])
            confidence = min(100, (best_template[1] / 100) * 100)
            
            return {
                'template': best_template[0],
                'confidence': confidence,
                'score': best_template[1],
                'is_sales': best_template[0] == 'sales_lead'
            }
        
        # Default to generic template
        return {
            'template': 'generic',
            'confidence': 100,
            'score': 0,
            'is_sales': False
        }
    
    def _calculate_sales_score(self, form_data: Dict, form_text: str) -> int:
        """Calculate additional score for sales-specific patterns"""
        bonus_score = 0
        
        # Check for budget patterns
        for pattern in self.sales_patterns['budget']:
            if re.search(pattern, form_text, re.IGNORECASE):
                bonus_score += 10
                break
        
        # Check for timeline patterns
        for pattern in self.sales_patterns['timeline']:
            if re.search(pattern, form_text, re.IGNORECASE):
                bonus_score += 8
                break
        
        # Check for company size patterns
        for pattern in self.sales_patterns['company_size']:
            if re.search(pattern, form_text, re.IGNORECASE):
                bonus_score += 5
                break
        
        # Check for decision authority patterns
        for pattern in self.sales_patterns['decision_authority']:
            if re.search(pattern, form_text, re.IGNORECASE):
                bonus_score += 7
                break
        
        # Check for competitor mentions
        competitors = ['salesforce', 'hubspot', 'pipedrive', 'excel', 'manual', 'spreadsheet']
        if any(comp in form_text for comp in competitors):
            bonus_score += 10
        
        # Check for specific sales fields
        sales_fields = ['budget', 'timeline', 'company_size', 'current_solution', 'pain_points']
        fields_present = sum(1 for field in sales_fields if field in form_data)
        bonus_score += fields_present * 3
        
        return bonus_score
    
    def extract_sales_insights(self, form_data: Dict) -> Dict:
        """Extract sales-specific insights from form data"""
        insights = {
            'budget': None,
            'timeline': None,
            'company_size': None,
            'decision_authority': None,
            'pain_points': [],
            'current_solution': None,
            'competitors_mentioned': []
        }
        
        form_text = json.dumps(form_data)
        
        # Extract budget
        budget_match = re.search(r'\$?([\d,]+)(?:k|K|m|M)?', form_text)
        if budget_match:
            insights['budget'] = budget_match.group(0)
        
        # Extract timeline
        timeline_patterns = [
            r'(immediate|asap|urgent)',
            r'(q[1-4]\s*202\d)',
            r'(this|next)\s+(week|month|quarter|year)',
            r'(\d+)\s*(days?|weeks?|months?)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, form_text, re.IGNORECASE)
            if match:
                insights['timeline'] = match.group(0)
                break
        
        # Extract company size
        size_match = re.search(r'(\d+)\s*employees?', form_text, re.IGNORECASE)
        if size_match:
            insights['company_size'] = size_match.group(0)
        
        # Extract decision authority
        authority_match = re.search(
            r'(ceo|cto|cfo|coo|vp|director|manager|head\s+of)',
            form_text,
            re.IGNORECASE
        )
        if authority_match:
            insights['decision_authority'] = authority_match.group(0)
        
        # Extract pain points
        pain_keywords = ['problem', 'challenge', 'issue', 'struggle', 'difficult', 'frustrat']
        for field_name, field_value in form_data.items():
            if isinstance(field_value, str):
                for keyword in pain_keywords:
                    if keyword in field_value.lower():
                        insights['pain_points'].append(field_value)
                        break
        
        # Extract current solution
        if 'current_solution' in form_data:
            insights['current_solution'] = form_data['current_solution']
        elif 'current' in form_text.lower():
            # Try to extract from context
            current_match = re.search(
                r'current[ly]*\s+(?:using|have|working with)\s+(\w+)',
                form_text,
                re.IGNORECASE
            )
            if current_match:
                insights['current_solution'] = current_match.group(1)
        
        # Extract competitors
        competitors = ['salesforce', 'hubspot', 'pipedrive', 'excel', 'manual', 
                      'spreadsheet', 'custom', 'in-house']
        for comp in competitors:
            if comp in form_text.lower():
                insights['competitors_mentioned'].append(comp)
        
        return insights