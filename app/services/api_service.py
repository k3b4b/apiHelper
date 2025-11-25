import requests

BASE_URL = "https://api-ru.iiko.services/api/1"
ENDPOINTS = {
        "token": "/access_token?=",
        "organizations": "/organizations",
        "terminals": "/terminal_groups",
        "payment_types": "/payment_types",
        "order_types": "/deliveries/order_types",
        "discounts": "/discounts"
}

class ApiService:
    # билдер хоста, соединяет URL c эндпоинтом
    def build_url(self, path: str) -> str:
        return BASE_URL + path

    # запрос токена
    def fetch_token(self, api_key: str) -> dict:
        response = requests.post(
            self.build_url(ENDPOINTS["token"]),
            json={"apiLogin": api_key}
        )
        response.raise_for_status()
        return response.json()

    # запрос организаций
    def fetch_organizations(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            self.build_url(ENDPOINTS["organizations"]),
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    # запрос терминалов
    def fetch_terminals(self, token: str, organization_id: str):
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "organizationIds": [organization_id],
            "includeDisabled": True
        }
        response = requests.post(
            self.build_url(ENDPOINTS["terminals"]),
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def fetch_payment_types(self, token: str, organization_id: str):
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "organizationIds": [organization_id]
        }
        response = requests.post(
            self.build_url(ENDPOINTS["payment_types"]),
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def fetch_order_types(self, token: str, organization_id: str):
        headers = {"Authorization": f"Bearer {token}"}
        print("Organization ID:", organization_id)
        payload = {
            "organizationIds": [organization_id]
        }
        response = requests.post(
            self.build_url(ENDPOINTS["order_types"]),
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def fetch_discount_types(self, token: str, organization_id: str):
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "organizationIds": [organization_id]
        }
        response = requests.post(
            self.build_url(ENDPOINTS["discounts"]),
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()