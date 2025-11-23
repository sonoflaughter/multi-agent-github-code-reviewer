import uuid
from typing import List
from ..schemas import PlannerOutput, AgentTask

def simple_decompose(request: dict) -> PlannerOutput:
    """
    Very small planner that decides which agents to call.
    For `review_pr` we'll call Reviewer + Tester.
    For `auto_fix` we'll call Planner -> Coder -> Tester -> Reviewer
    """
    req_type = request.get("type")
    tasks: List[AgentTask] = []
    plan_id = str(uuid.uuid4())
    if req_type == "review_pr":
        tasks.append(AgentTask(id="t1", agent="Tester", instruction=f"Run tests for PR #{request.get('pr_number')}", priority="high"))
        tasks.append(AgentTask(id="t2", agent="Reviewer", instruction=f"Review PR #{request.get('pr_number')} focusing on: {request.get('instructions', '')}", priority="high"))
    elif req_type == "auto_fix":
        tasks.append(AgentTask(id="t1", agent="Coder", instruction=f"Create fix for issue: {request.get('instructions')}", priority="high"))
        tasks.append(AgentTask(id="t2", agent="Tester", instruction="Run tests for the new branch", priority="high"))
        tasks.append(AgentTask(id="t3", agent="Reviewer", instruction="Review the fix", priority="high"))
    else:
        tasks.append(AgentTask(id="t1", agent="Reviewer", instruction="Generic review", priority="low"))

    return PlannerOutput(plan_id=plan_id, tasks=tasks, context_references=[])
