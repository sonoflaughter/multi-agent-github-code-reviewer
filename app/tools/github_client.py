import os
import httpx
from typing import Any

GITHUB_API = "https://api.github.com"

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self._client = httpx.AsyncClient(headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }, timeout=30.0)

    async def create_branch_and_pr(self, repo: str, branch_name: str, base: str, title: str, body: str, changes: dict) -> dict:
        # For a prototype we just return a fake PR response; integrate with commits API later.
        # `changes` expected {path: content}
        return {"pr_number": 999, "url": f"https://github.com/{repo}/pull/999", "branch": branch_name}

    async def comment_on_pr(self, repo: str, pr_number: int, body: str) -> dict:
        resp = {"ok": True, "pr": pr_number}
        return resp

    async def close(self):
        await self._client.aclose()
