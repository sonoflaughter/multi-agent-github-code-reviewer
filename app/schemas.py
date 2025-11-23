from pydantic import BaseModel
from typing import List, Optional, Any

class RequestReview(BaseModel):
    type: str
    repo: str
    pr_number: int
    requester: Optional[str] = None
    priority: Optional[str] = "normal"
    instructions: Optional[str] = ""

class AgentTask(BaseModel):
    id: str
    agent: str
    instruction: str
    priority: str = "normal"

class PlannerOutput(BaseModel):
    plan_id: str
    tasks: List[AgentTask]
    context_references: List[str] = []
