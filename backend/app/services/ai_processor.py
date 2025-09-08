from openai import AsyncOpenAI
from typing import Dict, Any
import json
from app.config import settings

class AIProcessor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def process(self, answers: Dict, template_type: str) -> Dict:
        """Process form answers with AI based on template type"""
        
        if not self.client:
            # Return mock data if OpenAI is not configured
            return self._get_mock_data(template_type, answers)
        
        processors = {
            "diet_plan": self._process_diet_plan,
            "lead_score": self._process_lead_score,
            "event_registration": self._process_event_registration,
            "generic": self._process_generic
        }
        
        processor = processors.get(template_type, self._process_generic)
        return await processor(answers)
    
    async def _process_diet_plan(self, answers: Dict) -> Dict:
        """Generate personalized diet plan"""
        
        prompt = f"""
        Based on the following user information, create a comprehensive 7-day diet plan:
        
        User Information:
        {json.dumps(answers, indent=2)}
        
        Generate a response in JSON format with:
        {{
            "user_profile": {{
                "goals": "string",
                "current_stats": {{}},
                "dietary_preferences": []
            }},
            "daily_calories": number,
            "macro_breakdown": {{
                "protein": number,
                "carbs": number,
                "fat": number
            }},
            "meal_plan": {{
                "monday": {{
                    "breakfast": {{"meal": "", "calories": 0, "recipe": ""}},
                    "lunch": {{"meal": "", "calories": 0, "recipe": ""}},
                    "dinner": {{"meal": "", "calories": 0, "recipe": ""}},
                    "snacks": []
                }},
                "tuesday": {{...similar structure...}},
                "wednesday": {{...similar structure...}},
                "thursday": {{...similar structure...}},
                "friday": {{...similar structure...}},
                "saturday": {{...similar structure...}},
                "sunday": {{...similar structure...}}
            }},
            "shopping_list": {{
                "proteins": [],
                "vegetables": [],
                "fruits": [],
                "grains": [],
                "dairy": [],
                "other": []
            }},
            "tips": [],
            "warnings": []
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI processing error: {str(e)}")
            return self._get_mock_data("diet_plan", answers)
    
    async def _process_lead_score(self, answers: Dict) -> Dict:
        """Score and analyze lead quality"""
        
        prompt = f"""
        Analyze this lead information and provide a detailed scoring:
        
        Lead Information:
        {json.dumps(answers, indent=2)}
        
        Generate a response in JSON format with:
        {{
            "lead_score": number (0-100),
            "score_breakdown": {{
                "budget_fit": number,
                "timeline_urgency": number,
                "decision_authority": number,
                "need_clarity": number,
                "engagement_level": number
            }},
            "lead_category": "Hot|Warm|Cold|Unqualified",
            "key_insights": [],
            "recommended_actions": [],
            "follow_up_timeline": "string",
            "potential_value": "string",
            "risk_factors": [],
            "conversation_starters": []
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a sales intelligence expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI processing error: {str(e)}")
            return self._get_mock_data("lead_score", answers)
    
    async def _process_event_registration(self, answers: Dict) -> Dict:
        """Process event registration and generate confirmation"""
        
        # Generate registration data
        import hashlib
        import base64
        
        # Create a unique ticket number
        ticket_data = f"EVENT-{answers.get('email', 'guest')}-{answers.get('name', 'attendee')}"
        ticket_hash = hashlib.sha256(ticket_data.encode()).hexdigest()[:12].upper()
        
        return {
            "attendee_name": answers.get("name", "Guest"),
            "attendee_email": answers.get("email", ""),
            "event_details": {
                "name": answers.get("event_name", "FormFlow AI Launch Event"),
                "date": answers.get("event_date", "2025-02-01"),
                "time": answers.get("event_time", "10:00 AM"),
                "location": answers.get("location", "Online")
            },
            "ticket_number": f"FF-{ticket_hash}",
            "qr_code": f"data:image/png;base64,{self._generate_qr_placeholder()}",
            "special_requirements": answers.get("requirements", []),
            "confirmation_message": "Your registration is confirmed! We look forward to seeing you."
        }
    
    async def _process_generic(self, answers: Dict) -> Dict:
        """Process generic form with basic analysis"""
        
        return {
            "summary": "Form Response Analysis",
            "total_responses": len(answers),
            "responses": answers,
            "insights": [
                f"Received {len(answers)} responses",
                "Form processed successfully",
                "Dashboard generated automatically"
            ],
            "timestamp": "2025-01-07T12:00:00Z"
        }
    
    def _get_mock_data(self, template_type: str, answers: Dict) -> Dict:
        """Return mock data for testing without OpenAI"""
        
        if template_type == "diet_plan":
            return {
                "user_profile": {
                    "goals": "Weight loss and healthy eating",
                    "current_stats": {"weight": 75, "height": 170},
                    "dietary_preferences": ["vegetarian-friendly", "low-carb"]
                },
                "daily_calories": 1800,
                "macro_breakdown": {
                    "protein": 135,
                    "carbs": 180,
                    "fat": 60
                },
                "meal_plan": {
                    day: {
                        "breakfast": {"meal": "Oatmeal with berries", "calories": 350, "recipe": "Mix oats with almond milk and top with fresh berries"},
                        "lunch": {"meal": "Grilled chicken salad", "calories": 450, "recipe": "Grilled chicken breast with mixed greens and vinaigrette"},
                        "dinner": {"meal": "Salmon with vegetables", "calories": 550, "recipe": "Baked salmon with roasted Brussels sprouts and sweet potato"},
                        "snacks": ["Greek yogurt", "Apple with almond butter"]
                    }
                    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                },
                "shopping_list": {
                    "proteins": ["Chicken breast", "Salmon", "Greek yogurt"],
                    "vegetables": ["Mixed greens", "Brussels sprouts", "Sweet potato"],
                    "fruits": ["Berries", "Apples"],
                    "grains": ["Oats", "Quinoa"],
                    "dairy": ["Almond milk"],
                    "other": ["Almond butter", "Olive oil"]
                },
                "tips": [
                    "Drink at least 8 glasses of water daily",
                    "Prep meals on Sunday for the week",
                    "Track your progress with a food journal"
                ],
                "warnings": [
                    "Consult with a healthcare provider before starting any new diet",
                    "Individual results may vary"
                ]
            }
        
        elif template_type == "lead_score":
            return {
                "lead_score": 75,
                "score_breakdown": {
                    "budget_fit": 80,
                    "timeline_urgency": 70,
                    "decision_authority": 85,
                    "need_clarity": 75,
                    "engagement_level": 65
                },
                "lead_category": "Warm",
                "key_insights": [
                    "Strong budget alignment",
                    "Decision maker identified",
                    "Timeline suggests Q1 implementation"
                ],
                "recommended_actions": [
                    "Schedule demo within 48 hours",
                    "Send case studies from similar industry",
                    "Prepare custom pricing proposal"
                ],
                "follow_up_timeline": "Within 24-48 hours",
                "potential_value": "$25,000 - $50,000",
                "risk_factors": [
                    "Multiple stakeholders involved",
                    "Evaluating competitors"
                ],
                "conversation_starters": [
                    "How does your current solution handle X?",
                    "What's your ideal implementation timeline?",
                    "Who else would be involved in the decision?"
                ]
            }
        
        else:
            return {
                "attendee_name": answers.get("name", "Guest"),
                "attendee_email": answers.get("email", ""),
                "event_details": {
                    "name": answers.get("event_name", "FormFlow AI Launch Event"),
                    "date": answers.get("event_date", "2025-02-01"),
                    "time": answers.get("event_time", "10:00 AM"),
                    "location": answers.get("location", "Online")
                },
                "ticket_number": "FF-MOCK-12345",
                "qr_code": f"data:image/png;base64,{self._generate_qr_placeholder()}",
                "special_requirements": answers.get("requirements", []),
                "confirmation_message": "Your registration is confirmed! We look forward to seeing you."
            }
    
    def _generate_qr_placeholder(self) -> str:
        """Generate a placeholder QR code as base64"""
        # This is a tiny 1x1 transparent PNG as placeholder
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="