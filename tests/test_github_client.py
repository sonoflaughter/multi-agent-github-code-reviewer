import pytest

from app.tools.github_client import GitHubClient


class FakeResp:
    def __init__(self, status_code, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text or ''

    def json(self):
        return self._json


@pytest.mark.asyncio
async def test_create_branch_and_pr_success(monkeypatch):
    client = GitHubClient("fake-token")

    # Prepare responses in the order _request will be called
    responses = [
        # GET ref
        FakeResp(200, {"object": {"sha": "base_sha"}}),
        # POST blob
        FakeResp(201, {"sha": "blob_sha"}),
        # GET commit
        FakeResp(200, {"tree": {"sha": "base_tree"}}),
        # POST tree
        FakeResp(201, {"sha": "tree_sha"}),
        # POST commit
        FakeResp(201, {"sha": "commit_sha"}),
        # POST ref
        FakeResp(201, {}),
        # POST pull
        FakeResp(201, {"number": 42, "html_url": "https://github.com/owner/repo/pull/42"}),
    ]

    async def fake_request(self, method, path, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(client, "_request", fake_request.__get__(client, GitHubClient))

    result = await client.create_branch_and_pr(
        repo="owner/repo",
        branch_name="agent/test-branch",
        base="main",
        title="Test PR",
        body="This is a test",
        changes={"src/example.py": "print('hello')"},
    )

    assert result["pr_number"] == 42
    assert result["branch"] == "agent/test-branch"
    assert "url" in result

    await client.close()


@pytest.mark.asyncio
async def test_comment_on_pr_success(monkeypatch):
    client = GitHubClient("fake-token")

    responses = [FakeResp(201, {"html_url": "https://github.com/owner/repo/pull/1#issuecomment-1"})]

    async def fake_request(self, method, path, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(client, "_request", fake_request.__get__(client, GitHubClient))

    res = await client.comment_on_pr("owner/repo", 1, "Nice PR")
    assert res.get("ok") is True
    assert "comment_url" in res

    await client.close()


@pytest.mark.asyncio
async def test_create_branch_and_pr_blob_failure(monkeypatch):
    client = GitHubClient("fake-token")

    responses = [
        # GET ref
        FakeResp(200, {"object": {"sha": "base_sha"}}),
        # POST blob fails
        FakeResp(400, {}, text="bad blob"),
    ]

    async def fake_request(self, method, path, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(client, "_request", fake_request.__get__(client, GitHubClient))

    result = await client.create_branch_and_pr(
        repo="owner/repo",
        branch_name="agent/test-branch",
        base="main",
        title="Test PR",
        body="This is a test",
        changes={"src/broken.py": "broken"},
    )

    assert isinstance(result, dict)
    assert result.get("error") == "failed_create_blob"

    await client.close()
