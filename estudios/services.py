import requests
from django.conf import settings
from functools import lru_cache

class OrthancClient:
    def __init__(self, base_url=None, username=None, password=None, timeout=10):
        self.base_url = base_url or settings.ORTHANC_BASE_URL.rstrip('/')
        if username and password:
            self.auth = (username, password)
        elif getattr(settings, 'ORTHANC_USERNAME', None) and getattr(settings, 'ORTHANC_PASSWORD', None):
            self.auth = (settings.ORTHANC_USERNAME, settings.ORTHANC_PASSWORD)
        else:
            self.auth = None  # sin auth
        self.timeout = timeout

    def _get(self, path):
        url = f"{self.base_url}{path}"
        resp = requests.get(url, auth=self.auth, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # Estudios
    def list_studies(self):
        return self._get('/studies')

    @lru_cache(maxsize=256)
    def get_study_metadata(self, study_id):
        return self._get(f'/studies/{study_id}')

    def get_study_shared_tags(self, study_id):
        return self._get(f'/studies/{study_id}/shared-tags')

    def list_series_in_study(self, study_id):
        return self._get(f'/studies/{study_id}/series')

    def list_instances_in_series(self, series_id):
        return self._get(f'/series/{series_id}/instances')

    def get_series_metadata(self, series_id):
        return self._get(f'/series/{series_id}')

    def get_instance_metadata(self, instance_id):
        return self._get(f'/instances/{instance_id}')

client = OrthancClient()
