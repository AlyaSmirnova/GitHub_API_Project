import allure


@allure.feature('Profile Management')
class TestGitHubProfile:

    @allure.story('User Profile')
    @allure.title('Verify authenticated user login matches GITHUB_USERNAME')
    @allure.description('This test ensures that the provided PAT belongs to the correct user.')
    def test_check_my_profile(self, user_api):
        response = user_api.get_user_profile()
        with allure.step('Verify response status code is 200'):
            assert response.status_code == 200, f'Expected 200, but got {response.status_code}. Response: {response.text}'
        with allure.step(f'Verify login equals {user_api.github_username}'):
            actual_login = response.json().get('login')
            assert actual_login == user_api.github_username, f'Expected {user_api.github_username}, but got {actual_login}'
