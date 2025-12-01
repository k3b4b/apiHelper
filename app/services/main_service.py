from io import BytesIO
import json
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import models
from app.services.api_service import ApiService
from app.services.db_service import check_token, create_api_key, read_terminals, update_terminals, update_token, update_organizations, update_payment_types, update_order_types, update_discount_types, read_exact_key, read_exact_organization, read_api_keys, read_organizations, read_payment_types, read_order_types, read_discount_types, check_exact_key
api = ApiService()

def get_token(db: Session, key_id: int) -> str:
    api_key_obj = read_exact_key(db, key_id)
    if not api_key_obj:
        return None
    token = check_token(db, api_key_obj)
    if token:
        return token
    data = api.fetch_token(api_key_obj.api_key)
    new_token = data["token"]
    update_token(db, api_key_obj, new_token)
    return new_token

def process_new_key(api_key: str, description: str, db: Session):
    existing = check_exact_key(db, api_key)
    if existing:
        raise ValueError(f"Ключ '{api_key}' уже существует")
    create_api_key(db, api_key, description)
    
def download_nomenclature(db: Session, org_id: int, key_id: int):
    token = get_token(db, key_id)
    org = read_exact_organization(db, org_id)
    data = api.fetch_nomenclature(token, org.organization_id)
    file_content = json.dumps(data, ensure_ascii=False, indent=2)
    file_bytes = BytesIO(file_content.encode("utf-8"))
    return StreamingResponse(
        file_bytes,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="nomenclature.txt"'}
    )
def refresh_organizations(db: Session, key_id: int):
    token = get_token(db, key_id)
    data = api.fetch_organizations(token)
    update_organizations(db, read_exact_key(db, key_id), data["organizations"])
    return data

def refresh_terminals(db: Session, org_id: int, key_id: int):
    token = get_token(db, key_id)
    org = read_exact_organization(db, org_id)
    data = api.fetch_terminals(token, org.organization_id)
    update_terminals(db, org, data["terminalGroups"])
    return data

def refresh_payment_types(db: Session, org_id: int, key_id: int):
    token = get_token(db, key_id)
    org = read_exact_organization(db, org_id)
    data = api.fetch_payment_types(token, org.organization_id)
    update_payment_types(db, org, data["paymentTypes"])
    return data

def refresh_order_types(db: Session, org_id: int, key_id: int):
    token = get_token(db, key_id)
    org = read_exact_organization(db, org_id)
    data = api.fetch_order_types(token, org.organization_id)
    update_order_types(db, org, data["orderTypes"])
    return data

def refresh_discount_types(db: Session, org_id: int, key_id: int):
    token = get_token(db, key_id)
    org = read_exact_organization(db, org_id)
    data = api.fetch_discount_types(token, org.organization_id)
    update_discount_types(db, org, data["discounts"])
    return data

def pass_essentials_api_keys(db: Session):
    api_keys = read_api_keys(db)
    return [{"id": key.id, "description": key.description} for key in api_keys]

def pass_organizations(db: Session, key_id: int):
    organizations = read_organizations(db, key_id)
    return organizations

def pass_terminals(db: Session, org_id: int):
    terminals = read_terminals(db, org_id)
    return terminals

def pass_payment_types(db: Session, org_id: int):
    payment_types = read_payment_types(db, org_id)
    return payment_types

def pass_order_types(db: Session, org_id: int):
    order_types = read_order_types(db, org_id)
    return order_types

def pass_discount_types(db: Session, org_id: int):
    discount_types = read_discount_types(db, org_id)
    return discount_types