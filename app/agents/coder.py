from typing import Dict, Any
from ..tools.github_client import GitHubClient

class CoderAgent:
    def __init__(self, gh: GitHubClient):
        self.gh = gh

    async def create_fix_pr(self, repo: str, base: str, files: Dict[str, str], title: str, body: str):
        branch = f"agent/auto-fix-{int(__import__('time').time())}"
        # In real impl: create blobs, tree, commit, and ref.
        pr = await self.gh.create_branch_and_pr(repo=repo, branch_name=branch, base=base, title=title, body=body, changes=files)
        return pr
