from app.agents.planner import simple_decompose
from app.schemas import RequestReview

def test_planner_review_decomposition():
    req = {"type": "review_pr", "pr_number": 1, "instructions": "Security focus"}
    plan = simple_decompose(req)
    assert plan.tasks[0].agent == "Tester"
    assert plan.tasks[1].agent == "Reviewer"
