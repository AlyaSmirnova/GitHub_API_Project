import uuid
import requests
import allure


@allure.feature('Issue Management')
class TestCreateGitHubIssue:

    @allure.story('Create an issue')
    @allure.title('Create an issue with only field "title"')
    @allure.description('Creates a repository and then adds a simple issue to it')
    def test_create_issue_with_only_title_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Create-issue-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title = f'Test issue {uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Create issue "{issue_title}" in repository "{repository_name}"'):
            response = issue_api.create_issue(repository_name=repository_name, title=issue_title)

        with allure.step('Verify response status code is 201'):
            assert response.status_code == 201, f'Expected 201, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify issue title and status'):
            data = response.json()
            assert data['title'] == issue_title, f'Expected title {issue_title}, but got {data['title']}'
            assert data['state'] == 'open', 'New issue should have "open" state by default'

        with allure.step('Verify issue has a unique number'):
            assert isinstance(data['number'], int), 'Issue number should be an integer'

    @allure.story('Create an issue')
    @allure.title('Create an issue with full metadata (body, labels, assignees)')
    @allure.description('Creates a repository and then adds an issue to it with full data')
    def test_create_issue_with_full_data_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Issue-full-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title = 'Bug: submit button not working'
        issue_body = 'Detailed description of the bug with steps to reproduce'
        issue_labels = ['bug', 'priority: high']
        issue_assignees = [repo_api.github_username]

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Create repository and add full data in it'):
            response = issue_api.create_issue(
                repository_name=repository_name,
                title=issue_title,
                body=issue_body,
                labels=issue_labels,
                assignees=issue_assignees
            )

        with allure.step('Verify response status code is 201'):
            assert response.status_code == 201, f'Expected 201, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify all data in response'):
            data = response.json()
            assert data['title'] == issue_title, f'Expected title {issue_title}, but got {data['title']}'
            assert data['body'] == issue_body, f'Expected body {issue_body}, but got {data['body']}'
            actual_labels = [label['name'] for label in data['labels']]
            for label in issue_labels:
                assert label in actual_labels, f'Label "{label}" missing in response'

            actual_assignees = [assignee['login'] for assignee in data['assignees']]
            assert issue_api.github_username in actual_assignees

    @allure.story('Create an issue')
    @allure.title('Verify issue numbering')
    @allure.description('Creates a repository and then adds two issue to it and verifies their sequential numbers (1, 2)')
    def test_create_two_issues_return_two_numbers(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Issue-numbering-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title_1 = 'First issue'
        issue_title_2 = 'Second issue'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Create first issue: "{issue_title_1}"'):
            response_1 = issue_api.create_issue(repository_name=repository_name, title=issue_title_1)
            assert response_1.status_code == 201
            issue_number_1 = response_1.json()['number']

        with allure.step(f'Create second issue: "{issue_title_2}"'):
            response_2 = issue_api.create_issue(repository_name=repository_name, title=issue_title_2)
            assert response_2.status_code == 201
            issue_number_2 = response_2.json()['number']

        with allure.step('Verify sequential numbers of two issues'):
            assert issue_number_1 == 1, f'Expected 1, but got {issue_number_1}'
            assert issue_number_2 == 2, f'Expected 2, but got {issue_number_2}'

    @allure.story('Create an issue')
    @allure.title('Error: create an issue with an empty title')
    @allure.description('Verifies that API returns 422 when "title" field is empty')
    def test_create_issues_with_empty_title_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Issue-empty-title-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Try to create issue with empty "field" title'):
            url = f'{issue_api.base_url}/repos/{issue_api.github_username}/{repository_name}/issues'
            response = requests.post(url, headers=issue_api.headers, json={'title': ''})

        with allure.step('Verify response status code is 422'):
            assert response.status_code == 422, f'Expected 422, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify error message for empty title'):
            error_data = response.json()
            assert 'errors' in error_data, 'Response should contain validation errors'

    @allure.story('Create an issue')
    @allure.title('Error: create an issue without "field" title')
    @allure.description('Verifies that API returns 422 when "title" field is completely missing')
    def test_create_issues_without_title_return_error(self, repository_api, issue_api):
        repo_api, created_repositories_list = repository_api
        repository_name = f'Issue-without-title-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Try to create issue with empty "field" title'):
            url = f'{issue_api.base_url}/repos/{issue_api.github_username}/{repository_name}/issues'
            payload = {'body': 'This issue does not have field "title" at all'}
            response = requests.post(url, headers=issue_api.headers, json=payload)

        with allure.step('Verify response status code is 422'):
            assert response.status_code == 422, f'Expected 422, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify error message contains "missing_field" details'):
            error_data = response.json()
            expected_error_message = '"title" wasn\'t supplied'
            assert expected_error_message in error_data.get('message', ''), f'Expected error message to contain "{expected_error_message}", but got {error_data}'

    @allure.story('Create an issue')
    @allure.title('Error: create an issue in a non-existent repository')
    @allure.description('Verifies that API returns 404 when trying to create an issue in a non-existent repository')
    def test_create_issues_in_non_existent_repository_return_error(self, repository_api, issue_api):

        non_existent_repository_name = f'Issue-test-non-existent-repository-{uuid.uuid4().hex[:5]}'
        issue_title = 'Non-existent issue'

        with allure.step('Try to create an issue in non-existent repository'):
            response = issue_api.create_issue(repository_name=non_existent_repository_name, title=issue_title)

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'

        with allure.step('Verify error message is "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == 'Not Found', f'Expected "Not Found" message, but got {error_data.get('message')}'

    @allure.story('Create an issue')
    @allure.title('Error: create an issue without authorization')
    @allure.description('Verifies that API returns 401 Unauthorized when trying to create an issue with invalid authorization token')
    def test_create_issues_with_invalid_token_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Issue-with-invalid-token-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Try to create issue with invalid token'):
            url = f'{issue_api.base_url}/repos/{issue_api.github_username}/{repository_name}/issues'
            response = requests.post(url, headers={'Accept': 'application/vnd.github+json'}, json={'title': 'Issue without token'})

        with allure.step('Verify response status code is 401'):
            assert response.status_code == 401, f'Expected 401, but got {response.status_code}'

        with allure.step('Verify error message contains "Requires authentication"'):
            assert 'Requires authentication' in response.text, f'Expected "Requires authentication" in error message, but got {response.text}'
