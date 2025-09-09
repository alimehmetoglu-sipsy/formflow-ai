"""
Aggregation Engine Service for FA-44 Epic
Handles data aggregation from multiple form sources
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import pandas as pd
import numpy as np
from collections import defaultdict
import asyncio
import json
from uuid import UUID

from app.models.multi_form_dashboard import (
    MultiFormDashboard, 
    MultiFormMapping,
    AggregationJob
)
from app.models.form_submission import FormSubmission
from app.core.logging import logger
from app.core.cache import cache_manager


class AggregationEngine:
    """
    Engine for aggregating data from multiple form sources
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = cache_manager
        
    async def aggregate_dashboard_data(
        self,
        dashboard_id: UUID,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Main method to aggregate data for a multi-form dashboard
        """
        # Get dashboard configuration
        dashboard = self.db.query(MultiFormDashboard).filter_by(id=dashboard_id).first()
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        # Check cache if not forcing refresh
        if not force_refresh and dashboard.cached_data:
            cache_age = datetime.utcnow() - dashboard.cache_updated_at
            if cache_age < timedelta(hours=1):  # Cache valid for 1 hour
                logger.info(f"Using cached data for dashboard {dashboard_id}")
                return dashboard.cached_data
        
        # Create aggregation job
        job = self._create_aggregation_job(dashboard_id)
        
        try:
            # Fetch data from all sources
            logger.info(f"Starting aggregation for dashboard {dashboard_id}")
            all_data = await self._fetch_all_form_data(dashboard)
            
            # Apply aggregation method
            aggregated_data = self._apply_aggregation_method(
                all_data,
                dashboard.aggregation_config
            )
            
            # Apply filters
            filtered_data = self._apply_filters(
                aggregated_data,
                dashboard.filter_config
            )
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                filtered_data,
                dashboard.analytics_config
            )
            
            # Prepare final result
            result = {
                "data": filtered_data,
                "metrics": metrics,
                "metadata": {
                    "total_records": len(filtered_data),
                    "sources": len(all_data),
                    "aggregation_method": dashboard.aggregation_config.get("aggregation_method"),
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            
            # Update cache
            dashboard.cached_data = result
            dashboard.cache_updated_at = datetime.utcnow()
            
            # Complete job
            self._complete_aggregation_job(job, "completed", result)
            
            self.db.commit()
            
            logger.info(f"Aggregation completed for dashboard {dashboard_id}")
            return result
            
        except Exception as e:
            logger.error(f"Aggregation failed for dashboard {dashboard_id}: {str(e)}")
            self._complete_aggregation_job(job, "failed", error_message=str(e))
            raise
    
    async def _fetch_all_form_data(
        self,
        dashboard: MultiFormDashboard
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from all form sources
        """
        all_data = []
        form_mappings = self.db.query(MultiFormMapping).filter_by(
            dashboard_id=dashboard.id,
            is_active=True
        ).all()
        
        # Fetch data in parallel
        tasks = []
        for mapping in form_mappings:
            tasks.append(self._fetch_form_data(mapping))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch data from form {form_mappings[idx].id}: {result}")
                continue
            all_data.append({
                "mapping_id": str(form_mappings[idx].id),
                "form_type": form_mappings[idx].form_type,
                "form_title": form_mappings[idx].form_title,
                "data": result,
                "weight": form_mappings[idx].weight,
                "priority": form_mappings[idx].priority
            })
        
        return all_data
    
    async def _fetch_form_data(self, mapping: MultiFormMapping) -> List[Dict]:
        """
        Fetch data from a single form source
        """
        # Query form submissions
        query = self.db.query(FormSubmission)
        
        if mapping.form_submission_id:
            query = query.filter_by(id=mapping.form_submission_id)
        elif mapping.form_external_id:
            query = query.filter_by(typeform_id=mapping.form_external_id)
        
        submissions = query.all()
        
        # Transform data according to field mappings
        transformed_data = []
        for submission in submissions:
            record = self._transform_record(
                submission.answers,
                mapping.field_mappings or {}
            )
            record["_source_id"] = str(submission.id)
            record["_submitted_at"] = submission.submitted_at.isoformat()
            transformed_data.append(record)
        
        return transformed_data
    
    def _transform_record(
        self,
        raw_data: Dict,
        field_mappings: Dict[str, str]
    ) -> Dict:
        """
        Transform a record according to field mappings
        """
        if not field_mappings:
            return raw_data
        
        transformed = {}
        for target_field, source_field in field_mappings.items():
            # Handle nested fields with dot notation
            value = self._get_nested_value(raw_data, source_field)
            if value is not None:
                transformed[target_field] = value
        
        # Include unmapped fields with prefix
        for key, value in raw_data.items():
            if key not in field_mappings.values():
                transformed[f"raw_{key}"] = value
        
        return transformed
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """
        Get nested value from dict using dot notation
        """
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def _apply_aggregation_method(
        self,
        all_data: List[Dict],
        config: Dict
    ) -> List[Dict]:
        """
        Apply the specified aggregation method to combine data
        """
        method = config.get("aggregation_method", "union")
        
        if method == "union":
            return self._aggregate_union(all_data)
        elif method == "intersection":
            return self._aggregate_intersection(all_data)
        elif method == "weighted":
            return self._aggregate_weighted(all_data)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    def _aggregate_union(self, all_data: List[Dict]) -> List[Dict]:
        """
        Union aggregation - combine all records
        """
        combined = []
        
        for source in all_data:
            for record in source["data"]:
                record["_form_source"] = source["form_title"]
                record["_form_type"] = source["form_type"]
                combined.append(record)
        
        return combined
    
    def _aggregate_intersection(self, all_data: List[Dict]) -> List[Dict]:
        """
        Intersection aggregation - only common records
        """
        if not all_data:
            return []
        
        # Find common keys across all sources
        common_keys = set()
        for source in all_data:
            if not source["data"]:
                continue
            
            if not common_keys:
                common_keys = set(source["data"][0].keys())
            else:
                common_keys &= set(source["data"][0].keys())
        
        # Combine records with common fields only
        combined = []
        for source in all_data:
            for record in source["data"]:
                filtered_record = {
                    k: v for k, v in record.items() 
                    if k in common_keys or k.startswith("_")
                }
                filtered_record["_form_source"] = source["form_title"]
                combined.append(filtered_record)
        
        return combined
    
    def _aggregate_weighted(self, all_data: List[Dict]) -> List[Dict]:
        """
        Weighted aggregation - apply weights to numeric fields
        """
        combined = []
        
        for source in all_data:
            weight = source.get("weight", 1.0)
            
            for record in source["data"]:
                weighted_record = {}
                
                for key, value in record.items():
                    if isinstance(value, (int, float)) and not key.startswith("_"):
                        weighted_record[key] = value * weight
                    else:
                        weighted_record[key] = value
                
                weighted_record["_form_source"] = source["form_title"]
                weighted_record["_weight"] = weight
                combined.append(weighted_record)
        
        return combined
    
    def _apply_filters(
        self,
        data: List[Dict],
        filter_config: Optional[Dict]
    ) -> List[Dict]:
        """
        Apply filters to the aggregated data
        """
        if not filter_config or not data:
            return data
        
        df = pd.DataFrame(data)
        
        # Apply date range filter
        if "date_range" in filter_config:
            date_range = filter_config["date_range"]
            if "_submitted_at" in df.columns:
                df["_submitted_at"] = pd.to_datetime(df["_submitted_at"])
                
                if "start" in date_range:
                    start_date = pd.to_datetime(date_range["start"])
                    df = df[df["_submitted_at"] >= start_date]
                
                if "end" in date_range:
                    end_date = pd.to_datetime(date_range["end"])
                    df = df[df["_submitted_at"] <= end_date]
        
        # Apply custom filters
        if "custom_filters" in filter_config:
            for filter_rule in filter_config["custom_filters"]:
                field = filter_rule.get("field")
                operator = filter_rule.get("operator")
                value = filter_rule.get("value")
                
                if field in df.columns:
                    df = self._apply_filter_operator(df, field, operator, value)
        
        return df.to_dict("records")
    
    def _apply_filter_operator(
        self,
        df: pd.DataFrame,
        field: str,
        operator: str,
        value: Any
    ) -> pd.DataFrame:
        """
        Apply a single filter operator
        """
        if operator == "=":
            return df[df[field] == value]
        elif operator == "!=":
            return df[df[field] != value]
        elif operator == ">":
            return df[df[field] > value]
        elif operator == ">=":
            return df[df[field] >= value]
        elif operator == "<":
            return df[df[field] < value]
        elif operator == "<=":
            return df[df[field] <= value]
        elif operator == "contains":
            return df[df[field].str.contains(value, na=False)]
        elif operator == "in":
            return df[df[field].isin(value)]
        else:
            logger.warning(f"Unknown filter operator: {operator}")
            return df
    
    def _calculate_metrics(
        self,
        data: List[Dict],
        analytics_config: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate metrics and KPIs
        """
        if not analytics_config or not data:
            return {}
        
        df = pd.DataFrame(data)
        metrics = {}
        
        # Calculate defined metrics
        if "metrics" in analytics_config:
            for metric_def in analytics_config["metrics"]:
                name = metric_def["name"]
                formula = metric_def["formula"]
                
                try:
                    value = self._evaluate_formula(df, formula)
                    metrics[name] = {
                        "value": value,
                        "formula": formula,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Failed to calculate metric {name}: {e}")
                    metrics[name] = {
                        "value": None,
                        "error": str(e)
                    }
        
        # Calculate KPIs
        if "kpis" in analytics_config:
            for kpi_def in analytics_config["kpis"]:
                name = kpi_def["name"]
                formula = kpi_def["formula"]
                target = kpi_def.get("target")
                
                try:
                    value = self._evaluate_formula(df, formula)
                    metrics[f"kpi_{name}"] = {
                        "value": value,
                        "target": target,
                        "achievement": (value / target * 100) if target else None,
                        "formula": formula
                    }
                except Exception as e:
                    logger.error(f"Failed to calculate KPI {name}: {e}")
        
        # Add basic statistics
        metrics["_statistics"] = {
            "total_records": len(df),
            "unique_sources": df["_form_source"].nunique() if "_form_source" in df else 0,
            "date_range": {
                "start": df["_submitted_at"].min() if "_submitted_at" in df else None,
                "end": df["_submitted_at"].max() if "_submitted_at" in df else None
            }
        }
        
        return metrics
    
    def _evaluate_formula(self, df: pd.DataFrame, formula: str) -> float:
        """
        Evaluate a metric formula
        Safe evaluation of simple formulas like sum(field), avg(field), count()
        """
        # Basic formula patterns
        if formula.startswith("sum(") and formula.endswith(")"):
            field = formula[4:-1]
            return df[field].sum() if field in df else 0
        
        elif formula.startswith("avg(") and formula.endswith(")"):
            field = formula[4:-1]
            return df[field].mean() if field in df else 0
        
        elif formula.startswith("count(") and formula.endswith(")"):
            field = formula[6:-1]
            if field == "*":
                return len(df)
            return df[field].count() if field in df else 0
        
        elif formula.startswith("min(") and formula.endswith(")"):
            field = formula[4:-1]
            return df[field].min() if field in df else 0
        
        elif formula.startswith("max(") and formula.endswith(")"):
            field = formula[4:-1]
            return df[field].max() if field in df else 0
        
        elif "/" in formula:
            # Simple division for rates
            parts = formula.split("/")
            if len(parts) == 2:
                numerator = self._evaluate_formula(df, parts[0].strip())
                denominator = self._evaluate_formula(df, parts[1].strip())
                return numerator / denominator if denominator != 0 else 0
        
        # Try to get field value directly
        if formula in df.columns:
            return df[formula].sum()
        
        raise ValueError(f"Unsupported formula: {formula}")
    
    def _create_aggregation_job(self, dashboard_id: UUID) -> AggregationJob:
        """
        Create an aggregation job record
        """
        job = AggregationJob(
            dashboard_id=dashboard_id,
            job_type="full_refresh",
            status="processing",
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        return job
    
    def _complete_aggregation_job(
        self,
        job: AggregationJob,
        status: str,
        result: Dict = None,
        error_message: str = None
    ):
        """
        Complete an aggregation job
        """
        job.status = status
        job.completed_at = datetime.utcnow()
        
        if result:
            job.result_summary = {
                "total_records": result.get("metadata", {}).get("total_records"),
                "sources": result.get("metadata", {}).get("sources")
            }
        
        if error_message:
            job.error_message = error_message
        
        self.db.commit()