import uuid
import allure
import time
import requests


@allure.feature('Repository Management')
class TestUpdateGithubRepository:

    @allure.story('Update a repository')
    @allure.title('Update repository description successfully')
    @allure.description('Creates a repository and updates its description using PATCH request')
    def test_update_description_in_existent_repository_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        new_repository_name = f'Update-test-repository-{uuid.uuid4().hex[:5]}'
        new_repository_description = 'Update description via API'

        with allure.step(f'Pre-condition: create new repository "{new_repository_name}"'):
            create_response = api.create_repo(new_repository_name)
            assert create_response.status_code == 201, f'Expected 201, but got {create_response.status_code}. Response: {create_response.text}'
            created_repositories_list.append(new_repository_name)

        with allure.step(f'Update description to a {new_repository_name}'):
            response = api.update_repo(repository_name = new_repository_name, description = new_repository_description)

        with allure.step(f'Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

        with allure.step(f'Verify that description was updated and name remained the same'):
            data = response.json()
            assert data['name'] == new_repository_name, f'Repository name should not have changed'
            assert data['description'] == new_repository_description, f"Description mismatch. Expected {new_repository_description}, but got {data['description']}"

        created_repositories_list.append(new_repository_name)

    @allure.story('Update a repository')
    @allure.title('Rename repository successfully')
    @allure.description('Verifies that repository can be renamed and remains accessible via new name')
    def test_update_repository_name_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        initial_repository_name = f'Rename-test-repository-{uuid.uuid4().hex[:5]}'
        new_repository_name = f'Renamed-initial-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository "{initial_repository_name}"'):
            api.create_repo(initial_repository_name)
            created_repositories_list.append(initial_repository_name)
            # Giving GitHub API some time to finalize repository creation and indexing to avoid
            # 422 'Conflicting operation' error on the next PATCH request
            time.sleep(3)

        with allure.step(f'Rename repository from {initial_repository_name} to {new_repository_name}'):
            response = api.update_repo(repository_name=initial_repository_name, name=new_repository_name)

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify that name was updated'):
            data = response.json()
            assert data['name'] == new_repository_name, f"Name mismatch. Expected {new_repository_name}, but got {data['name']}"

        with allure.step('Verify repository is accessible via the new name'):
            get_response = api.get_repo(new_repository_name)
            assert get_response.status_code == 200, f'Expected 200, but got {get_response.status_code}. Response: {get_response.text}'

        created_repositories_list.append(new_repository_name)

    @allure.story('Update a repository')
    @allure.title('Change repository visibility from Public to Private')
    @allure.description('Verifies that a public repository can be successfully converted to a private one')
    def test_change_repository_visibility_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Visibility-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository "{repository_name}"'):
            create_response = api.create_repo(name=repository_name, private=False)
            actual_name = create_response.json()['name']
            created_repositories_list.append(actual_name)
            # Giving GitHub API some time to finalize repository creation and indexing to avoid
            # 422 'Conflicting operation' error on the next PATCH request
            time.sleep(3)

        with allure.step('Change repository visibility to private=True'):
            response = api.update_repo(repository_name=actual_name, private=True)

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify that visibility was changed from False to True'):
            data = response.json()
            assert data['private'] == True, f"Expected private: True, but got {data['private']}"

        # Small delay to ensure Access Control Propagation is completed on GitHub side
        # before teardown fixture attempts to delete the new private repository
        time.sleep(3)

    @allure.story('Update a repository')
    @allure.title('Disable repository features (Issues and Wiki)')
    @allure.description('Verifies that has_issues and has_wiki can be disabled via PATCH request')
    def test_update_repository_features_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Features-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository "{repository_name}"'):
            api.create_repo(repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Disable Issues and Wiki Features'):
            response = api.update_repo(repository_name=repository_name, has_issues=False, has_wiki=False)

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify that features are successfully disabled'):
            data = response.json()
            assert data['has_issues'] is False, f"Expected has_issues: False, but got {data['has_issues']}"
            assert data['has_wiki'] is False, f"Expected has_wiki: False, but got {data['has_wiki']}"

    @allure.story('Update a repository')
    @allure.title('Error: rename repository to an already existing name')
    @allure.description('Verifies that API returns 422 when trying to rename a repository to a name that is already existed')
    def test_update_repository_existent_name_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name_1 = f'Existent-name-update-test-repository-{uuid.uuid4().hex[:5]}'
        repository_name_2 = f'Existent-name-update-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create 2 new repositories: "{repository_name_1}" and "{repository_name_2}"'):
            api.create_repo(repository_name_1)
            created_repositories_list.append(repository_name_1)
            api.create_repo(repository_name_2)
            created_repositories_list.append(repository_name_2)

        with allure.step(f'Try to rename {repository_name_1} to {repository_name_2}'):
            response = api.update_repo(repository_name=repository_name_2, name=repository_name_1)

        with allure.step('Verify response status code is 422'):
            assert response.status_code == 422, f'Expected 422, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify that error message contains "name already exists"'):
            error_data = response.json()
            assert 'name already exists' in str(error_data).lower(), f'Error message should mention duplicate name'

    @allure.story('Update a repository')
    @allure.title('Check: update repository with invalid data type')
    @allure.description('Verifies that GitHub API ignores invalid data types instead of crashing')
    def test_update_repository_invalid_data_type_return_success(self, repository_api):

        api, created_repositories_list = repository_api
        repository_name = f'Data-type-update-test-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository: "{repository_name}"'):
            api.create_repo(repository_name)
            created_repositories_list.append(repository_name)

        with allure.step('Try to update "has_issues" using a string instead of a boolean'):
            response = api.update_repo(repository_name=repository_name, has_issues='yes')

        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify that "has_issues" remains True (invalid data type ignored)'):
            data = response.json()
            assert data['has_issues'] is True, 'Value should not have changed to a string'

    @allure.story('Update a repository')
    @allure.title('Error: update non-existent repository')
    @allure.description('Verifies that API returns 404 when trying to update repository that does not exist')
    def test_update_non_existent_repository_return_error(self, repository_api):

        api, created_repositories_list = repository_api
        non_existent_repository = f'Update-test-non-existent-repository-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Try to update description of non-existent repository "{non_existent_repository}"'):
            response = api.update_repo(repository_name=non_existent_repository, description='some description')

        with allure.step('Verify response status code is 404'):
            assert response.status_code == 404, f'Expected 404, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify error message is "Not Found"'):
            error_data = response.json()
            assert error_data.get('message') == 'Not Found', f"Expected 'Not Found' message, but got {error_data.get('message')}"

    @allure.story('Update a repository')
    @allure.title('Error: update repository with invalid token')
    @allure.description('Verifies that API returns 401 Unauthorized when token is invalid')
    def test_update_repository_unauthorized_return_error(self, repository_api):
        api, created_repositories_list = repository_api
        repository_name = f'Update-test-repository-unauthorized-{uuid.uuid4().hex[:5]}'

        with allure.step(f'Pre-condition: create new repository: "{repository_name}"'):
            api.create_repo(repository_name)
            created_repositories_list.append(repository_name)

        invalid_headers = api.headers.copy()
        invalid_headers['Authorization'] = 'Bearer-invalid-token-12345'

        with allure.step('Try to update description with invalid token'):
            url = f'{api.base_url}/repos/{api.github_username}/{repository_name}'
            response = requests.patch(url, headers=invalid_headers, json={'description': 'some description for this repository'})

        with allure.step('Verify response status code is 401'):
            assert response.status_code == 401, f'Expected 401, but got {response.status_code}. Response: {response.text}'

        with allure.step('Verify error message contains "Requires authentication"'):
            assert 'Requires authentication' in response.text, f'Expected "Requires authentication" in error message, but got {response.text}'
