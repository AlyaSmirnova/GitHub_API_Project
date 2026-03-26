from services.base_service import BaseService
import requests
import allure


class IssueService(BaseService):

    def __init__(self):
        super().__init__()

    @allure.step('API: create an issue in "{repository_name}"')
    def create_issue(self, repository_name, title, **kwargs):

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}/issues'
        payload = {"title": title}
        payload.update(kwargs)

        response = requests.post(url, headers=self.headers, json=payload)
        return response

    @allure.step('API: get issue #{issue_number} in "{repository_name}"')
    def get_issue(self, repository_name, issue_number): # issue_number - это динамический ID, который присваивает GitHub

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}/issues/{issue_number}'
        response = requests.get(url, headers=self.headers)
        return response

    @allure.step('API: update issue #{issue_number} in "{repository_name}"')
    def update_issue(self, repository_name, issue_number, **kwargs):

        url = f'{self.base_url}/repos/{self.github_username}/{repository_name}/issues/{issue_number}'
        response = requests.patch(url, headers=self.headers, json=kwargs)
        return response
