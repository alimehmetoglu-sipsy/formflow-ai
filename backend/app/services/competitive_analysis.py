"""
Competitive Analysis Service for FA-49
Service for detecting competitors and generating battle cards
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID
import openai

from app.models.competitive_analysis import (
    CompetitorProfile,
    CompetitiveInsight,
    ObjectionHandler,
    BattleCard,
    CompetitiveOutcome
)
from app.models.form import FormSubmission
from app.core.config import settings


class CompetitiveAnalysisService:
    """Service for competitive analysis and battle card generation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        
        # Competitor detection patterns
        self.competitor_patterns = {
            'salesforce': {
                'keywords': ['salesforce', 'sfdc', 'sf crm'],
                'category': 'enterprise_crm',
                'tier': 'enterprise'
            },
            'hubspot': {
                'keywords': ['hubspot', 'hub spot'],
                'category': 'marketing_automation',
                'tier': 'mid_market'
            },
            'pipedrive': {
                'keywords': ['pipedrive', 'pipe drive'],
                'category': 'sales_crm',
                'tier': 'smb'
            },
            'excel': {
                'keywords': ['excel', 'spreadsheet', 'sheets', 'google sheets'],
                'category': 'manual_process',
                'tier': 'manual'
            },
            'custom': {
                'keywords': ['custom', 'in-house', 'built internally', 'homegrown'],
                'category': 'custom_solution',
                'tier': 'custom'
            },
            'none': {
                'keywords': ['nothing', 'manual', 'no solution', 'pen and paper'],
                'category': 'no_solution',
                'tier': 'none'
            }
        }
        
        # Default battle cards
        self.default_battle_cards = self._load_default_battle_cards()
    
    async def analyze_competition(
        self,
        submission_id: UUID,
        form_data: Dict
    ) -> CompetitiveInsight:
        """
        Analyze form submission for competitive intelligence
        """
        # Detect competitors
        detected_competitors, confidence = self._detect_competitors(form_data)
        
        # Get or create competitor profiles
        competitor_profiles = []
        for comp_name in detected_competitors:
            profile = self._get_or_create_competitor(comp_name)
            competitor_profiles.append(profile)
        
        # Generate positioning strategy
        positioning = await self._generate_positioning(
            form_data,
            detected_competitors,
            competitor_profiles
        )
        
        # Create competitive insight
        primary_competitor = competitor_profiles[0] if competitor_profiles else None
        
        insight = CompetitiveInsight(
            submission_id=submission_id,
            competitor_id=primary_competitor.id if primary_competitor else None,
            competitors_detected=detected_competitors,
            detection_method='explicit' if confidence > 0.8 else 'implicit',
            confidence_score=confidence,
            mention_context=self._extract_mention_context(form_data, detected_competitors),
            current_solution=form_data.get('current_solution', detected_competitors[0] if detected_competitors else None),
            positioning_strategy=positioning['strategy'],
            recommended_approach=positioning['approach'],
            battle_points=positioning['battle_points'],
            risk_factors=positioning['risks']
        )
        
        self.db.add(insight)
        self.db.commit()
        
        return insight
    
    def _detect_competitors(self, form_data: Dict) -> Tuple[List[str], float]:
        """Detect competitors mentioned in form data"""
        form_text = json.dumps(form_data).lower()
        detected = []
        confidence_scores = []
        
        for comp_name, comp_data in self.competitor_patterns.items():
            for keyword in comp_data['keywords']:
                if keyword in form_text:
                    detected.append(comp_name)
                    # Higher confidence for exact matches
                    if f'"{keyword}"' in form_text or f' {keyword} ' in form_text:
                        confidence_scores.append(0.95)
                    else:
                        confidence_scores.append(0.75)
                    break
        
        # Use AI for implicit detection if no explicit mentions
        if not detected:
            detected, ai_confidence = self._ai_detect_competitors(form_text)
            confidence_scores = [ai_confidence] * len(detected)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        return detected, avg_confidence
    
    def _ai_detect_competitors(self, form_text: str) -> Tuple[List[str], float]:
        """Use AI to detect implicit competitor mentions"""
        try:
            prompt = f"""
            Analyze this text for any mentions of competitors or current solutions.
            Look for indirect references like "our current CRM", "existing system", etc.
            
            Text: {form_text[:1000]}
            
            Return JSON with: competitors (list), confidence (0-1)
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('competitors', []), result.get('confidence', 0.5)
        except:
            return [], 0.0
    
    def _get_or_create_competitor(self, name: str) -> CompetitorProfile:
        """Get existing competitor profile or create new one"""
        competitor = self.db.query(CompetitorProfile).filter(
            CompetitorProfile.name == name
        ).first()
        
        if not competitor:
            # Create new profile with defaults
            battle_card = self.default_battle_cards.get(name, self._get_generic_battle_card())
            
            competitor = CompetitorProfile(
                name=name,
                display_name=name.title(),
                strengths=battle_card.get('strengths', []),
                weaknesses=battle_card.get('weaknesses', []),
                our_advantages=battle_card.get('our_advantages', []),
                their_advantages=battle_card.get('their_advantages', []),
                positioning_strategy=battle_card.get('positioning', ''),
                key_differentiators=battle_card.get('differentiators', []),
                battle_card=battle_card
            )
            
            self.db.add(competitor)
            self.db.commit()
        
        return competitor
    
    async def _generate_positioning(
        self,
        form_data: Dict,
        competitors: List[str],
        profiles: List[CompetitorProfile]
    ) -> Dict:
        """Generate competitive positioning strategy"""
        if not competitors:
            return {
                'strategy': 'Focus on unique value proposition',
                'approach': ['Emphasize ease of use', 'Highlight ROI', 'Show quick time to value'],
                'battle_points': ['No current solution means no switching costs', 'Green field opportunity'],
                'risks': []
            }
        
        primary_competitor = profiles[0] if profiles else None
        
        try:
            prompt = f"""
            Generate competitive positioning strategy.
            
            Lead is evaluating: {', '.join(competitors)}
            Current solution: {form_data.get('current_solution', 'unknown')}
            Pain points: {form_data.get('pain_points', [])}
            Timeline: {form_data.get('timeline', 'not specified')}
            
            Our advantages over {competitors[0]}:
            {primary_competitor.our_advantages if primary_competitor else []}
            
            Provide:
            1. Positioning strategy (1-2 sentences)
            2. Key approach points (3-5 bullets)
            3. Battle points to emphasize (3-5 bullets)
            4. Risks to mitigate (2-3 bullets)
            
            Format as JSON.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
        except:
            # Fallback positioning
            return {
                'strategy': f'Position as modern alternative to {competitors[0]}',
                'approach': [
                    'Faster implementation',
                    'Better ROI',
                    'Superior support',
                    'No hidden costs'
                ],
                'battle_points': primary_competitor.our_advantages[:3] if primary_competitor else [],
                'risks': ['Switching costs', 'Change resistance']
            }
    
    def get_battle_card(self, competitor_name: str) -> Dict:
        """Get battle card for specific competitor"""
        competitor = self.db.query(CompetitorProfile).filter(
            CompetitorProfile.name == competitor_name
        ).first()
        
        if competitor and competitor.battle_card:
            return competitor.battle_card
        
        return self.default_battle_cards.get(competitor_name, self._get_generic_battle_card())
    
    def get_objection_handlers(self, competitor_id: UUID) -> List[ObjectionHandler]:
        """Get objection handling scripts for competitor"""
        return self.db.query(ObjectionHandler).filter(
            ObjectionHandler.competitor_id == competitor_id,
            ObjectionHandler.is_active == True
        ).all()
    
    def track_competitive_outcome(
        self,
        lead_id: UUID,
        competitor_id: UUID,
        outcome: str,
        details: Dict
    ):
        """Track win/loss against competitor"""
        # Record outcome
        outcome_record = CompetitiveOutcome(
            lead_id=lead_id,
            competitor_id=competitor_id,
            outcome=outcome,
            outcome_date=datetime.utcnow(),
            primary_reason=details.get('reason'),
            deal_size=details.get('deal_size'),
            what_worked=details.get('what_worked'),
            what_didnt_work=details.get('what_didnt_work')
        )
        
        self.db.add(outcome_record)
        
        # Update competitor win/loss stats
        competitor = self.db.query(CompetitorProfile).filter(
            CompetitorProfile.id == competitor_id
        ).first()
        
        if competitor:
            competitor.total_competitions += 1
            if outcome == 'won':
                competitor.wins_against += 1
            elif outcome == 'lost':
                competitor.losses_against += 1
            
            # Recalculate win rate
            if competitor.total_competitions > 0:
                competitor.win_rate = competitor.wins_against / competitor.total_competitions
        
        self.db.commit()
    
    def _extract_mention_context(self, form_data: Dict, competitors: List[str]) -> str:
        """Extract context where competitor was mentioned"""
        form_text = json.dumps(form_data)
        contexts = []
        
        for comp in competitors:
            # Find sentences containing competitor mention
            sentences = form_text.split('.')
            for sentence in sentences:
                if comp in sentence.lower():
                    contexts.append(sentence.strip())
        
        return ' | '.join(contexts[:3])  # Return up to 3 context sentences
    
    def _load_default_battle_cards(self) -> Dict:
        """Load default battle cards for known competitors"""
        return {
            'salesforce': {
                'strengths': ['Market leader', 'Enterprise features', 'Extensive ecosystem'],
                'weaknesses': ['Complex setup', 'Expensive', 'Steep learning curve'],
                'our_advantages': [
                    '80% faster implementation (5 minutes vs 2+ weeks)',
                    '70% lower cost of ownership',
                    'No technical skills required',
                    'AI-powered insights out of the box',
                    'Instant value - no consulting needed'
                ],
                'their_advantages': [
                    'Established brand',
                    'Large partner ecosystem',
                    'Enterprise-grade security'
                ],
                'positioning': 'Modern, AI-first alternative that delivers instant value without the complexity',
                'differentiators': ['AI automation', 'Instant setup', 'No training required'],
                'objection_handlers': {
                    'price': 'While Salesforce may seem established, consider the total cost including implementation, training, and maintenance. FormFlow delivers 80% of the value at 30% of the cost.',
                    'features': 'FormFlow focuses on what actually drives results - turning form data into insights. We eliminate feature bloat and complexity.',
                    'trust': 'We serve 500+ growing companies who switched from Salesforce and saw immediate ROI.'
                }
            },
            'hubspot': {
                'strengths': ['All-in-one platform', 'Good marketing tools', 'Free tier'],
                'weaknesses': ['Limited AI capabilities', 'Gets expensive at scale', 'Form analytics basic'],
                'our_advantages': [
                    'Specialized in form-to-insight transformation',
                    'Advanced AI analysis vs basic reporting',
                    'Instant dashboard generation',
                    'No per-contact pricing',
                    'Purpose-built for conversion optimization'
                ],
                'their_advantages': [
                    'Broader marketing toolkit',
                    'Built-in CRM',
                    'Email marketing included'
                ],
                'positioning': 'Purpose-built for teams that need deep form insights, not another generic marketing platform',
                'differentiators': ['AI insights', 'Specialized for forms', 'Predictable pricing']
            },
            'excel': {
                'strengths': ['Familiar', 'Flexible', 'Low cost'],
                'weaknesses': ['Manual process', 'Error-prone', 'No real-time insights', 'No collaboration'],
                'our_advantages': [
                    '95% time savings on analysis',
                    'Real-time insights vs manual updates',
                    'AI-powered recommendations',
                    'Zero errors vs manual formulas',
                    'Team collaboration built-in',
                    'Scales with your growth'
                ],
                'their_advantages': [
                    'No learning curve',
                    'One-time cost',
                    'Complete control'
                ],
                'positioning': 'Graduate from manual spreadsheets to AI-powered insights that scale with your business',
                'differentiators': ['Automation', 'AI insights', 'Real-time updates', 'Collaboration']
            }
        }
    
    def _get_generic_battle_card(self) -> Dict:
        """Get generic battle card for unknown competitors"""
        return {
            'strengths': ['Unknown'],
            'weaknesses': ['Unknown'],
            'our_advantages': [
                'Purpose-built for form insights',
                'AI-powered analysis',
                '5-minute setup',
                'No technical skills required',
                'Instant ROI'
            ],
            'their_advantages': ['Existing relationship'],
            'positioning': 'Modern AI-first solution that delivers immediate value',
            'differentiators': ['Simplicity', 'Speed', 'Intelligence']
        }