import allure
import pytest
from services.repo_service import RepoService
from services.user_service import UserService
from services.issue_service import IssueService


@pytest.fixture(scope='function')
def repository_api():
    # SETUP: Initialized the service
    service = RepoService()
    created_repositories = [] # list of created repositories
    yield service, created_repositories
    # TEARDOWN: logic after the test is finished
    for repository_name in created_repositories:
        with allure.step(f'Automatically deleting repository {repository_name}'):
            service.delete_repo(repository_name)

@pytest.fixture
def user_api():
    return UserService()

@pytest.fixture
def issue_api():
    return IssueService()