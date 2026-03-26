import uuid
import requests
import allure


@allure.feature('Issue Management')
class TestGetGithubIssue:

    @allure.story('Get an issue')
    @allure.title('Get existing issue details and verify data')
    @allure.description('Creates a repository and an issue, then fetches issue details by its number')
    def test_get_issue_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Get-issue-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title = f'Read test issue {uuid.uuid4().hex[:5]}'
        issue_body = 'Checking if GET request returns correct data'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title, body=issue_body)
            issue_number = create_result.json()['number']

        with allure.step(f'Get details for issue #{issue_number}'):
            response = issue_api.get_issue(repository_name=repository_name, issue_number=issue_number)

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'

        with allure.step('Verify issue data consistency'):
            data = response.json()
            assert data['number'] == issue_number, f"Expected {issue_number}, but got {data['number']}"
            assert data['title'] == issue_title, f"Expected {issue_title}, but got {data['title']}"
            assert data['body'] == issue_body, f"Expected {issue_body}, but got {data['body']}"
            assert data['state'] == 'open', f"Expected state 'open', but got {data['state']}"

    @allure.story('Get an issue')
    @allure.title('Verify author association field')
    @allure.description('Verifies that issue creator is correctly identified as OWNER of the repository')
    def test_get_issue_author_association_is_owner(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Auth-assoc-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title = 'Ownership Verification Issue'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']

        with allure.step(f'Get details for issue #{issue_number}'):
            response = issue_api.get_issue(repository_name=repository_name, issue_number=issue_number)

        with allure.step('Verify author association is "OWNER"'):
            data = response.json()
            actual_association = data.get('author_association')
            assert actual_association == 'OWNER', f'Expected "OWNER", but got "{actual_association}"'

    @allure.story('Get an issue')
    @allure.title('Error: get non-existent issue number')
    @allure.description('Verifies that API returns 404 when requesting non-existent issue number')
    def test_get_issue_non_existent_issue_number_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Non-existent-issue-number-test-repository-{uuid.uuid4().hex[:5]}'
        invalid_issue_number = 55555

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Request non-existent issue number {invalid_issue_number}'):
            response = issue_api.get_issue(repository_name=repository_name, issue_number=invalid_issue_number)

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'

        with allure.step('Verify error message is "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == 'Not Found', f"Expected 'Not Found', but got {error_data.get('message')}"

    @allure.story('Get an issue')
    @allure.title('Error: get issue number from non-existent repository')
    @allure.description('Verifies that API returns 404 when requesting issue by its number from non-existent repository')
    def test_get_issue_non_existent_issue_number_return_error(self, repository_api, issue_api):

        non_existent_repository_name = f'Non-existent-issue-number-test-repository-{uuid.uuid4().hex[:5]}'
        issue_number = 1

        with allure.step(f'Request issue details from non-existent repository "{non_existent_repository_name}"'):
            response = issue_api.get_issue(repository_name=non_existent_repository_name, issue_number=issue_number)

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'

        with allure.step('Verify error message is "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == 'Not Found', f"Expected 'Not Found', but got {error_data.get('message')}"

    @allure.story('Get an issue')
    @allure.title('Error: access issue in private repository without authorization')
    @allure.description('Verifies that an issue in a private repository is hidden (returns 404) when requested without a token')
    def test_get_issue_without_token_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Get-issue-test-private-repository-without-token-{uuid.uuid4().hex[:5]}'
        issue_title = 'Secret issue'

        with allure.step(f'Pre-condition: create a private repository: {repository_name}'):
            repo_api.create_repo(name=repository_name, private=True)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']

        with allure.step(f'Request issue_number #{issue_number} without Authorization header'):
            url = f'{issue_api.base_url}/repos/{issue_api.github_username}/{repository_name}/issues'
            response = requests.get(url, headers={'Accept': 'application/vnd.github+json'})

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'

    @allure.story('Get an issue')
    @allure.title('Error: invalid issue number format (string instead of integer)')
    @allure.description('Verifies that API returns 404 when issue number in URL is not an integer')
    def test_get_issue_invalid_number_format_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Get-issue-test-repository-invalid-format-number-{uuid.uuid4().hex[:5]}'
        invalid_issue_number = 'Not a number'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Request issue with invalid number'):
            response = issue_api.get_issue(repository_name=repository_name, issue_number=invalid_issue_number)

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'
