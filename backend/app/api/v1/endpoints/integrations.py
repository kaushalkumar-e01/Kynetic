import secrets
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.errors import ValidationException
from app.models.user import User
from app.models.project import Project, ConnectedAccount
from app.schemas.project import (
    GitHubConnectResponse,
    GitHubRepoItem,
    ImportGitHubRepoRequest,
    ProjectResponse,
)
from app.services.github_service import github_service

router = APIRouter()


@router.get(
    "/integrations/github/connect",
    response_model=GitHubConnectResponse,
    summary="Get GitHub OAuth authorization URL",
)
def connect_github(current_user: User = Depends(get_current_user)):
    state = secrets.token_urlsafe(16)
    auth_url = github_service.get_authorization_url(state=state)
    return GitHubConnectResponse(authorization_url=auth_url, state=state)


@router.get(
    "/integrations/github/callback",
    summary="GitHub OAuth callback to store credentials",
)
def github_callback(
    code: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token_data = github_service.exchange_code_for_token(code)
    token = token_data.get("access_token")
    if not token:
        raise ValidationException("Did not receive access token from GitHub.")

    account = db.query(ConnectedAccount).filter_by(user_id=current_user.id, provider="github").first()
    if not account:
        account = ConnectedAccount(
            user_id=current_user.id,
            provider="github",
            provider_account_id="github_user",
            encrypted_token=token,
            granted_scopes=["read:user", "repo"],
        )
        db.add(account)
    else:
        account.encrypted_token = token
    db.commit()

    return {"message": "GitHub account successfully connected.", "provider": "github"}


@router.get(
    "/integrations/github/repositories",
    response_model=List[GitHubRepoItem],
    summary="List repositories from connected GitHub account",
)
def list_github_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(ConnectedAccount).filter_by(user_id=current_user.id, provider="github").first()
    token = account.encrypted_token if account else "gho_mock_token_dev"
    repos = github_service.fetch_user_repositories(token)
    return [GitHubRepoItem(**r) for r in repos]


@router.post(
    "/integrations/github/repositories",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import a GitHub repository as a user project",
)
def import_github_repository(
    payload: ImportGitHubRepoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owner, repo_name = github_service.parse_repo_url(payload.repository_url)
    project_name = payload.name or repo_name.replace("-", " ").title()

    project = Project(
        user_id=current_user.id,
        name=project_name,
        description=payload.description or f"Imported GitHub repository: {owner}/{repo_name}",
        source_type="github",
        repository_url=payload.repository_url,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete(
    "/integrations/github/connection",
    summary="Disconnect GitHub account",
)
def disconnect_github(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    github_service.disconnect(user_id=current_user.id, db=db)
    return {"message": "GitHub connection removed successfully."}

