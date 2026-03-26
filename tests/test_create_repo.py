import uuid
import allure
import requests


@allure.feature('Repository Management')
class TestCreateGithubRepository:

    @allure.story('Create a repository')
    @allure.title('Create a repository with minimum required data')
    @allure.description('Verifies that a repository can be created with only "name" field')
    def test_create_repo_with_only_name_return_success(self, repository_api):
        # Unpacking the repository_api fixture: (RepoService instance, cleanup list)
        api, created_repositories_list = repository_api
        repository_name = f'Only-name-repository-{uuid.uuid4().hex[:5]}'
        with allure.step(f'Create a repository: {repository_name}'):
            response = api.create_repo(name=repository_name)
        with allure.step('Verify response status code is 201'):
            assert response.status_code == 201, f'Expected 201, but got {response.status_coed}. Response: {response.text}'
        with allure.step('Check repository name and default visibility'):
            data = response.json()
            assert data['name'] == repository_name, f"Expected name {repository_name}, but got {data['name']}"
            assert data['private'] is False, 'New repository should be public by default'

        created_repositories_list.append(repository_name)

    @allure.story('Create a repository')
    @allure.title('Create a private repository with full data')
    @allure.description('Verifies creation of a private repository with name, description and private field')
    def test_create_repo_with_full_data_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Full-data-private-repository-{uuid.uuid4().hex[:5]}'
        description = 'Full data test repository'

        with allure.step(f'Create a repository'):
            response = api.create_repo(
                name = repository_name,
                description = description,
                private = True
            )
        with allure.step('Verify response statis code is 201'):
            assert response.status_code == 201, f'Expected 201, but got {response.status_code}. Response: {response.text}'
        with allure.step('Verify data of the private test repository'):
            data = response.json()
            assert data['name'] == repository_name, f"Expected {repository_name}, but got {data['name']}"
            assert data['description'] == description, f"Expected {description}, but got {data['description']}"
            assert data['private'] is True, 'Repository should be private'

        created_repositories_list.append(repository_name)

    @allure.story('Create a repository')
    @allure.title('Error: Create a repository with a duplicate name')
    @allure.description('Verifies that API returns 422 when trying to create a repository with a duplicate name')
    def test_create_repository_with_duplicate_name_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Duplicate-test-repository-{uuid.uuid4().hex[:5]}'
        with allure.step(f'Create first repository "{repository_name}"'):
            first_repo = api.create_repo(name=repository_name)
            assert first_repo.status_code == 201, f'Expected 201, but got {first_repo.status_code}. Response: {first_repo.text}'
            created_repositories_list.append(repository_name)
        with allure.step(f'Try to create duplicate repository "{repository_name}"'):
            duplicate_repo = api.create_repo(name = repository_name)
        with allure.step('Verify response status code is 422'):
            assert duplicate_repo.status_code == 422, f'Expected 422, but got {duplicate_repo.status_code}. Response: {duplicate_repo.text}'
        with allure.step('Verify that error message contains "name already exists"'):
            error_data = duplicate_repo.json()
            assert 'name already exist' in str(error_data).lower(), f'Error message should mention duplicate name'

    @allure.story('Create a repository')
    @allure.title('Error: Create a repository with an empty name')
    @allure.description('Verifies that API returns 422 when "name" is empty')
    def test_create_repository_with_empty_name_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = ''

        with allure.step(f'Try to creates a repository with an empty name'):
            response = api.create_repo(name=repository_name)
        with allure.step('Verify response status code is 422'):
           assert response.status_code == 422, f'Expected 422, but got {response.status_code}. Response: {response.text}'
        with allure.step('Verify error details in response'):
            error_data = response.json()
            assert 'errors' in error_data, 'Response should contains validation errors'

    @allure.story('Create a repository')
    @allure.title('Error: Create a repository without name')
    @allure.description('Verifies that API returns 422 when "name" is missing in the payload')
    def test_create_repository_missing_name_in_payload_return_error(self, repository_api):
        # We use direct requests.post here to bypass the RepoService's auto-name generation logic
        api, created_repositories_list = repository_api
        payload = {'description': 'Empty repository without name field'}

        with allure.step(f'Try to create repository without "name"'):
            url = f'{api.base_url}/user/repos'
            response = requests.post(url, headers = api.headers, json=payload)
        with allure.step('Verify response status code is 422'):
           assert response.status_code == 422, f'Expected 422, but got {response.status_code}. Response: {response.text}'
           assert 'name' in response.text, 'Error message should mention missing "name" field'

    @allure.story('Create a repository')
    @allure.title('Check: Create a repository with invalid type of field "name"')
    @allure.description('Verifies that API returns error when "name" is passed as an integer')
    def test_create_repository_with_name_as_an_integer_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = 58

        with allure.step('Try to create repository with name as an integer'):
            response = api.create_repo(repository_name)

        allure.dynamic.description(f'Note: GitHub API automatically casts integer to strings')
        with allure.step('Verify that response status code is 201'):
            assert response.status_code == 201, f'Expected 201, but got {response.status_code}. Response: {response.text}'
        with allure.step('Verify that the name was converted to string'):
            data = response.json()
            assert data['name'] == str(repository_name), 'Integer name should be cast to string'

        created_repositories_list.append(str(repository_name))

    @allure.story('Create a repository')
    @allure.title('Error: Create a repository with invalid token')
    @allure.description('Verifies that API returns 401 error when authorization token is invalid')
    def test_create_repository_with_invalid_token_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        invalid_headers = api.headers.copy()
        invalid_headers['Authorization'] = 'Bearer fake_token'

        with allure.step('Try to create repository with invalid token'):
            url = f'{api.base_url}/user/repos'
            response = requests.post(url, headers=invalid_headers, json={'name': 'fake_repository'})
        with allure.step('Verify response status code is 401'):
            assert response.status_code == 401, f'Expected 401, but got {response.status_code}. Response: {response.text}'
            assert 'Bad credentials' in response.text, 'Error should indicate invalid credentials'
