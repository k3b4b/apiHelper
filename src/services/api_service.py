import requests
from src.core.logger import logger

ENDPOINTS = {
        "organizations": "organizations",
        "terminals": "terminal_groups",
        "payment_types": "payment_types",
        "order_types": "deliveries/order_types",
        "discounts": "discounts",
        "nomenclature": "nomenclature"
}

class ApiService:
    BASE_URL = "https://api-ru.iiko.services/api/1/"
    TOKEN_URL = "https://api-ru.iiko.services/api/v2/access_token"

    def __init__(self, token: str = None):
        self.base_url = self.BASE_URL
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        masked = f"***{token[-5:]}" if token else "None"
        logger.debug(f"ApiService initialized with token: {masked}")
    
    # слепляю юрл с эндпоинтами
    def build_url(self, endpoint: str) -> str:
        logger.trace(f"Built URL: {self.base_url + endpoint}")
        return self.base_url + endpoint
    
    # универсальные методы гет и пост с логированием и обработкой ошибок
    def _get(self, endpoint: str, **kwargs):
        logger.info(f"Sending GET to {self.build_url(endpoint)}")
        try:
            response = self.session.get(self.build_url(endpoint), **kwargs)
            logger.debug(f"Response Status Code: {response.status_code}")
            response.raise_for_status()
            logger.trace(f"Response JSON: {response.json()}")
            return response.json()
        except Exception as e:
            logger.exception(f"GET request to {self.build_url(endpoint)} failed: {e}")
            raise

    def _post(self, endpoint: str, **kwargs):
        logger.info(f"Sending POST to {self.build_url(endpoint)}")
        try:
            response = self.session.post(self.build_url(endpoint), **kwargs)
            logger.debug(f"Response Status Code: {response.status_code}")
            response.raise_for_status()
            logger.trace(f"Response JSON: {response.json()}")
            return response.json()
        except Exception as e:
            logger.exception(f"POST request to {self.build_url(endpoint)} failed: {e}")
            raise
    

    # методы для каждого из эндпоинтов
    def fetch_token(self, api_key: str, app_id: str, client_secret: str) -> dict:
        logger.info("Fetching access token…")
        payload = {
            "apiKey": api_key,
            "appId": app_id,
            "clientSecret": client_secret,
        }

        try:
            response = self.session.post(self.TOKEN_URL, json=payload)
            logger.debug(f"Response Status Code: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(f"Token request to {self.TOKEN_URL} failed: {e}")
            raise
    
    def fetch_nomenclature(self, organization_id: str):
        logger.info(f"Fetching nomenclature for org: {organization_id}")
        payload = {"organizationId": organization_id, "startRevision": 0}
        return self._post(ENDPOINTS["nomenclature"], json=payload)
    
    def fetch_organizations(self):
        logger.info("Fetching organizations for the API key")
        return self._get(ENDPOINTS["organizations"])

    def fetch_terminals(self, organization_id: str):
        logger.info(f"Fetching terminals for org: {organization_id}")
        payload = {"organizationIds": [organization_id], "includeDisabled": True}
        return self._post(ENDPOINTS["terminals"], json=payload)

    def fetch_payment_types(self, organization_id: str):
        logger.info(f"Fetching payment types for org: {organization_id}")
        payload = {"organizationIds": [organization_id]}
        return self._post(ENDPOINTS["payment_types"], json=payload)
    
    def fetch_order_types(self, organization_id: str):
        logger.info(f"Fetching order types for org: {organization_id}")
        payload = {"organizationIds": [organization_id]}
        return self._post(ENDPOINTS["order_types"], json=payload)
    
    def fetch_discount_types(self, organization_id: str):
        logger.info(f"Fetching discount types for org: {organization_id}")
        payload = {"organizationIds": [organization_id]}
        return self._post(ENDPOINTS["discounts"], json=payload)
