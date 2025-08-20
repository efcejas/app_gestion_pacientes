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

    @lru_cache(maxsize=512)
    def get_study_instance_uid(self, study_id: str) -> str | None:
        """Devuelve el StudyInstanceUID (0020,000D) para enlace OHIF.
        Intenta primero en shared-tags; si no está, recurre a metadatos completos.
        Devuelve None si no puede obtenerlo.
        """
        try:
            tags = self.get_study_shared_tags(study_id)
            uid = tags.get("StudyInstanceUID", {}).get("Value")
            if uid:
                return uid
        except Exception:
            pass
        try:
            meta = self.get_study_metadata(study_id)
            return (meta.get("MainDicomTags", {}) or {}).get("StudyInstanceUID")
        except Exception:
            return None

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
