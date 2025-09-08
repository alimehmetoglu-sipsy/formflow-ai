from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class GoogleFormsResponse(BaseModel):
    """Google Forms response schema"""
    responseId: str
    createTime: str
    lastSubmittedTime: str
    answers: Dict[str, Any]
    
    def parse_answers(self) -> Dict[str, Any]:
        """Extract and normalize answers from Google Forms response"""
        parsed = {}
        
        for question_id, answer_data in self.answers.items():
            # Handle different Google Forms answer types
            if "textAnswers" in answer_data:
                # Text response
                texts = answer_data["textAnswers"]["answers"]
                parsed[question_id] = texts[0]["value"] if texts else ""
            
            elif "choiceAnswers" in answer_data:
                # Multiple choice or checkbox
                choices = answer_data["choiceAnswers"]["answers"]
                if len(choices) == 1:
                    parsed[question_id] = choices[0]["value"]
                else:
                    parsed[question_id] = [c["value"] for c in choices]
            
            elif "scaleAnswer" in answer_data:
                # Linear scale
                parsed[question_id] = answer_data["scaleAnswer"]["value"]
            
            elif "dateAnswer" in answer_data:
                # Date
                date_parts = answer_data["dateAnswer"]
                parsed[question_id] = f"{date_parts.get('year')}-{date_parts.get('month', 1):02d}-{date_parts.get('day', 1):02d}"
            
            elif "timeAnswer" in answer_data:
                # Time
                time_parts = answer_data["timeAnswer"]
                parsed[question_id] = f"{time_parts.get('hour', 0):02d}:{time_parts.get('minute', 0):02d}"
            
            elif "fileUploadAnswers" in answer_data:
                # File upload
                files = answer_data["fileUploadAnswers"]["answers"]
                parsed[question_id] = [f["fileId"] for f in files]
            
            else:
                # Unknown type, store as is
                parsed[question_id] = answer_data
        
        return parsed

class SimpleGoogleFormsResponse(BaseModel):
    """Simplified Google Forms response for Apps Script"""
    question: str
    answer: str

class GoogleFormsWebhook(BaseModel):
    """Google Forms webhook payload - flexible schema"""
    # Original complex schema fields (optional)
    formId: Optional[str] = None
    formTitle: Optional[str] = None
    response: Optional[GoogleFormsResponse] = None
    eventType: str = "form_response"
    
    # Simplified schema fields from Apps Script
    form_id: Optional[str] = None
    form_title: Optional[str] = None
    response_id: Optional[str] = None
    timestamp: Optional[str] = None
    responses: Optional[List[SimpleGoogleFormsResponse]] = None
    
    def to_typeform_format(self) -> Dict[str, Any]:
        """Convert Google Forms webhook to Typeform format for compatibility"""
        # Handle both complex and simple formats
        if self.response:
            # Complex format from Google Forms API
            return {
                "event_id": self.response.responseId,
                "event_type": "form_response",
                "form_response": {
                    "form_id": self.formId or "unknown",
                    "token": self.response.responseId[:8],
                    "submitted_at": self.response.lastSubmittedTime,
                    "definition": {
                        "title": self.formTitle or "Google Form"
                    },
                    "answers": self._convert_answers()
                }
            }
        else:
            # Simple format from Apps Script
            return {
                "event_id": self.response_id or str(datetime.now().timestamp()),
                "event_type": "form_response",
                "form_response": {
                    "form_id": self.form_id or "google_form",
                    "token": (self.response_id or str(datetime.now().timestamp()))[:8],
                    "submitted_at": self.timestamp or datetime.now().isoformat(),
                    "definition": {
                        "title": self.form_title or "Google Form"
                    },
                    "answers": self._convert_simple_answers()
                }
            }
    
    def _convert_answers(self) -> List[Dict[str, Any]]:
        """Convert Google Forms answers to Typeform format"""
        answers = []
        parsed = self.response.parse_answers()
        
        for idx, (question_id, value) in enumerate(parsed.items()):
            answer_type = self._detect_type(value)
            answer = {
                "field": {
                    "id": question_id,
                    "title": f"Question {idx + 1}"  # Will be enhanced with actual questions
                },
                "type": answer_type
            }
            
            # Add value based on type
            if answer_type == "text":
                answer["text"] = str(value)
            elif answer_type == "number":
                answer["number"] = float(value) if isinstance(value, (int, float)) else 0
            elif answer_type == "choice":
                answer["choice"] = {"label": str(value)}
            elif answer_type == "choices":
                answer["choices"] = [{"label": str(v)} for v in value]
            elif answer_type == "date":
                answer["date"] = str(value)
            
            answers.append(answer)
        
        return answers
    
    def _convert_simple_answers(self) -> List[Dict[str, Any]]:
        """Convert simple Google Forms answers (from Apps Script) to Typeform format"""
        answers = []
        
        if not self.responses:
            return answers
        
        for idx, response in enumerate(self.responses):
            answer_type = self._detect_type(response.answer)
            answer = {
                "field": {
                    "id": f"question_{idx}",
                    "title": response.question
                },
                "type": answer_type
            }
            
            # Add value based on type
            if answer_type == "text":
                answer["text"] = str(response.answer)
            elif answer_type == "number":
                answer["number"] = float(response.answer) if isinstance(response.answer, (int, float)) else 0
            elif answer_type == "choice":
                answer["choice"] = {"label": str(response.answer)}
            elif answer_type == "choices":
                # If answer is already a list
                if isinstance(response.answer, list):
                    answer["choices"] = [{"label": str(v)} for v in response.answer]
                else:
                    answer["choices"] = [{"label": str(response.answer)}]
            elif answer_type == "date":
                answer["date"] = str(response.answer)
            
            answers.append(answer)
        
        return answers
    
    def _detect_type(self, value: Any) -> str:
        """Detect answer type from value"""
        if isinstance(value, list):
            return "choices"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        else:
            # Check if it's a date format
            if isinstance(value, str) and len(value) == 10 and value.count('-') == 2:
                return "date"
            return "text"