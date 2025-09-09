"""
Lead Scoring Service for FA-45
AI-powered lead scoring algorithm with weighted criteria and buying signal detection
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from uuid import UUID
import openai

from app.models.lead_score import LeadScore, ScoringRule
from app.models.form import FormSubmission
from app.core.config import settings


class LeadScoringEngine:
    """Engine for calculating lead scores based on form data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        
        # Default scoring weights
        self.default_weights = {
            "budget": 0.30,      # 30% weight
            "timeline": 0.25,    # 25% weight
            "authority": 0.20,   # 20% weight
            "need": 0.15,        # 15% weight
            "company_size": 0.10 # 10% weight
        }
        
        # Budget thresholds
        self.budget_thresholds = [
            (100000, 30),  # >$100k = 30 points
            (50000, 25),   # >$50k = 25 points
            (25000, 20),   # >$25k = 20 points
            (10000, 15),   # >$10k = 15 points
            (5000, 10),    # >$5k = 10 points
            (0, 5)         # <$5k = 5 points
        ]
        
        # Timeline scoring
        self.timeline_scores = {
            "immediate": 25,
            "this_month": 23,
            "q1": 20,
            "q2": 15,
            "q3": 10,
            "q4": 5,
            "next_year": 3,
            "no_timeline": 0
        }
        
        # Authority levels
        self.authority_scores = {
            "decision_maker": 20,
            "influencer": 15,
            "recommender": 10,
            "evaluator": 8,
            "end_user": 5,
            "unknown": 2
        }
        
        # Company size scores
        self.company_size_scores = {
            "enterprise": 10,    # 1000+ employees
            "mid_market": 8,     # 100-999 employees
            "small_business": 6, # 10-99 employees
            "startup": 4,        # <10 employees
            "unknown": 2
        }
        
        # Buying signals keywords
        self.buying_signals = {
            "high_urgency": ["urgent", "asap", "immediately", "critical", "pressing", "time-sensitive"],
            "budget_ready": ["budget approved", "funded", "ready to invest", "allocated funds"],
            "pain_points": ["struggling", "frustrated", "losing money", "inefficient", "manual process", "time-consuming"],
            "comparison": ["comparing", "evaluating", "looking at alternatives", "researching solutions"],
            "commitment": ["ready to move forward", "want to get started", "implement", "deploy"]
        }
    
    async def calculate_lead_score(self, submission_id: UUID, form_data: Dict) -> LeadScore:
        """Calculate comprehensive lead score for a form submission"""
        
        # Calculate base score components
        budget_score = self._score_budget(form_data)
        timeline_score = self._score_timeline(form_data)
        authority_score = self._score_authority(form_data)
        need_score = self._score_need(form_data)
        company_score = self._score_company_size(form_data)
        
        # Calculate weighted base score
        base_score = (
            budget_score * self.default_weights["budget"] +
            timeline_score * self.default_weights["timeline"] +
            authority_score * self.default_weights["authority"] +
            need_score * self.default_weights["need"] +
            company_score * self.default_weights["company_size"]
        )
        
        # Get AI adjustment based on buying signals
        ai_adjustment, ai_insights, signals = await self._get_ai_adjustment(form_data)
        
        # Calculate final score (capped at 100)
        final_score = min(100, int(base_score + ai_adjustment))
        
        # Determine category
        if final_score >= 80:
            category = "hot"
        elif final_score >= 60:
            category = "warm"
        else:
            category = "cold"
        
        # Create score factors breakdown
        score_factors = {
            "budget": {"value": budget_score, "weight": self.default_weights["budget"]},
            "timeline": {"value": timeline_score, "weight": self.default_weights["timeline"]},
            "authority": {"value": authority_score, "weight": self.default_weights["authority"]},
            "need": {"value": need_score, "weight": self.default_weights["need"]},
            "company_size": {"value": company_score, "weight": self.default_weights["company_size"]}
        }
        
        # Save to database
        lead_score = LeadScore(
            submission_id=submission_id,
            base_score=int(base_score),
            ai_adjustment=ai_adjustment,
            final_score=final_score,
            score_factors=score_factors,
            score_category=category,
            ai_insights=ai_insights,
            buying_signals_detected=signals,
            calculated_at=datetime.utcnow()
        )
        
        self.db.add(lead_score)
        self.db.commit()
        self.db.refresh(lead_score)
        
        return lead_score
    
    def _score_budget(self, form_data: Dict) -> int:
        """Score based on budget information"""
        budget_fields = ["budget", "investment", "spending", "price_range"]
        
        for field in budget_fields:
            if field in form_data:
                value = str(form_data[field]).lower()
                
                # Extract numeric value
                numbers = re.findall(r'\d+', value.replace(',', ''))
                if numbers:
                    amount = int(numbers[0])
                    
                    # Check if it's in thousands (k) or millions (m)
                    if 'k' in value:
                        amount *= 1000
                    elif 'm' in value:
                        amount *= 1000000
                    
                    # Return score based on thresholds
                    for threshold, score in self.budget_thresholds:
                        if amount >= threshold:
                            return score
        
        return 5  # Default low score if no budget info
    
    def _score_timeline(self, form_data: Dict) -> int:
        """Score based on purchase timeline"""
        timeline_fields = ["timeline", "when", "timeframe", "purchase_date", "implementation"]
        
        for field in timeline_fields:
            if field in form_data:
                value = str(form_data[field]).lower()
                
                # Check for immediate indicators
                if any(word in value for word in ["immediate", "asap", "urgent", "now"]):
                    return self.timeline_scores["immediate"]
                
                # Check for month references
                if "this month" in value or "30 days" in value:
                    return self.timeline_scores["this_month"]
                
                # Check for quarter references
                if "q1" in value or "first quarter" in value:
                    return self.timeline_scores["q1"]
                elif "q2" in value or "second quarter" in value:
                    return self.timeline_scores["q2"]
                elif "q3" in value or "third quarter" in value:
                    return self.timeline_scores["q3"]
                elif "q4" in value or "fourth quarter" in value:
                    return self.timeline_scores["q4"]
                
                # Check for year references
                if "next year" in value or "2026" in value:
                    return self.timeline_scores["next_year"]
        
        return self.timeline_scores["no_timeline"]
    
    def _score_authority(self, form_data: Dict) -> int:
        """Score based on decision-making authority"""
        authority_fields = ["role", "title", "position", "job_title", "authority"]
        
        decision_maker_keywords = ["ceo", "cto", "cfo", "president", "vp", "director", "head of", "manager", "owner", "founder"]
        influencer_keywords = ["lead", "senior", "principal", "architect", "consultant"]
        
        for field in authority_fields:
            if field in form_data:
                value = str(form_data[field]).lower()
                
                # Check for decision maker
                if any(keyword in value for keyword in decision_maker_keywords):
                    return self.authority_scores["decision_maker"]
                
                # Check for influencer
                if any(keyword in value for keyword in influencer_keywords):
                    return self.authority_scores["influencer"]
                
                # Check for explicit authority mention
                if "decision" in value or "approve" in value or "budget" in value:
                    return self.authority_scores["decision_maker"]
        
        return self.authority_scores["unknown"]
    
    def _score_need(self, form_data: Dict) -> int:
        """Score based on identified needs and pain points"""
        need_score = 0
        max_score = 15
        
        # Convert all form data to searchable text
        form_text = json.dumps(form_data).lower()
        
        # Check for pain point indicators
        pain_indicators = ["problem", "challenge", "issue", "struggling", "difficult", "frustrat", "pain", "inefficient"]
        pain_count = sum(1 for indicator in pain_indicators if indicator in form_text)
        
        # Check for specific needs
        need_indicators = ["need", "require", "looking for", "want", "seeking", "must have"]
        need_count = sum(1 for indicator in need_indicators if indicator in form_text)
        
        # Calculate score based on indicators found
        indicator_score = min(max_score, (pain_count * 3) + (need_count * 2))
        
        return indicator_score
    
    def _score_company_size(self, form_data: Dict) -> int:
        """Score based on company size"""
        size_fields = ["company_size", "employees", "team_size", "organization_size"]
        
        for field in size_fields:
            if field in form_data:
                value = str(form_data[field]).lower()
                
                # Extract numbers
                numbers = re.findall(r'\d+', value.replace(',', ''))
                if numbers:
                    size = int(numbers[0])
                    
                    if size >= 1000 or "enterprise" in value:
                        return self.company_size_scores["enterprise"]
                    elif size >= 100 or "mid" in value:
                        return self.company_size_scores["mid_market"]
                    elif size >= 10 or "small" in value:
                        return self.company_size_scores["small_business"]
                    else:
                        return self.company_size_scores["startup"]
        
        # Check company name field for size indicators
        if "company" in form_data:
            company = str(form_data["company"]).lower()
            if any(corp in company for corp in ["inc", "corp", "llc", "ltd"]):
                return self.company_size_scores["mid_market"]
        
        return self.company_size_scores["unknown"]
    
    async def _get_ai_adjustment(self, form_data: Dict) -> tuple[int, Dict, List]:
        """Use AI to detect buying signals and adjust score"""
        form_text = json.dumps(form_data)
        
        # Detect buying signals
        detected_signals = []
        for signal_type, keywords in self.buying_signals.items():
            if any(keyword in form_text.lower() for keyword in keywords):
                detected_signals.append(signal_type)
        
        # Get AI insights
        try:
            prompt = f"""
            Analyze this form submission for buying signals and lead quality.
            
            Form Data: {form_text}
            
            Provide:
            1. Additional score adjustment (0-15 points)
            2. Key buying signals detected
            3. Recommended follow-up priority
            
            Format as JSON with keys: adjustment, signals, priority, insights
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            return (
                min(15, ai_response.get("adjustment", 0)),
                ai_response.get("insights", {}),
                detected_signals + ai_response.get("signals", [])
            )
        except Exception as e:
            print(f"AI scoring error: {e}")
            # Fallback to rule-based adjustment
            adjustment = len(detected_signals) * 2  # 2 points per signal
            return min(15, adjustment), {}, detected_signals
    
    def get_score_explanation(self, lead_score: LeadScore) -> Dict:
        """Get human-readable explanation of the score"""
        factors = lead_score.score_factors
        
        explanation = {
            "total_score": lead_score.final_score,
            "category": lead_score.score_category,
            "breakdown": []
        }
        
        for factor, details in factors.items():
            explanation["breakdown"].append({
                "factor": factor.replace("_", " ").title(),
                "points": details["value"],
                "weight": f"{int(details['weight'] * 100)}%",
                "contribution": round(details["value"] * details["weight"], 1)
            })
        
        if lead_score.ai_adjustment > 0:
            explanation["ai_bonus"] = {
                "points": lead_score.ai_adjustment,
                "reason": "Buying signals detected"
            }
        
        return explanation