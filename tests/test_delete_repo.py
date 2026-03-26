import uuid
import allure
import time
import requests


@allure.feature('Repository Management')
class TestDeleteGithubRepository:

    @allure.story('Delete a repository')
    @allure.title('Delete an existing repository successfully')
    @allure.description('Creates a repository and then deletes it')
    def test_delete_repository_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Delete-test-repo-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository "{repository_name}"'):
            create_response = api.create_repo(repository_name)
            assert create_response.status_code == 201, f'Expected 201, but got {create_response.status_code}. Response: {create_response.text}'
            created_repositories_list.append(repository_name)

        with allure.step(f'Delete repository "{repository_name}"'):
            response = api.delete_repo(repository_name)

        with allure.step('Verify response status code is 204'):
            assert response.status_code == 204, f'Expected 204, but got {response.status_code}. Response: {response.text}'

        if repository_name in created_repositories_list:
            created_repositories_list.remove(repository_name)

    @allure.story('Delete a repository')
    @allure.title('Verify that repository is inaccessible after deletion')
    @allure.description('Deletes repository and then try to fetch it via GET to confirm 404 error')
    def test_verify_repository_was_deleted(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Deletion-check-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository "{repository_name}"'):
            api.create_repo(repository_name)
            created_repositories_list.append(repository_name)

        with allure.step(f'Delete repository "{repository_name}"'):
            api.delete_repo(repository_name)
            created_repositories_list.remove(repository_name)

        with allure.step(f'Verify repository "{repository_name}" is no longer accessible via GET'):
            get_response = api.get_repo(repository_name)
            assert get_response.status_code == 404, f'Expected 404, but got {get_response.status_code}. Response: {get_response.text}'

    @allure.story('Delete a repository')
    @allure.title('Delete a renamed repository successfully')
    @allure.description('Creates, renames and then deletes a repository')
    def test_delete_renamed_repository_return_success(self, repository_api):
        api, created_repositories_list = repository_api
        initial_repository_name = f'Deletion-test-initial-repository-{uuid.uuid4().hex[:5]}'
        new_repository_name = f'Deletion-test-renamed-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create a repository "{initial_repository_name}"'):
            api.create_repo(initial_repository_name)
            created_repositories_list.append(initial_repository_name)
            time.sleep(3)

        with allure.step(f'Pre-condition: rename {initial_repository_name} to {new_repository_name}'):
            api.update_repo(repository_name=initial_repository_name, name=new_repository_name)
            if initial_repository_name in created_repositories_list:
                created_repositories_list.remove(initial_repository_name)
            created_repositories_list.append(new_repository_name)
            time.sleep(3)

        with allure.step(f'Delete repository using its new name {new_repository_name}'):
            response = api.delete_repo(new_repository_name)

        with allure.step('Verify response status code is 204'):
            assert response.status_code == 204, f'Expected 204, but got {response.status_code}. Response: {response.text}'

        if new_repository_name in created_repositories_list:
            created_repositories_list.remove(new_repository_name)

    @allure.story('Delete a repository')
    @allure.title('Error: delete non-existent repository')
    @allure.description('Verifies that API returns 404 when trying to delete non-existent repository')
    def test_delete_non_existent_repository_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        non_existent_repository = f'Deletion-test-non-existent-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Try to delete non-existent repository "{non_existent_repository}"'):
            response = api.delete_repo(non_existent_repository)

        with allure.step('Verifies response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verifies error message contains "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == "Not Found", f'Expected "Not Found" message, but got {error_data.get('message')}'

    @allure.story('Delete a repository')
    @allure.title('Error: delete repository with invalid token')
    @allure.description('Verifies that API returns 401 Unauthorized when authorization token is invalid')
    def test_delete_repository_with_invalid_token_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Delete-test-repository-unauthorized-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository: "{repository_name}"'):
            api.create_repo(repository_name)
            created_repositories_list.append(repository_name)

        invalid_headers = api.headers.copy()
        invalid_headers['Authorization'] = 'Bearer-invalid-token-55555'

        with allure.step('Try to delete repository with invalid token'):
            url = f'{api.base_url}/repos/{api.github_username}/{repository_name}'
            response = requests.delete(url, headers=invalid_headers)

        with allure.step('Verify response status code is 401'):
            assert response.status_code == 401, f'Expected 401, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify error message contains "Requires authentication"'):
            assert 'Requires authentication' in response.text, f'Expected "Requires authentication" in error message, but got {response.text}'


