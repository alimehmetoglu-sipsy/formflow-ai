from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TypeformAnswer(BaseModel):
    field: Dict[str, Any]
    type: str
    text: Optional[str] = None
    number: Optional[float] = None
    boolean: Optional[bool] = None
    choice: Optional[Dict] = None
    choices: Optional[List[Dict]] = None

class TypeformWebhook(BaseModel):
    event_id: str
    event_type: str
    form_response: Dict[str, Any]
    
    def parse_answers(self) -> Dict[str, Any]:
        """Extract and normalize answers from Typeform response"""
        answers = {}
        for answer in self.form_response.get("answers", []):
            field_id = answer["field"]["id"]
            # Use field title if available, otherwise use field id
            field_title = answer["field"].get("title", field_id)
            
            # Handle different answer types
            value = None
            if answer["type"] == "text":
                value = answer.get("text")
            elif answer["type"] == "number":
                value = answer.get("number")
            elif answer["type"] == "boolean":
                value = answer.get("boolean")
            elif answer["type"] == "choice":
                value = answer.get("choice", {}).get("label")
            elif answer["type"] == "choices":
                value = [c.get("label") for c in answer.get("choices", [])]
            elif answer["type"] == "email":
                value = answer.get("email")
            elif answer["type"] == "url":
                value = answer.get("url")
            elif answer["type"] == "date":
                value = answer.get("date")
            
            answers[field_title] = value
        
        return answers