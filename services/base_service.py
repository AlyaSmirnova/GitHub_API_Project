from src.config import Config


class BaseService:

    def __init__(self):

        self.base_url = Config.BASE_URL
        self.github_token = Config.GITHUB_TOKEN
        self.github_username = Config.GITHUB_USERNAME
        self.headers = Config.HEADERS
