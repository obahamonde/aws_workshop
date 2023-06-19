from typing import Optional

from ._config import cfg
from .client import ApiClient


class GithubClient(ApiClient):
    def __init__(self, token: Optional[str] = None):
        if token is None:
            self.headers = {
                "Authorization": "token " + cfg.GH_API_TOKEN,
                "Accept": "application/vnd.github.v3+json",
            }
        else:
            self.headers = {
                "Authorization": "token " + token,
                "Accept": "application/vnd.github.v3+json",
            }
        super().__init__()
        self.base_url = "https://api.github.com"

    async def get(self, url: str):
        return await self.fetch(self.base_url + url, headers=self.headers)

    async def post(self, url: str, json: dict):
        return await self.fetch(
            self.base_url + url, method="POST", headers=self.headers, json=json
        )

    async def put(self, url: str, json: dict):
        return await self.fetch(
            self.base_url + url, method="PUT", headers=self.headers, json=json
        )

    async def delete(self, url: str):
        return await self.fetch(
            self.base_url + url, method="DELETE", headers=self.headers
        )

    async def patch(self, url: str, json: dict):
        return await self.fetch(
            self.base_url + url, method="PATCH", headers=self.headers, json=json
        )

    async def head(self, url: str):
        return await self.fetch(
            self.base_url + url, method="HEAD", headers=self.headers
        )

    async def options(self, url: str):
        return await self.fetch(
            self.base_url + url, method="OPTIONS", headers=self.headers
        )

    async def download(self, url: str):
        return await self.blob(self.base_url + url, headers=self.headers)


    async def create_repo(self, repo_name: str, private: bool = False):
        return await self.post(
            "/user/repos",
            json={
                "name": repo_name,
                "private": private,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
            },
        )
        
    async def get_repo(self, repo_name: str):
        return await self.get(f"/repos/{repo_name}")
    
    async def create_webhook(self, repo_name: str, url: str):
        return await self.post(
            f"/repos/{repo_name}/hooks",
            json={
                "name": "web",
                "active": True,
                "events": ["push"],
                "config": {"url": url, "content_type": "json"},
            },
        )
        
    async def init(self, repo_name: str, url: str):
        await self.create_repo(repo_name)
        await self.create_webhook(repo_name, url)
        return await self.get_repo(repo_name)