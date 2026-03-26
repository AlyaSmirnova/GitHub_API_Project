import uuid
import allure
import requests


@allure.feature('Repository Management')
class TestGetGithubRepository:

    @allure.story('Get a repository')
    @allure.title('Get existing repository details and verify response status code')
    @allure.description('Creates a repository and then fetch its details to verify response status code')
    def test_get_repository_return_success_status_code(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'get-test-repository-{uuid.uuid4().hex[:5]}'
        description = 'First test description for GET request'

        with allure.step(f'Pre-condition: create a new repository "{repository_name}"'):
            create_response = api.create_repo(name=repository_name, description=description)
            assert create_response.status_code == 201, f'Failed to create a repository. Expected 201, but got {create_response.status_code}. Response: {create_response.text}'
            created_repositories_list.append(repository_name)

        with allure.step(f'Fetch details for repository "{repository_name}"'):
            response = api.get_repo(repository_name)
        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

    @allure.story('Get a repository')
    @allure.title('Get existing repository details and verify data')
    @allure.description('Creates a repository and then fetch its details to verify all important fields')
    def test_get_repository_return_all_important_fields(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'get-test-repository-{uuid.uuid4().hex[:5]}'
        description = 'Second test description for GET request'
        with allure.step(f'Pre-condition: create a new repository "{repository_name}"'):
            create_response = api.create_repo(name=repository_name, description=description)
            assert create_response.status_code == 201, f'Failed to create a repository. Expected 201, but got {create_response.status_code}. Response: {create_response.text}'
            created_repositories_list.append(repository_name)
        with allure.step(f'Fetch details for repository "{repository_name}"'):
            response = api.get_repo(repository_name)
        with allure.step('Verify repository data consistency'):
            data = response.json()
            assert data['name'] == repository_name, f'Name mismatch! Expected {repository_name}, but got {data['name']}'
            assert data['owner']['login'] == api.github_username, 'Owner login mismatch'
            assert data['description'] == description, 'Description mismatch'
            assert data['private'] is False, 'Repository should be public by default'

    @allure.story('Get a repository')
    @allure.title('Get existing repository details and verify data types and essential properties')
    @allure.description('Creates a repository and then verify data types of response fields and essential properties')
    def test_get_repository_return_correct_data_types(self, repository_api):
        api, created_repositories_list = repository_api
        repository_name = f'get-test-repository-{uuid.uuid4().hex[:5]}'
        description = 'Third test description for GET request'
        with allure.step(f'Pre-condition: create a new repository "{repository_name}"'):
            create_response = api.create_repo(name=repository_name, description=description)
            assert create_response.status_code == 201, f'Failed to create a repository. Expected 201, but got {create_response.status_code}. Response: {create_response.text}'
            created_repositories_list.append(repository_name)
        with allure.step(f'Fetch details for repository "{repository_name}"'):
            response = api.get_repo(repository_name)
        with allure.step('Verify data types and essential properties'):
            data = response.json()
            assert isinstance(data['id'], int), 'Repository ID should be an integer'
            assert data['permissions']['push'] is True, 'Token should have push permissions'

    @allure.story('Get a repository')
    @allure.title('Error: get non-existent repository')
    @allure.description('Verifies that API returns 404 when repository name doesn\'t exist')
    def test_get_repository_not_found(self, repository_api):

        api, created_repositories_list = repository_api
        non_existent_repository_name = 'repository-does-not-exist'

        with allure.step(f'Request non-existent repository {non_existent_repository_name}'):
            response = api.get_repo(non_existent_repository_name)
        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404 for non-existent repository, but got {response.status_code}'
        with allure.step('Verify error message is "Not Found"'):
            assert response.json().get('message') == 'Not Found', 'Error message should be "Not Found"'

    @allure.story('Get a repository')
    @allure.title('Error: get repository with invalid owner name')
    @allure.description('Verifies that API returns 404 when owner name is incorrect')
    def test_get_repository_incorrect_owner_name_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        invalid_owner = 'invalid-owner-name-12343'
        repository_name = 'test-invalid-owner-name-repository'
        url = f'{api.base_url}/repos/{invalid_owner}/{repository_name}'

        with allure.step(f'Request repository with invalid owner name: {invalid_owner}'):
            response = requests.get(url, headers=api.headers)
        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404 for invalid owner, but got {response.status_code}'

    @allure.story('Get a repository')
    @allure.title('Error: access private repository without authorization')
    @allure.description('Verifies that private repository is hidden (returns 404) when requested without token')
    def test_get_repository_without_token_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'private-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create private repository {repository_name}'):
            private_repository = api.create_repo(name=repository_name, private=True)
            created_repositories_list.append(repository_name)
        with allure.step('Request private repository without Authorization header'):
            url = f'{api.base_url}/repos/{api.github_username}/{repository_name}'
            response = requests.get(url, headers={'Accept': 'application/vnd.github+json'})
        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404 (Hidden), but got {response.status_code}'
