"""
Follow-up Recommendations Engine for FA-47
AI-powered engine for generating personalized follow-up recommendations
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID
import openai

from app.models.lead_score import LeadScore
from app.models.form import FormSubmission
from app.core.config import settings


class FollowUpRecommendationEngine:
    """Engine for generating AI-powered follow-up recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        
        # Follow-up method preferences by score
        self.method_by_score = {
            'hot': ['call', 'demo', 'meeting'],
            'warm': ['email', 'call', 'linkedin'],
            'cold': ['email', 'linkedin', 'nurture']
        }
        
        # Timing recommendations by urgency
        self.timing_by_urgency = {
            'immediate': 'Within 1 hour',
            'urgent': 'Within 24 hours',
            'high': 'Within 48 hours',
            'medium': 'This week',
            'low': 'Next 2 weeks'
        }
        
        # Email templates
        self.email_templates = {
            'hot_lead': """Subject: Quick question about your {pain_point} challenge

Hi {name},

I saw your form submission about {pain_point}. With your {timeline} timeline, I wanted to reach out immediately.

Based on what you shared, FormFlow AI can help you:
• {benefit_1}
• {benefit_2}
• {benefit_3}

Given your budget range of {budget}, we have a solution that fits perfectly.

Are you available for a quick 15-minute call {call_time} to discuss how we can solve this before {deadline}?

Best regards,
{sales_rep_name}""",
            
            'warm_lead': """Subject: Solving {pain_point} for {company}

Hi {name},

Thank you for your interest in FormFlow AI. I noticed you're currently using {current_solution} and looking to improve {improvement_area}.

Companies like yours typically see:
• 80% reduction in manual analysis time
• 50% increase in lead conversion
• ROI within 2 months

Would you be interested in a personalized demo showing exactly how this would work for {company}?

I have availability {availability}.

Best regards,
{sales_rep_name}""",
            
            'competitor_mention': """Subject: FormFlow AI vs {competitor} - Quick comparison

Hi {name},

I saw you mentioned evaluating {competitor}. Smart to compare options!

Here's how FormFlow AI specifically addresses your needs better:

{comparison_points}

Unlike {competitor}, we offer:
• {differentiator_1}
• {differentiator_2}
• {differentiator_3}

Happy to show you a side-by-side comparison. Are you free for a quick call {call_time}?

Best regards,
{sales_rep_name}"""
        }
        
        # Call scripts
        self.call_scripts = {
            'opening': """Hi {name}, this is {sales_rep_name} from FormFlow AI. 

I just received your form submission about {main_challenge}. I wanted to reach out immediately because I noticed your {urgency_indicator}.

Do you have 2 minutes to discuss how we can help you {desired_outcome}?""",
            
            'qualifying': """I see you mentioned {pain_point}. Can you tell me more about:
1. How much time this currently takes your team?
2. What solution are you using now?
3. What would success look like for you?""",
            
            'closing': """Based on what you've shared, FormFlow AI is a perfect fit because {reasons}.

The next step would be {next_step}. Does {proposed_time} work for you?"""
        }
    
    async def generate_recommendations(
        self,
        lead_data: Dict,
        lead_score: int,
        score_category: str = 'warm',
        urgency: str = 'medium'
    ) -> List[Dict]:
        """
        Generate personalized follow-up recommendations
        
        Returns:
            List of recommendation dictionaries with actions, timing, and templates
        """
        # Analyze lead characteristics
        insights = self._analyze_lead(lead_data)
        
        # Generate base recommendations
        base_recommendations = self._generate_base_recommendations(
            score_category,
            urgency,
            insights
        )
        
        # Enhance with AI
        ai_recommendations = await self._enhance_with_ai(
            lead_data,
            lead_score,
            insights,
            base_recommendations
        )
        
        # Add templates and scripts
        final_recommendations = self._add_templates(
            ai_recommendations,
            lead_data,
            insights
        )
        
        # Prioritize recommendations
        return self._prioritize_recommendations(final_recommendations)
    
    def _analyze_lead(self, lead_data: Dict) -> Dict:
        """Analyze lead data to extract key insights"""
        insights = {
            'has_budget': False,
            'has_timeline': False,
            'is_decision_maker': False,
            'has_pain_points': False,
            'mentioned_competitor': False,
            'company_size': 'unknown',
            'urgency_level': 'medium',
            'main_challenge': None,
            'desired_outcome': None,
            'current_solution': None,
            'competitors': []
        }
        
        form_text = json.dumps(lead_data).lower()
        
        # Check for budget
        if any(indicator in form_text for indicator in ['budget', '$', 'invest', 'spend']):
            insights['has_budget'] = True
        
        # Check for timeline
        timeline_indicators = ['immediate', 'asap', 'urgent', 'q1', 'q2', 'month', 'week']
        if any(indicator in form_text for indicator in timeline_indicators):
            insights['has_timeline'] = True
            if any(urgent in form_text for urgent in ['immediate', 'asap', 'urgent']):
                insights['urgency_level'] = 'high'
        
        # Check for decision maker
        authority_indicators = ['ceo', 'cto', 'director', 'manager', 'vp', 'head of']
        if any(indicator in form_text for indicator in authority_indicators):
            insights['is_decision_maker'] = True
        
        # Check for pain points
        pain_indicators = ['problem', 'challenge', 'issue', 'struggle', 'difficult', 'frustrat']
        if any(indicator in form_text for indicator in pain_indicators):
            insights['has_pain_points'] = True
        
        # Check for competitors
        competitors = ['salesforce', 'hubspot', 'excel', 'manual', 'spreadsheet']
        found_competitors = [comp for comp in competitors if comp in form_text]
        if found_competitors:
            insights['mentioned_competitor'] = True
            insights['competitors'] = found_competitors
            insights['current_solution'] = found_competitors[0]
        
        # Extract main challenge (simplified)
        if 'challenge' in lead_data:
            insights['main_challenge'] = lead_data['challenge']
        elif 'problem' in lead_data:
            insights['main_challenge'] = lead_data['problem']
        
        return insights
    
    def _generate_base_recommendations(
        self,
        score_category: str,
        urgency: str,
        insights: Dict
    ) -> List[Dict]:
        """Generate base recommendations based on score and urgency"""
        recommendations = []
        
        # Primary action based on score
        if score_category == 'hot':
            recommendations.append({
                'action': 'Call immediately to capture high interest',
                'priority': 'high',
                'timing': self.timing_by_urgency.get(urgency, 'Within 24 hours'),
                'method': 'call',
                'reason': 'Hot lead with high conversion probability'
            })
            
            recommendations.append({
                'action': 'Schedule product demo',
                'priority': 'high',
                'timing': 'Within 48 hours',
                'method': 'demo',
                'reason': 'Demonstrate value while interest is peak'
            })
        
        elif score_category == 'warm':
            recommendations.append({
                'action': 'Send personalized email with case study',
                'priority': 'high',
                'timing': self.timing_by_urgency.get(urgency, 'Within 48 hours'),
                'method': 'email',
                'reason': 'Build trust with relevant success stories'
            })
            
            recommendations.append({
                'action': 'Follow up with phone call',
                'priority': 'medium',
                'timing': '2-3 days after email',
                'method': 'call',
                'reason': 'Personal touch to move deal forward'
            })
        
        else:  # cold
            recommendations.append({
                'action': 'Add to nurture email sequence',
                'priority': 'medium',
                'timing': 'Immediately',
                'method': 'email',
                'reason': 'Build relationship over time'
            })
            
            recommendations.append({
                'action': 'Connect on LinkedIn',
                'priority': 'low',
                'timing': 'This week',
                'method': 'linkedin',
                'reason': 'Stay connected for future opportunities'
            })
        
        # Additional recommendations based on insights
        if insights['mentioned_competitor']:
            recommendations.append({
                'action': f"Send comparison guide vs {insights['competitors'][0]}",
                'priority': 'high',
                'timing': 'Within 24 hours',
                'method': 'email',
                'reason': 'Address competitive concerns directly'
            })
        
        if insights['has_budget'] and insights['is_decision_maker']:
            recommendations.append({
                'action': 'Send ROI calculator and pricing',
                'priority': 'high',
                'timing': 'Immediately',
                'method': 'email',
                'reason': 'Decision maker with budget ready'
            })
        
        if not insights['is_decision_maker']:
            recommendations.append({
                'action': 'Identify and connect with decision maker',
                'priority': 'medium',
                'timing': 'This week',
                'method': 'linkedin',
                'reason': 'Need to reach budget authority'
            })
        
        return recommendations
    
    async def _enhance_with_ai(
        self,
        lead_data: Dict,
        lead_score: int,
        insights: Dict,
        base_recommendations: List[Dict]
    ) -> List[Dict]:
        """Enhance recommendations using AI"""
        try:
            prompt = f"""
            Analyze this lead and enhance the follow-up recommendations:
            
            Lead Score: {lead_score}
            Lead Data: {json.dumps(lead_data)}
            Insights: {json.dumps(insights)}
            Base Recommendations: {json.dumps(base_recommendations)}
            
            Enhance each recommendation with:
            1. More specific action details
            2. Personalization suggestions
            3. Optimal timing based on buying signals
            4. Success probability
            
            Add 2-3 additional creative recommendations based on the lead's specific situation.
            
            Format as JSON array with keys: action, priority, timing, method, template_snippet, reason, success_probability
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            # Merge AI enhancements with base recommendations
            enhanced = base_recommendations.copy()
            
            # Add AI-generated recommendations
            if isinstance(ai_response, list):
                for ai_rec in ai_response[:3]:  # Limit to 3 additional
                    if all(key in ai_rec for key in ['action', 'priority', 'timing']):
                        enhanced.append(ai_rec)
            
            return enhanced
            
        except Exception as e:
            print(f"AI enhancement error: {e}")
            # Return base recommendations if AI fails
            return base_recommendations
    
    def _add_templates(
        self,
        recommendations: List[Dict],
        lead_data: Dict,
        insights: Dict
    ) -> List[Dict]:
        """Add email templates and call scripts to recommendations"""
        enhanced_recs = []
        
        for rec in recommendations:
            enhanced = rec.copy()
            
            # Add email template if email method
            if rec.get('method') == 'email':
                template_key = 'hot_lead' if 'immediate' in rec.get('timing', '').lower() else 'warm_lead'
                if insights['mentioned_competitor']:
                    template_key = 'competitor_mention'
                
                template = self.email_templates.get(template_key, '')
                
                # Basic template variable replacement
                template = template.replace('{name}', lead_data.get('name', 'there'))
                template = template.replace('{company}', lead_data.get('company', 'your company'))
                template = template.replace('{pain_point}', insights.get('main_challenge', 'challenge'))
                
                enhanced['template'] = template
            
            # Add call script if call method
            elif rec.get('method') == 'call':
                script = self.call_scripts['opening']
                script = script.replace('{name}', lead_data.get('name', 'there'))
                script = script.replace('{main_challenge}', insights.get('main_challenge', 'challenge'))
                
                enhanced['template'] = script
            
            enhanced_recs.append(enhanced)
        
        return enhanced_recs
    
    def _prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Prioritize and sort recommendations"""
        # Define priority order
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        # Sort by priority and limit to top 5
        sorted_recs = sorted(
            recommendations,
            key=lambda x: priority_order.get(x.get('priority', 'low'), 3)
        )
        
        return sorted_recs[:5]
    
    def track_recommendation_effectiveness(
        self,
        recommendation_id: UUID,
        outcome: str,
        notes: Optional[str] = None
    ):
        """Track the effectiveness of recommendations for future improvement"""
        # This would store feedback in a database table for ML training
        # Implementation depends on your tracking requirements
        pass