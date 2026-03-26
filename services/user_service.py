from services.base_service import BaseService
import requests
import allure


class UserService(BaseService):

    def __init__(self):
        super().__init__()

    @allure.step('API: Get current user profile')
    def get_user_profile(self):

        url = f'{self.base_url}/user'
        return requests.get(url, headers=self.headers)
