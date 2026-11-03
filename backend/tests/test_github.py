from app.models.user import User
from app.models.project import ConnectedAccount
from app.core.security import get_password_hash
from app.schemas.project import ImportGitHubRepoRequest
from app.api.v1.endpoints.integrations import (
    connect_github,
    github_callback,
    list_github_repositories,
    import_github_repository,
    disconnect_github,
)


def test_github_integration_flow(db_session):
    user = User(email="github_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Connect endpoint returns authorization URL
    connect_data = connect_github(current_user=user)
    assert "github.com/login/oauth/authorize" in connect_data.authorization_url
    assert connect_data.state is not None

    # 2. Callback exchanges code and stores credentials
    cb_result = github_callback(code="mock_auth_code_12345", current_user=user, db=db_session)
    assert cb_result["provider"] == "github"

    account = db_session.query(ConnectedAccount).filter_by(user_id=user.id, provider="github").first()
    assert account is not None
    assert account.encrypted_token is not None

    # 3. List repositories
    repos = list_github_repositories(current_user=user, db=db_session)
    assert len(repos) >= 1
    assert any(r.name == "kynetic-platform" for r in repos)

    # 4. Import a repository as project
    import_req = ImportGitHubRepoRequest(
        repository_url="https://github.com/developer/kynetic-platform",
    )
    imported_proj = import_github_repository(payload=import_req, current_user=user, db=db_session)
    assert imported_proj.source_type == "github"
    assert "kynetic-platform" in imported_proj.repository_url

    # 5. Disconnect GitHub
    disconnect_res = disconnect_github(current_user=user, db=db_session)
    assert "removed successfully" in disconnect_res["message"]
    assert db_session.query(ConnectedAccount).filter_by(user_id=user.id, provider="github").first() is None

