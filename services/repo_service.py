from services.base_service import BaseService
import requests
import allure
import uuid


class RepoService(BaseService):

    def __init__(self):
        super().__init__()

    @allure.step('API: Create a new repository')
    def create_repo(self, name=None, **kwargs):

        unique_repository_name = name or f'api-test-{uuid.uuid4().hex[:7]}' if name is None else name
        url = f'{self.base_url}/user/repos'
        payload = {'name': unique_repository_name}
        payload.update(kwargs)

        response = requests.post(url, headers=self.headers, json=payload)
        return response

    @allure.step('API: Get a repository details')
    def get_repo(self, repository_name):

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}'
        response = requests.get(url, headers=self.headers)
        return response

    @allure.step('API: Update a repository settings')
    def update_repo(self, repository_name, **kwargs):

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}'
        response = requests.patch(url, headers=self.headers, json=kwargs)
        return response

    @allure.step('API: Delete a repository')
    def delete_repo(self, repository_name):

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}'
        response = requests.delete(url, headers=self.headers)
        return response
