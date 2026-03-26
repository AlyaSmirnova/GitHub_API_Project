import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # Global API Configuration
    BASE_URL = 'https://api.github.com'
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        raise ValueError('GITHUB_TOKEN or GITHUB_USERNAME not found in .env file')

    # Common Headers
    HEADERS = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2026-03-10'
    }
