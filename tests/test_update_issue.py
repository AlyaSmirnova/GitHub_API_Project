import uuid
import requests
import allure
import time


@allure.feature('Issue Management')
class TestUpdateGithubIssue:

    @allure.story('Update an issue')
    @allure.title('Close an open issue successfully')
    @allure.description('Creates an issue and then updates its state to "closed" via PATCH request')
    def test_update_issue_state_to_closed_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-repository-{uuid.uuid4().hex[:5]}'
        issue_title = 'Bug was closed'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)
            time.sleep(3)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']
            issue_state = create_result.json()['state']
            time.sleep(3)

        with allure.step('Verify state for new issue is open'):
            assert issue_state == 'open', 'Initial state should be "open"'

        with allure.step(f'Close issue #{issue_number} in "{repository_name}"'):
            response = issue_api.update_issue(repository_name=repository_name, issue_number=issue_number, state='closed')

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'

        with allure.step('Verify that issue state now is "closed"'):
            data = response.json()
            assert data['state'] == 'closed', f'Expected state "closed", but got {data['state']}'
            assert data['number'] == issue_number, 'Issue number should remain the same'

    @allure.story('Update an issue')
    @allure.title('Edit issue title and body successfully')
    @allure.description('Creates an issue and then updates both title and body via PATCH request')
    def test_update_issue_change_title_and_body_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-edit-title-and-body-{uuid.uuid4().hex[:5]}'
        initial_title = 'Initial title'
        new_title = 'New title'
        new_body = 'This is new body'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {initial_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=initial_title)
            issue_number = create_result.json()['number']

        with allure.step('Create issue title and body'):
            response = issue_api.update_issue(
                repository_name=repository_name,
                issue_number=issue_number,
                title=new_title,
                body=new_body
            )

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'

        with allure.step('Verify updated fields "title" and "body"'):
            data = response.json()
            assert data['title'] == new_title, f'Expected {new_title}, but got {data['title']}'
            assert data['body'] == new_body, f'Expected {new_body}, but got {data['body']}'

    @allure.story('Update an issue')
    @allure.title('Replace issue labels successfully')
    @allure.description('Creates an issue with "bug" label and then replace it with "fixed" label')
    def test_update_issue_replace_label_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-replace-label-{uuid.uuid4().hex[:5]}'
        issue_title = 'Test Issue labels replacement'
        initial_labels = ['bug']
        new_labels = ['fixed']

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title, labels=initial_labels)
            issue_number = create_result.json()['number']

        with allure.step(f'Replace labels {initial_labels} with {new_labels}'):
            response = issue_api.update_issue(repository_name=repository_name, issue_number=issue_number, labels=new_labels)

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'

        with allure.step('Verify that old labels are gone and only new labels exist'):
            data = response.json()
            actual_labels = [label['name'] for label in data['labels']]
            assert 'fixed' in actual_labels, f'Expected "fixed" in {actual_labels}'
            assert 'bug' not in actual_labels, f'Expected "bug" not in {actual_labels}'

    @allure.story('Update an issue')
    @allure.title('Reopen a closed issue successfully')
    @allure.description('Verifies that closed issue can be reopened')
    def test_update_issue_reopen_issue_return_success(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-reopen-issue-{uuid.uuid4().hex[:5]}'
        issue_title = 'Test Issue labels replacement'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']

        with allure.step('Change issue state from "open" to "closed"'):
            issue_api.update_issue(repository_name=repository_name, issue_number=issue_number, state='closed')

        with allure.step(f'Reopen issue #{issue_number}'):
            response = issue_api.update_issue(repository_name=repository_name, issue_number=issue_number, state='open')

        with allure.step('Verify response status code is 200 and state is "open"'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'
            assert response.json()['state'] == 'open', f'Expected state "open", but got {response.json()['state']}'

    @allure.story('Update an issue')
    @allure.title('Error: update non-existent issue number')
    @allure.description('Verifies that API returns 404 when trying to update an issue number that doesn\'t exist')
    def test_update_issue_non_existent_issue_number_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-non-existent-issue-number-{uuid.uuid4().hex[:5]}'
        invalid_number = 99999

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Try to close non-existent issue #{invalid_number}'):
            response = issue_api.update_issue(repository_name=repository_name, issue_number=invalid_number, state='closed')

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}'

        with allure.step('Verify error message is "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == 'Not Found', f'Expected error message "Not Found", but got {error_data.get('message')}'

    @allure.story('Update an issue')
    @allure.title('Check: update issue with invalid state value')
    @allure.description('Verifies that API ignores unsupported value to the "state" field instead of returning an error')
    def test_update_issue_invalid_state_value_ignores(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-invalid-state-value-{uuid.uuid4().hex[:5]}'
        issue_title = 'Invalid state test'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']

        with allure.step(f'Try to set state "finished" for issue #{issue_number}'):
            response = issue_api.update_issue(repository_name=repository_name, issue_number=issue_number, state='finished')

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}'

        with allure.step('Verify that state remains "open" (invalid value ignored)'):
            data = response.json()
            assert data['state'] == 'open', f'State should still be "open", but got {data['state']}'

    @allure.story('Update an issue')
    @allure.title('Error: update issue without authorization')
    @allure.description('Verifies that API returns 401 Unauthorized when trying to update an issue with invalid token')
    def test_update_issue_unauthorized_return_error(self, repository_api, issue_api):

        repo_api, created_repositories_list = repository_api
        repository_name = f'Update-issue-test-unauthorized-{uuid.uuid4().hex[:5]}'
        issue_title = 'Authorization issue test'

        with allure.step(f'Pre-condition: create a repository: {repository_name}'):
            repo_api.create_repo(name=repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Pre-condition: create an issue: {issue_title}'):
            create_result = issue_api.create_issue(repository_name=repository_name, title=issue_title)
            issue_number = create_result.json()['number']

        with allure.step(f'Try to close issue #{issue_number} with invalid token'):
            url = f'{issue_api.base_url}/repos/{issue_api.github_username}/{repository_name}/issues/{issue_number}'
            response = requests.patch(url, headers={'Accept': 'application/vnd.github+json'}, json={'state': 'close'})

        with allure.step('Verify response status code is 401'):
            assert response.status_code == 401, f'Expected 401, but got {response.status_code}'

        with allure.step('Verify error message indicates missing credentials'):
            assert 'Requires authentication' in response.text, f'Expected "Requires authentication" in error message, but got {response.text}'
