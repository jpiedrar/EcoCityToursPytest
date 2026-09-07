import os
import requests

class BaseAPIClient:
    DEFAULT_BASE_URL = os.getenv('API_BASE_URL', 'https://mockedapi.com/api/')
    DEFAULT_TIMEOUT = float(os.getenv('API_TIMEOUT', '10'))

    def __init__(self, base_url=None, timeout=None):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip('/') + '/'
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

    def build_url(self, path=''):
        return f"{self.base_url}{path.lstrip('/')}"

    def post(self, path='', **kwargs):
        return requests.post(
            self.build_url(path),
            timeout=self.timeout,
            **kwargs,
        )
