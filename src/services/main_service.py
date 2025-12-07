from io import BytesIO
import json
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.db import models
from src.services.api_service import ApiService
from src.core.logger import logger
from typing import List, Dict, Optional, Type
from src.services.db_service import check_token, create_api_key, read_entities, update_token, upsert_entities
from src.core.cryptography import decrypt_entity
from src.core.token_management import get_token as redis_get_token, set_token as redis_set_token

# нюхаем токен в редисе, если нет - в бд, если просрочен - запрашиваем новый у апи и сохраняем в бд и редис
def get_token(db: Session, key_id: int) -> str:
    logger.debug(f"Request token for key_id={key_id}")
    cached_token = redis_get_token(key_id)
    if cached_token:
        logger.debug(f"Token found in cache. Returning cached token.")
        return cached_token
    logger.debug(f"Token not found in cache. Checking database...")
    api_key_obj = read_entities(db, models.ApiKey, filters={"id": key_id}, single=True)
    if not api_key_obj:
        logger.warning(f"API key with id={key_id} not found.")
        return None
    token = check_token(db, api_key_obj)
    if token:
        token = decrypt_entity(token)
        logger.debug(f"Token is fresh in database. Caching and returning token.")
        redis_set_token(key_id, token)
        return token
    logger.info(f"Token expired. Fetching a new one from API...")
    temp_api = ApiService()
    data = temp_api.fetch_token(decrypt_entity(api_key_obj.api_key))
    new_token = data["token"]
    masked = new_token[:5] + "..." + new_token[-5:]
    logger.info(f"New token received: {masked}")
    update_token(db, api_key_obj, new_token)
    redis_set_token(key_id, new_token)
    return new_token

# создаем экземпляр ApiService с нужным токеном
def get_api_client(db: Session, key_id: int) -> ApiService:
    logger.debug(f"Initializing ApiService for key_id={key_id}")
    token = get_token(db, key_id)
    api = ApiService(token=token)   # токен устанавливается в headers
    logger.debug(f"ApiService created with token.")
    return api

# обработка создания нового ключа
def process_new_key(api_key: str, description: str, db: Session):
    logger.info(f"Creating new API key description='{description}'")
    existing = read_entities(db, models.ApiKey, filters={"api_key": api_key}, single=True)
    if existing:
        logger.warning(f"[process_new_key] Duplicate key '{api_key}'. Rejecting.")
        raise ValueError(f"Ключ '{api_key}' уже существует")
    create_api_key(db, api_key, description)
    logger.success(f"API key successfully created.")

# разворачиваем json с вложенными списками в плоский список
def flatten_items(data: Dict, key: str, subkey: Optional[str] = None) -> List[Dict]:
    logger.debug(f"Flattening key='{key}', subkey='{subkey}'")
    items = data.get(key, [])
    flattened = []
    for item in items:
        if subkey:
            subitems = item.get(subkey, [])
            if isinstance(subitems, list):
                flattened.extend(subitems)
        else:
            flattened.append(item)
    logger.debug(f"Flattened {len(flattened)} items.")
    return flattened

# скачивание номенклатуры и отдача в виде файла
def download_nomenclature(db: Session, org_id: int, key_id: int):
    logger.info(f"Request nomenclature for org_id={org_id}, key_id={key_id}")
    api = get_api_client(db, key_id)
    org = read_entities(db, models.Organization, filters={"id": org_id}, single=True)
    data = api.fetch_nomenclature(org.organization_id)
    logger.debug(f"Nomenclature received, preparing response...")
    file_content = json.dumps(data, ensure_ascii=False, indent=2)
    file_bytes = BytesIO(file_content.encode("utf-8"))
    return StreamingResponse(
        file_bytes,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="nomenclature.txt"'}
    )

#----------------------------------------------------------------------
# обновление справочников из апи
def refresh_organizations(db: Session, key_id: int):
    logger.info(f"Updating organizations for key_id={key_id}")
    api = get_api_client(db, key_id)
    data = api.fetch_organizations()
    flat_organizations = flatten_items(data, "organizations")
    logger.debug(f"Upserting {len(flat_organizations)} organizations.")
    upsert_entities(db=db, model=models.Organization, data_list=flat_organizations, get_filter=lambda d: {"organization_id": d["id"], "api_key_id": key_id}, update_fields=["name"])
    logger.success("Organizations updated.")
    return data

def refresh_terminals(db: Session, org_id: int, key_id: int):
    logger.info(f"Updating terminals for org_id={org_id}, key_id={key_id}")
    api = get_api_client(db, key_id)
    org = read_entities(db, models.Organization, filters={"id": org_id}, single=True)
    data = api.fetch_terminals(org.organization_id)
    flat_terminals = flatten_items(data, "terminalGroups", "items")
    logger.debug(f"Upserting {len(flat_terminals)} terminals.")
    upsert_entities(db=db, model=models.Terminal, data_list=flat_terminals, get_filter=lambda d: {"terminal_id": d["id"], "organization_id": org.id}, update_fields=["name"])
    logger.success("Terminals updated.")
    return data

def refresh_payment_types(db: Session, org_id: int, key_id: int):
    logger.info(f"Updating payment types for org_id={org_id}, key_id={key_id}")
    api = get_api_client(db, key_id)
    org = read_entities(db, models.Organization, filters={"id": org_id}, single=True)
    data = api.fetch_payment_types(org.organization_id)
    flat_payment_types = flatten_items(data, "paymentTypes")
    field_map = {
        "id": "payment_type_id",
        "paymentTypeKind": "payment_type_kind"
    }
    logger.debug(f"Upserting {len(flat_payment_types)} payment types.")
    upsert_entities(db=db, model=models.PaymentType, data_list=flat_payment_types, get_filter=lambda d: {"payment_type_id": d["payment_type_id"], "organization_id": org.id}, update_fields=["name", "payment_type_kind", "code"], field_map=field_map)
    logger.success("Payment types updated.")
    return data

def refresh_order_types(db: Session, org_id: int, key_id: int):
    logger.info(f"Updating order types for org_id={org_id}, key_id={key_id}")
    api = get_api_client(db, key_id)
    org = read_entities(db, models.Organization, filters={"id": org_id}, single=True)
    data = api.fetch_order_types(org.organization_id)
    flat_order_types = flatten_items(data, "orderTypes", "items")
    field_map = {
        "id": "order_type_id",
        "orderServiceType": "order_service_type"
    }
    logger.debug(f"Upserting {len(flat_order_types)} order types.")
    upsert_entities(db=db, model=models.OrderType, data_list=flat_order_types, get_filter=lambda d: {"order_type_id": d["order_type_id"], "organization_id": org.id}, update_fields=["name", "order_service_type"], field_map=field_map)
    logger.success("Order types updated.")
    return data

def refresh_discount_types(db: Session, org_id: int, key_id: int):
    logger.info(f"Updating discount types for org_id={org_id}, key_id={key_id}")
    api = get_api_client(db, key_id)
    org = read_entities(db, models.Organization, filters={"id": org_id}, single=True)
    data = api.fetch_discount_types(org.organization_id)
    flat_discount_types = flatten_items(data, "discounts", "items")
    field_map = {
        "id": "discount_type_id"
    }
    logger.debug(f"Upserting {len(flat_discount_types)} discount types.")
    upsert_entities(db=db, model=models.DiscountType, data_list=flat_discount_types, get_filter=lambda d: {"discount_type_id": d["discount_type_id"], "organization_id": org.id}, update_fields=["name"], field_map=field_map)
    logger.success("Discount types updated.")
    return data


#----------------------------------------------------------------------
# простые пассеры для получения данных из бд. два нижних пока не трогал, остальные загнал в один универсальный
def pass_entities(db: Session, model: Type, filters: Optional[Dict] = None):
    logger.debug(f"model={model.__name__}, filters={filters}")
    return read_entities(db, model, filters = filters)

def pass_essentials_api_keys(db: Session):
    logger.debug("Fetching info of API keys.")
    api_keys = read_entities(db, models.ApiKey)
    return [{"id": key.id, "description": key.description} for key in api_keys]

def pass_organizations(db: Session, key_id: int):
    logger.debug(f"Fetching organizations for key_id={key_id}.")
    organizations = read_entities(db, models.Organization, filters={"api_key_id": key_id})
    return organizations
