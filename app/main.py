import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from .config import settings
from .tools.github_client import GitHubClient
from .tools.vector_store import VectorStoreMock
from .agents.planner import simple_decompose
from .agents.tester import TesterAgent
from .agents.reviewer import ReviewerAgent
from .agents.coder import CoderAgent
from .schemas import RequestReview

app = FastAPI(title="Multi-Agent Code Reviewer")

# init clients
gh = GitHubClient(settings.github_token)
vector_store = VectorStoreMock()
tester = TesterAgent(ci_runner_url=settings.ci_runner_url)
reviewer = ReviewerAgent()
coder = CoderAgent(gh)

@app.post("/v1/request-review")
async def request_review(payload: RequestReview, background_tasks: BackgroundTasks):
    # Synchronous planner decomposition
    plan = simple_decompose(payload.dict())
    # Kick off background tasks for each agent
    for task in plan.tasks:
        if task.agent == "Tester":
            background_tasks.add_task(_run_tests_and_comment, payload.repo, payload.pr_number, task.instruction)
        elif task.agent == "Reviewer":
            background_tasks.add_task(_run_review_and_comment, payload.repo, payload.pr_number, task.instruction)
        elif task.agent == "Coder":
            background_tasks.add_task(_coder_create_fix, payload.repo, payload.instructions)
    return {"request_id": plan.plan_id, "status": "queued", "assigned_agents": [t.agent for t in plan.tasks]}

@app.post("/webhook/github")
async def github_webhook(req: Request):
    event = req.headers.get("x-github-event", "unknown")
    payload = await req.json()
    # For prototype: handle PR opened event
    if event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        repo = payload.get("repository", {}).get("full_name")
        if action in ("opened", "synchronize", "reopened"):
            # schedule reviewer + tester
            asyncio.create_task(_run_tests_and_comment(repo, pr_number, "Webhook-triggered test run"))
            asyncio.create_task(_run_review_and_comment(repo, pr_number, "Webhook-triggered review"))
    return {"ok": True}

# Agent task implementations

async def _run_tests_and_comment(repo: str, pr_number: int, instruction: str):
    report = await tester.run_tests_for_pr(repo, pr_number)
    # store report in vector store as metadata (demo)
    vector_store.upsert(f"pr-{pr_number}", [0.0]*8, {"report": report})
    # Optionally, create summary comment
    body = f"Automated test report for PR #{pr_number}: {report['status']}\n\nLogs:\n{report['logs']}"
    await gh.comment_on_pr(repo, pr_number, body)

async def _run_review_and_comment(repo: str, pr_number: int, instruction: str):
    # get test report from vector store if present
    found = vector_store.query([], top_k=1)
    test_report = None
    if found:
        test_report = found[0]["meta"].get("report")
    review = await reviewer.review_pr(repo, pr_number, diff=None, test_report=test_report)
    comment_body = f"Automated review summary: {review['summary']}\n\n"
    for c in review["comments"]:
        comment_body += f"- {c.get('severity')} — {c.get('comment')}\n"
    await gh.comment_on_pr(repo, pr_number, comment_body)

async def _coder_create_fix(repo: str, instructions: str):
    # simple placeholder
    pr = await coder.create_fix_pr(repo, base="main", files={"src/example.py": "# example fix"}, title="Auto-fix", body=instructions)
    return pr

# graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    await gh.close()
