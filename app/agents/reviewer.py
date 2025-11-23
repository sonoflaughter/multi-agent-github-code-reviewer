from typing import Dict, Any
import json

class ReviewerAgent:
    def __init__(self):
        pass

    async def review_pr(self, repo: str, pr_number: int, diff: str | None = None, test_report: Dict | None = None) -> Dict[str, Any]:
        """
        Basic heuristic reviewer that returns structured comment suggestions
        """
        summary = f"Automated review for PR #{pr_number}."
        comments = []
        if test_report and test_report.get("status") != "passed":
            comments.append({"file": None, "line": None, "comment": "Tests failing — ensure fixes pass tests", "severity": "blocker"})
        else:
            comments.append({"file": "src/example.py", "line": 10, "comment": "Consider using a guard clause for readability", "severity": "suggestion"})

        approve = test_report and test_report.get("status") == "passed"
        return {"summary": summary, "comments": comments, "approve": approve}
