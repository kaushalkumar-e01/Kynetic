import re
from typing import List, Dict, Any
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ValidationException
from app.models.project import ConnectedAccount


class GitHubService:
    @staticmethod
    def get_authorization_url(state: str) -> str:
        client_id = settings.GITHUB_CLIENT_ID or "placeholder-github-client-id"
        redirect_uri = settings.GITHUB_REDIRECT_URI
        scope = "read:user,repo"
        return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            # Fallback mock for local development without live OAuth app
            return {
                "access_token": f"gho_mock_token_{code[:10]}",
                "scope": "read:user,repo",
                "token_type": "bearer",
            }

        url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=data)
            if resp.status_code != 200:
                raise ValidationException("Failed to exchange GitHub authorization code.")
            return resp.json()

    @staticmethod
    def fetch_user_repositories(access_token: str) -> List[Dict[str, Any]]:
        if access_token.startswith("gho_mock_token_"):
            return [
                {
                    "name": "kynetic-platform",
                    "full_name": "developer/kynetic-platform",
                    "description": "Personalized capability development and career platform",
                    "html_url": "https://github.com/developer/kynetic-platform",
                    "language": "Python",
                    "is_private": False,
                    "stargazers_count": 12,
                    "updated_at": "2026-11-01T12:00:00Z",
                },
                {
                    "name": "distributed-task-worker",
                    "full_name": "developer/distributed-task-worker",
                    "description": "Fault-tolerant background job worker using Redis and FastAPI",
                    "html_url": "https://github.com/developer/distributed-task-worker",
                    "language": "Python",
                    "is_private": False,
                    "stargazers_count": 28,
                    "updated_at": "2026-10-15T08:30:00Z",
                },
            ]

        url = "https://api.github.com/user/repos?sort=updated&per_page=30"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code != 200:
                    return []
                repos = resp.json()
                return [
                    {
                        "name": r.get("name"),
                        "full_name": r.get("full_name"),
                        "description": r.get("description"),
                        "html_url": r.get("html_url"),
                        "language": r.get("language"),
                        "is_private": r.get("private", False),
                        "stargazers_count": r.get("stargazers_count", 0),
                        "updated_at": r.get("updated_at"),
                    }
                    for r in repos
                ]
        except Exception:
            return []

    @staticmethod
    def parse_repo_url(url: str) -> tuple[str, str]:
        clean_url = url.strip().rstrip("/")
        match = re.search(r"github\.com/([^/]+)/([^/]+)", clean_url)
        if not match:
            raise ValidationException(f"Invalid GitHub repository URL: '{url}'")
        return match.group(1), match.group(2)

    @staticmethod
    def disconnect(user_id: str, db: Session):
        account = db.query(ConnectedAccount).filter_by(user_id=user_id, provider="github").first()
        if account:
            db.delete(account)
            db.commit()


github_service = GitHubService()

