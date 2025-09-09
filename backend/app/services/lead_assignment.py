"""
Lead Assignment Service for FA-50
Service for managing sales team collaboration and lead distribution
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from uuid import UUID
import random

from app.models.team_collaboration import (
    Team,
    TeamMember,
    LeadAssignment,
    LeadActivity,
    AssignmentRule,
    TeamRole,
    AssignmentMethod,
    LeadStatus
)
from app.models.form import FormSubmission
from app.models.lead_score import LeadScore
from app.models.user import User


class LeadAssignmentService:
    """Service for managing lead assignments and team collaboration"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_team(
        self,
        name: str,
        manager_id: UUID,
        settings: Optional[Dict] = None
    ) -> Team:
        """Create a new sales team"""
        team = Team(
            name=name,
            manager_id=manager_id,
            settings=settings or {
                'auto_assignment': True,
                'assignment_method': 'round_robin',
                'sla_hours': 24,
                'notification_preferences': {
                    'new_lead': True,
                    'sla_warning': True,
                    'conversion': True
                }
            }
        )
        
        self.db.add(team)
        
        # Add manager as team member
        manager_member = TeamMember(
            team_id=team.id,
            user_id=manager_id,
            role=TeamRole.MANAGER,
            max_capacity=100
        )
        
        self.db.add(manager_member)
        self.db.commit()
        
        return team
    
    def add_team_member(
        self,
        team_id: UUID,
        user_id: UUID,
        role: TeamRole,
        territories: Optional[List[str]] = None,
        expertise: Optional[List[str]] = None,
        capacity: int = 50
    ) -> TeamMember:
        """Add a member to a team"""
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            territories=territories or [],
            expertise=expertise or [],
            max_capacity=capacity
        )
        
        self.db.add(member)
        self.db.commit()
        
        return member
    
    def assign_lead(
        self,
        lead_id: UUID,
        team_id: UUID,
        manual_assignee: Optional[UUID] = None,
        assignment_reason: Optional[str] = None
    ) -> LeadAssignment:
        """Assign a lead to a team member"""
        # Get team and lead data
        team = self.db.query(Team).filter(Team.id == team_id).first()
        lead = self.db.query(FormSubmission).filter(FormSubmission.id == lead_id).first()
        
        if not team or not lead:
            raise ValueError("Team or lead not found")
        
        # Get lead score
        lead_score = self.db.query(LeadScore).filter(
            LeadScore.submission_id == lead_id
        ).first()
        
        # Determine assignee
        if manual_assignee:
            assignee_id = manual_assignee
            method = AssignmentMethod.MANUAL
        else:
            assignee_id, method, reason = self._determine_assignee(
                team, lead, lead_score
            )
            assignment_reason = reason
        
        # Create assignment
        assignment = LeadAssignment(
            lead_id=lead_id,
            team_id=team_id,
            assigned_to=assignee_id,
            assignment_method=method,
            assignment_reason=assignment_reason,
            lead_score=lead_score.final_score if lead_score else 0,
            lead_data_snapshot=lead.form_data,
            priority=self._calculate_priority(lead_score),
            sla_deadline=datetime.utcnow() + timedelta(hours=team.settings.get('sla_hours', 24))
        )
        
        self.db.add(assignment)
        
        # Update member capacity
        member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == assignee_id
            )
        ).first()
        
        if member:
            member.current_capacity += 1
            member.leads_assigned_today += 1
            member.total_leads_assigned += 1
            member.last_assignment_at = datetime.utcnow()
        
        # Create initial activity
        activity = LeadActivity(
            assignment_id=assignment.id,
            user_id=assignee_id,
            activity_type='assignment',
            activity_data={'method': method.value},
            description=f"Lead assigned via {method.value}"
        )
        
        self.db.add(activity)
        self.db.commit()
        
        # Send notification (would integrate with notification service)
        self._notify_assignee(assignee_id, lead, assignment)
        
        return assignment
    
    def _determine_assignee(
        self,
        team: Team,
        lead: FormSubmission,
        lead_score: Optional[LeadScore]
    ) -> tuple[UUID, AssignmentMethod, str]:
        """Determine who should be assigned the lead"""
        # Get available team members
        available_members = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team.id,
                TeamMember.is_available == True,
                TeamMember.current_capacity < TeamMember.max_capacity,
                TeamMember.leads_assigned_today < TeamMember.daily_lead_limit
            )
        ).all()
        
        if not available_members:
            # Fallback to manager
            return team.manager_id, AssignmentMethod.MANUAL, "No available reps"
        
        # Check assignment rules
        rules = self.db.query(AssignmentRule).filter(
            and_(
                AssignmentRule.team_id == team.id,
                AssignmentRule.is_active == True
            )
        ).order_by(AssignmentRule.priority.desc()).all()
        
        for rule in rules:
            if self._matches_rule(lead, lead_score, rule):
                assignee = self._get_assignee_from_rule(rule, available_members)
                if assignee:
                    return assignee, AssignmentMethod(rule.rule_type), f"Matched rule: {rule.name}"
        
        # Default assignment method from team settings
        method = team.settings.get('assignment_method', 'round_robin')
        
        if method == 'round_robin':
            return self._round_robin_assignment(available_members)
        elif method == 'score_based' and lead_score:
            return self._score_based_assignment(available_members, lead_score)
        elif method == 'capacity':
            return self._capacity_based_assignment(available_members)
        else:
            # Random assignment as fallback
            member = random.choice(available_members)
            return member.user_id, AssignmentMethod.ROUND_ROBIN, "Random selection"
    
    def _round_robin_assignment(
        self,
        members: List[TeamMember]
    ) -> tuple[UUID, AssignmentMethod, str]:
        """Assign using round-robin method"""
        # Get member with oldest last assignment
        member = min(members, key=lambda m: m.last_assignment_at or datetime.min)
        return member.user_id, AssignmentMethod.ROUND_ROBIN, "Round-robin assignment"
    
    def _score_based_assignment(
        self,
        members: List[TeamMember],
        lead_score: LeadScore
    ) -> tuple[UUID, AssignmentMethod, str]:
        """Assign based on lead score"""
        score = lead_score.final_score
        
        # Hot leads to senior reps
        if score >= 80:
            senior_members = [m for m in members if m.role in [TeamRole.SENIOR_REP, TeamRole.MANAGER]]
            if senior_members:
                member = min(senior_members, key=lambda m: m.current_capacity)
                return member.user_id, AssignmentMethod.SCORE_BASED, f"Hot lead (score: {score})"
        
        # Warm leads to regular reps
        elif score >= 60:
            regular_members = [m for m in members if m.role in [TeamRole.REP, TeamRole.SENIOR_REP]]
            if regular_members:
                member = min(regular_members, key=lambda m: m.current_capacity)
                return member.user_id, AssignmentMethod.SCORE_BASED, f"Warm lead (score: {score})"
        
        # Cold leads to junior reps or least loaded
        member = min(members, key=lambda m: m.current_capacity)
        return member.user_id, AssignmentMethod.SCORE_BASED, f"Cold lead (score: {score})"
    
    def _capacity_based_assignment(
        self,
        members: List[TeamMember]
    ) -> tuple[UUID, AssignmentMethod, str]:
        """Assign to member with most available capacity"""
        member = min(members, key=lambda m: m.current_capacity / m.max_capacity)
        capacity_percent = (member.current_capacity / member.max_capacity) * 100
        return member.user_id, AssignmentMethod.CAPACITY, f"Lowest capacity ({capacity_percent:.0f}%)"
    
    def _matches_rule(
        self,
        lead: FormSubmission,
        lead_score: Optional[LeadScore],
        rule: AssignmentRule
    ) -> bool:
        """Check if lead matches assignment rule"""
        conditions = rule.conditions or {}
        
        # Score-based rules
        if rule.rule_type == 'score_based' and lead_score:
            score = lead_score.final_score
            if 'score_min' in conditions and score < conditions['score_min']:
                return False
            if 'score_max' in conditions and score > conditions['score_max']:
                return False
            return True
        
        # Territory-based rules
        elif rule.rule_type == 'territory':
            field = conditions.get('field')
            values = conditions.get('values', [])
            if field and field in lead.form_data:
                return lead.form_data[field] in values
        
        # Field-based rules
        elif rule.rule_type == 'field_match':
            field = conditions.get('field')
            value = conditions.get('value')
            if field and field in lead.form_data:
                return str(lead.form_data[field]).lower() == str(value).lower()
        
        return False
    
    def _get_assignee_from_rule(
        self,
        rule: AssignmentRule,
        available_members: List[TeamMember]
    ) -> Optional[UUID]:
        """Get assignee based on rule target"""
        target = rule.assign_to_target or {}
        
        if rule.assign_to_type == 'specific_user':
            user_id = target.get('user_id')
            if user_id and any(m.user_id == UUID(user_id) for m in available_members):
                return UUID(user_id)
        
        elif rule.assign_to_type == 'role':
            role = TeamRole(target.get('role'))
            role_members = [m for m in available_members if m.role == role]
            if role_members:
                return min(role_members, key=lambda m: m.current_capacity).user_id
        
        return None
    
    def _calculate_priority(self, lead_score: Optional[LeadScore]) -> int:
        """Calculate lead priority"""
        if not lead_score:
            return 0
        
        if lead_score.final_score >= 80:
            return 3  # Urgent
        elif lead_score.final_score >= 60:
            return 2  # High
        elif lead_score.final_score >= 40:
            return 1  # Medium
        return 0  # Low
    
    def _notify_assignee(
        self,
        user_id: UUID,
        lead: FormSubmission,
        assignment: LeadAssignment
    ):
        """Send notification to assigned user"""
        # This would integrate with a notification service
        # For now, just log
        print(f"Notification: Lead {lead.id} assigned to user {user_id}")
    
    def update_lead_status(
        self,
        assignment_id: UUID,
        new_status: LeadStatus,
        user_id: UUID,
        notes: Optional[str] = None
    ):
        """Update lead assignment status"""
        assignment = self.db.query(LeadAssignment).filter(
            LeadAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        old_status = assignment.status
        assignment.status = new_status
        
        # Update timestamps
        if new_status == LeadStatus.CONTACTED and not assignment.first_contact_at:
            assignment.first_contact_at = datetime.utcnow()
        elif new_status == LeadStatus.QUALIFIED:
            assignment.qualified_at = datetime.utcnow()
        elif new_status == LeadStatus.CONVERTED:
            assignment.converted_at = datetime.utcnow()
            # Update member stats
            self._update_member_conversion_stats(assignment.assigned_to)
        elif new_status == LeadStatus.LOST:
            assignment.lost_at = datetime.utcnow()
        
        assignment.last_contact_at = datetime.utcnow()
        
        # Create activity
        activity = LeadActivity(
            assignment_id=assignment_id,
            user_id=user_id,
            activity_type='status_change',
            activity_data={
                'old_status': old_status.value,
                'new_status': new_status.value
            },
            description=notes
        )
        
        self.db.add(activity)
        self.db.commit()
    
    def _update_member_conversion_stats(self, user_id: UUID):
        """Update team member conversion statistics"""
        member = self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id
        ).first()
        
        if member:
            member.total_conversions += 1
            if member.total_leads_assigned > 0:
                member.conversion_rate = member.total_conversions / member.total_leads_assigned
    
    def get_team_performance(
        self,
        team_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """Get team performance metrics"""
        query = self.db.query(LeadAssignment).filter(
            LeadAssignment.team_id == team_id
        )
        
        if date_from:
            query = query.filter(LeadAssignment.assigned_at >= date_from)
        if date_to:
            query = query.filter(LeadAssignment.assigned_at <= date_to)
        
        assignments = query.all()
        
        # Calculate metrics
        total_leads = len(assignments)
        contacted = sum(1 for a in assignments if a.status in [LeadStatus.CONTACTED, LeadStatus.QUALIFIED, LeadStatus.CONVERTED])
        qualified = sum(1 for a in assignments if a.status in [LeadStatus.QUALIFIED, LeadStatus.CONVERTED])
        converted = sum(1 for a in assignments if a.status == LeadStatus.CONVERTED)
        
        # Member performance
        member_stats = {}
        members = self.db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
        
        for member in members:
            member_assignments = [a for a in assignments if a.assigned_to == member.user_id]
            member_conversions = sum(1 for a in member_assignments if a.status == LeadStatus.CONVERTED)
            
            member_stats[str(member.user_id)] = {
                'name': member.user.name if member.user else 'Unknown',
                'role': member.role.value,
                'leads': len(member_assignments),
                'conversions': member_conversions,
                'conversion_rate': member_conversions / len(member_assignments) if member_assignments else 0,
                'current_capacity': f"{member.current_capacity}/{member.max_capacity}"
            }
        
        return {
            'total_leads': total_leads,
            'contacted': contacted,
            'qualified': qualified,
            'converted': converted,
            'conversion_rate': converted / total_leads if total_leads > 0 else 0,
            'contact_rate': contacted / total_leads if total_leads > 0 else 0,
            'member_performance': member_stats,
            'top_performer': max(member_stats.items(), key=lambda x: x[1]['conversions'])[0] if member_stats else None
        }