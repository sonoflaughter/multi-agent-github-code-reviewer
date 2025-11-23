import httpx
from typing import Any, Dict

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self._client = httpx.AsyncClient(headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }, timeout=30.0)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{GITHUB_API}{path}"
        resp = await self._client.request(method, url, **kwargs)
        return resp

    async def create_branch_and_pr(self, repo: str, branch_name: str, base: str, title: str, body: str, changes: Dict[str, str]) -> Dict[str, Any]:
        """Create a branch from `base`, commit `changes`, and open a PR.

        `repo` should be "owner/name". `changes` is a mapping path->content.
        Returns a dict with PR number and url on success.
        """
        owner, name = repo.split("/")

        # 1) Get base ref
        resp = await self._request("GET", f"/repos/{owner}/{name}/git/refs/heads/{base}")
        if resp.status_code != 200:
            return {"error": "failed_get_base_ref", "status_code": resp.status_code, "details": resp.text}
        base_ref = resp.json()
        base_sha = base_ref.get("object", {}).get("sha")

        # 2) Create blobs for files
        blobs = {}
        for path, content in changes.items():
            payload = {"content": content, "encoding": "utf-8"}
            r = await self._request("POST", f"/repos/{owner}/{name}/git/blobs", json=payload)
            if r.status_code not in (200, 201):
                return {"error": "failed_create_blob", "path": path, "status_code": r.status_code, "details": r.text}
            blobs[path] = r.json().get("sha")

        # 3) Get base commit to obtain tree
        r = await self._request("GET", f"/repos/{owner}/{name}/git/commits/{base_sha}")
        if r.status_code != 200:
            return {"error": "failed_get_base_commit", "status_code": r.status_code, "details": r.text}
        base_commit = r.json()
        base_tree = base_commit.get("tree", {}).get("sha")

        # 4) Create tree
        tree_entries = []
        for path, sha in blobs.items():
            tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": sha})
        tree_payload = {"base_tree": base_tree, "tree": tree_entries}
        r = await self._request("POST", f"/repos/{owner}/{name}/git/trees", json=tree_payload)
        if r.status_code not in (200, 201):
            return {"error": "failed_create_tree", "status_code": r.status_code, "details": r.text}
        tree_sha = r.json().get("sha")

        # 5) Create commit
        commit_payload = {"message": title, "tree": tree_sha, "parents": [base_sha]}
        r = await self._request("POST", f"/repos/{owner}/{name}/git/commits", json=commit_payload)
        if r.status_code not in (200, 201):
            return {"error": "failed_create_commit", "status_code": r.status_code, "details": r.text}
        commit_sha = r.json().get("sha")

        # 6) Create ref (new branch)
        ref_payload = {"ref": f"refs/heads/{branch_name}", "sha": commit_sha}
        r = await self._request("POST", f"/repos/{owner}/{name}/git/refs", json=ref_payload)
        if r.status_code not in (200, 201):
            # If branch already exists, return error info
            return {"error": "failed_create_ref", "status_code": r.status_code, "details": r.text}

        # 7) Open PR
        pr_payload = {"title": title, "head": branch_name, "base": base, "body": body}
        r = await self._request("POST", f"/repos/{owner}/{name}/pulls", json=pr_payload)
        if r.status_code not in (200, 201):
            return {"error": "failed_create_pr", "status_code": r.status_code, "details": r.text}
        pr = r.json()
        return {"pr_number": pr.get("number"), "url": pr.get("html_url"), "branch": branch_name}

    async def comment_on_pr(self, repo: str, pr_number: int, body: str) -> Dict[str, Any]:
        owner, name = repo.split("/")
        payload = {"body": body}
        r = await self._request("POST", f"/repos/{owner}/{name}/issues/{pr_number}/comments", json=payload)
        if r.status_code not in (200, 201):
            return {"error": "failed_comment", "status_code": r.status_code, "details": r.text}
        return {"ok": True, "comment_url": r.json().get("html_url")}

    async def close(self):
        await self._client.aclose()
