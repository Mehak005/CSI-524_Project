"""
api_client.py
HTTP client wrapper for the FileShareAPI Flask server.

Provides methods that mirror the mock API but call the HTTP endpoints.
"""
from types import SimpleNamespace
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiClient:
    def __init__(self, base_url: str = 'http://localhost:5000', timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def _wrap_response(self, resp: requests.Response) -> SimpleNamespace:
        try:
            body = resp.json()
        except Exception:
            body = {'message': resp.text}

        return SimpleNamespace(status_code=resp.status_code, data=body.get('data', {}), message=body.get('message', ''), raw=body)

    def reset(self) -> SimpleNamespace:
        url = f"{self.base_url}/reset"
        r = self.session.post(url, timeout=self.timeout)
        return self._wrap_response(r)

    def create_user(self, email: str, organization_id: str, name: str) -> SimpleNamespace:
        url = f"{self.base_url}/users"
        r = self.session.post(url, json={'email': email, 'organization_id': organization_id, 'name': name}, timeout=self.timeout)
        return self._wrap_response(r)

    def get_user(self, user_id: str) -> SimpleNamespace:
        url = f"{self.base_url}/users/{user_id}"
        r = self.session.get(url, timeout=self.timeout)
        return self._wrap_response(r)

    def create_file(self, owner_id: str, name: str, visibility: str, content: str = '') -> SimpleNamespace:
        url = f"{self.base_url}/files"
        r = self.session.post(url, json={'owner_id': owner_id, 'name': name, 'visibility': visibility, 'content': content}, timeout=self.timeout)
        return self._wrap_response(r)

    def get_file(self, file_id: str, user_id: str) -> SimpleNamespace:
        url = f"{self.base_url}/files/{file_id}"
        r = self.session.get(url, params={'user_id': user_id}, timeout=self.timeout)
        return self._wrap_response(r)

    def update_file(self, file_id: str, user_id: str, content: str) -> SimpleNamespace:
        url = f"{self.base_url}/files/{file_id}"
        r = self.session.put(url, json={'user_id': user_id, 'content': content}, timeout=self.timeout)
        return self._wrap_response(r)

    def delete_file(self, file_id: str, user_id: str) -> SimpleNamespace:
        url = f"{self.base_url}/files/{file_id}"
        r = self.session.delete(url, params={'user_id': user_id}, timeout=self.timeout)
        return self._wrap_response(r)

    def share_file(self, file_id: str, user_id: str, target_user_id: str, permission_type: str = 'read') -> SimpleNamespace:
        url = f"{self.base_url}/files/{file_id}/share"
        r = self.session.post(url, json={'user_id': user_id, 'target_user_id': target_user_id, 'permission_type': permission_type}, timeout=self.timeout)
        return self._wrap_response(r)

    def get_file_permissions(self, file_id: str, user_id: str) -> SimpleNamespace:
        url = f"{self.base_url}/files/{file_id}/permissions"
        r = self.session.get(url, params={'user_id': user_id}, timeout=self.timeout)
        return self._wrap_response(r)

    def list_files(self) -> SimpleNamespace:
        url = f"{self.base_url}/files"
        r = self.session.get(url, timeout=self.timeout)
        return self._wrap_response(r)

    def check_authorization(self, file_id: str, user_id: str, action: str) -> bool:
        """Non-destructive authorization check (uses server's /authorize endpoint)."""
        url = f"{self.base_url}/authorize"
        r = self.session.post(url, json={'file_id': file_id, 'user_id': user_id, 'action': action}, timeout=self.timeout)
        try:
            body = r.json()
            return bool(body.get('allowed', False))
        except Exception:
            return False
