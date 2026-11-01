from pydantic import BaseModel


class RelationshipIntelligenceResponse(BaseModel):
    total_leads: int
    healthy_relationships: int
    overdue_followups: int
    engagement_score: int
    recommendations: list[str]
