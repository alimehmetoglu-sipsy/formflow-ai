import json
import jsonpath_ng
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import hmac
from app.models.webhook import WebhookConfig, WebhookLog
from app.models.form import FormSubmission, Dashboard
from app.schemas.webhook import TypeformWebhook
from sqlalchemy.orm import Session
import uuid

class CustomWebhookProcessor:
    """Process custom webhooks with dynamic field mapping"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_signature(self, payload: bytes, signature: str, secret: str, platform: str) -> bool:
        """Verify webhook signature based on platform"""
        if not secret or not signature:
            return True  # Skip if no secret configured
        
        if platform == "jotform":
            # Jotform uses SHA256
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected)
        elif platform == "microsoft_forms":
            # Microsoft Forms uses SHA256 with "sha256=" prefix
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(f"sha256={expected}", signature)
        else:
            # Default to SHA256
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            # Try both with and without prefix
            return hmac.compare_digest(signature, expected) or \
                   hmac.compare_digest(f"sha256={expected}", signature)
    
    def extract_field_value(self, data: Dict[str, Any], json_path: str) -> Any:
        """Extract value from JSON using JSONPath"""
        try:
            # Handle simple dot notation
            if not json_path.startswith("$"):
                json_path = f"$.{json_path}"
            
            # Parse JSONPath expression
            jsonpath_expr = jsonpath_ng.parse(json_path)
            matches = jsonpath_expr.find(data)
            
            if matches:
                # If single match, return the value
                if len(matches) == 1:
                    return matches[0].value
                # If multiple matches, return as list
                else:
                    return [match.value for match in matches]
            return None
        except Exception as e:
            print(f"Error extracting field with path {json_path}: {str(e)}")
            return None
    
    def map_fields(self, data: Dict[str, Any], field_mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Map webhook data to our standard format using field mappings"""
        mapped_data = {}
        
        # Default field mappings if not specified
        default_mappings = {
            "form_title": "$.form_title",
            "submission_id": "$.id",
            "submitted_at": "$.timestamp",
            "answers": "$.data"
        }
        
        # Merge with user-defined mappings
        mappings = {**default_mappings, **field_mappings}
        
        for target_field, source_path in mappings.items():
            if isinstance(source_path, dict):
                # Handle nested mappings for answers
                mapped_data[target_field] = {}
                for sub_field, sub_path in source_path.items():
                    value = self.extract_field_value(data, sub_path)
                    if value is not None:
                        mapped_data[target_field][sub_field] = value
            else:
                value = self.extract_field_value(data, source_path)
                if value is not None:
                    mapped_data[target_field] = value
        
        # Ensure required fields have defaults
        if "submission_id" not in mapped_data or not mapped_data["submission_id"]:
            mapped_data["submission_id"] = str(uuid.uuid4())
        
        if "submitted_at" not in mapped_data or not mapped_data["submitted_at"]:
            mapped_data["submitted_at"] = datetime.utcnow().isoformat()
        
        if "form_title" not in mapped_data or not mapped_data["form_title"]:
            mapped_data["form_title"] = "Untitled Form"
        
        if "answers" not in mapped_data:
            # If no specific answer mapping, use the entire data as answers
            mapped_data["answers"] = data
        
        return mapped_data
    
    def convert_to_typeform_format(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert mapped data to Typeform webhook format for compatibility"""
        # Create Typeform-compatible structure
        typeform_data = {
            "event_id": str(uuid.uuid4()),
            "event_type": "form_response",
            "form_response": {
                "form_id": mapped_data.get("form_id", "custom_form"),
                "token": mapped_data.get("submission_id", str(uuid.uuid4())),
                "submitted_at": mapped_data.get("submitted_at", datetime.utcnow().isoformat()),
                "definition": {
                    "title": mapped_data.get("form_title", "Custom Form"),
                    "fields": []
                },
                "answers": []
            }
        }
        
        # Convert answers to Typeform format
        answers = mapped_data.get("answers", {})
        if isinstance(answers, dict):
            for key, value in answers.items():
                # Create field definition
                field = {
                    "id": f"field_{key}",
                    "title": key,
                    "type": "short_text"  # Default type
                }
                typeform_data["form_response"]["definition"]["fields"].append(field)
                
                # Create answer
                answer = {
                    "field": {
                        "id": f"field_{key}",
                        "type": "short_text"
                    },
                    "type": "text",
                    "text": str(value) if value is not None else ""
                }
                typeform_data["form_response"]["answers"].append(answer)
        elif isinstance(answers, list):
            # Handle list of answers
            for idx, value in enumerate(answers):
                field = {
                    "id": f"field_{idx}",
                    "title": f"Question {idx + 1}",
                    "type": "short_text"
                }
                typeform_data["form_response"]["definition"]["fields"].append(field)
                
                answer = {
                    "field": {
                        "id": f"field_{idx}",
                        "type": "short_text"
                    },
                    "type": "text",
                    "text": str(value) if value is not None else ""
                }
                typeform_data["form_response"]["answers"].append(answer)
        
        return typeform_data
    
    async def process(
        self,
        webhook_config: WebhookConfig,
        data: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process custom webhook data"""
        
        # Create webhook log entry
        log = WebhookLog(
            webhook_config_id=webhook_config.id,
            status="processing",
            request_body=data,
            ip_address=ip_address
        )
        self.db.add(log)
        self.db.commit()
        
        try:
            # Map fields using configuration
            mapped_data = self.map_fields(data, webhook_config.field_mappings)
            
            # Convert to Typeform format for processing
            typeform_data = self.convert_to_typeform_format(mapped_data)
            
            # Create TypeformWebhook object for compatibility
            webhook = TypeformWebhook(**typeform_data)
            
            # Extract form information
            form_response = webhook.form_response
            response_id = f"{form_response.get('token', '')}_{uuid.uuid4().hex[:8]}"
            
            # Store submission
            submission = FormSubmission(
                user_id=webhook_config.user_id,
                typeform_id=form_response.get("form_id", ""),
                form_title=form_response.get("definition", {}).get("title", "Custom Form"),
                response_id=response_id,
                submitted_at=datetime.fromisoformat(
                    form_response.get("submitted_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                ),
                answers=webhook.parse_answers(),
                dashboard_url=f"/dashboard/{response_id}"
            )
            self.db.add(submission)
            
            # Update log with success
            log.status = "success"
            log.response_body = {
                "submission_id": submission.id,
                "dashboard_url": submission.dashboard_url
            }
            
            self.db.commit()
            
            return {
                "status": "success",
                "submission_id": submission.id,
                "dashboard_url": submission.dashboard_url,
                "message": "Custom webhook processed successfully"
            }
            
        except Exception as e:
            # Update log with error
            log.status = "error"
            log.error_message = str(e)
            self.db.commit()
            
            raise e
    
    def test_mapping(
        self,
        webhook_config: WebhookConfig,
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test field mapping configuration with sample data"""
        try:
            # Map fields
            mapped_data = self.map_fields(test_data, webhook_config.field_mappings)
            
            # Convert to Typeform format
            typeform_data = self.convert_to_typeform_format(mapped_data)
            
            return {
                "success": True,
                "mapped_data": mapped_data,
                "typeform_format": typeform_data,
                "field_mapping_results": {
                    field: "✓ Mapped successfully" if field in mapped_data else "✗ Not found"
                    for field in ["form_title", "submission_id", "submitted_at", "answers"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "field_mapping_results": None
            }