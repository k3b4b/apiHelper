from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db import models
from typing import List, Dict, Callable, Optional, Type
from src.core.logger import logger
from src.core.config import TOKEN_TTL
from src.core.cryptography import encrypt_entity

# проверка свежести токена в бд
def check_token(db: Session, api_key_obj: models.ApiKey):
    logger.debug(f"Checking token for API key ID {api_key_obj.id}")
    now = datetime.utcnow()
    if api_key_obj.access_token and api_key_obj.token_ttl and api_key_obj.token_ttl > now:
        logger.debug(f"Token is valid for API key ID {api_key_obj.id}, expires at {api_key_obj.token_ttl.isoformat()}")
        return api_key_obj.access_token
    logger.debug(f"Token is invalid or expired for API key ID {api_key_obj.id}")
    return None
    
# обновление токена в бд
def update_token(db: Session, api_key_obj: models.ApiKey, new_token: str): 
    try:
        api_key_obj.access_token = encrypt_entity(new_token)
        api_key_obj.token_ttl = datetime.utcnow() + timedelta(seconds=TOKEN_TTL)
        db.commit()
        db.refresh(api_key_obj)
        logger.success(f"Updated token for API key ID {api_key_obj.id}")
    except SQLAlchemyError as e:
        # тут чекнуть может ли в исключении засветиться токен
        logger.exception(f"Failed to update token for API key ID {api_key_obj.id}: {str(e)}")
        db.rollback()
        raise

# создание новой записи с апи ключом
def create_api_key(db: Session, api_key: str, description: str):
    try:
        new_key = models.ApiKey(api_key=encrypt_entity(api_key), description=description)
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        logger.success(f"API key saved with ID {new_key.id}")
    except SQLAlchemyError as e:
        masked = f"***{api_key[-5:]}"
        logger.exception(f"Failed to create API key {masked}: {str(e)}")
        db.rollback()
        raise

def update_api_key_description(db: Session, key_id: int, description: str):
    try:
        api_key_obj = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
        if not api_key_obj:
            return None
        api_key_obj.description = description
        db.commit()
        db.refresh(api_key_obj)
        logger.success(f"Updated description for API key ID {key_id}")
        return api_key_obj
    except SQLAlchemyError as e:
        logger.exception(f"Failed to update description for API key ID {key_id}: {str(e)}")
        db.rollback()
        raise

def delete_api_key(db: Session, key_id: int) -> bool:
    try:
        api_key_obj = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
        if not api_key_obj:
            return False

        organization_ids = [org.id for org in api_key_obj.organizations]
        if organization_ids:
            for model in (models.Terminal, models.OrderType, models.PaymentType, models.DiscountType):
                db.query(model).filter(model.organization_id.in_(organization_ids)).delete(synchronize_session=False)
            db.query(models.Organization).filter(models.Organization.id.in_(organization_ids)).delete(synchronize_session=False)
            db.expire(api_key_obj, ["organizations"])

        db.query(models.ApiAccess).filter(models.ApiAccess.api_key_id == key_id).delete(synchronize_session=False)
        db.delete(api_key_obj)
        db.commit()
        logger.success(f"Deleted API key ID {key_id}")
        return True
    except SQLAlchemyError as e:
        logger.exception(f"Failed to delete API key ID {key_id}: {str(e)}")
        db.rollback()
        raise

# универальный апсер для любых таблиц
def upsert_entities(db: Session, model: Type, data_list: List[Dict], get_filter: Callable[[Dict], Dict], update_fields: List[str], field_map: Dict[str, str] = None):
    logger.debug(f"Starting UPSERT for model {model.__name__}. Items: {len(data_list)}")
    try:
        for data in data_list:
            if field_map:
                data = {field_map.get(k, k): v for k, v in data.items()}
            filters = get_filter(data)
            existing = db.query(model).filter_by(**filters).first()
            if existing:
                for field in update_fields:
                    new_value = data.get(field)
                    if new_value is not None and getattr(existing, field) != new_value:
                        setattr(existing, field, new_value)
            else:
                record = {**filters, **{f: data.get(f) for f in update_fields}}
                db.add(model(**record))
        db.commit()
        logger.success(f"UPSERT completed for model {model.__name__}")
    except SQLAlchemyError as e:
        logger.exception(f"UPSERT failed for model {model.__name__}: {str(e)}. Rolling back.")
        db.rollback()
        raise

# читалка из бд с возможностью фильтрации и выбора одной или всех записей
def read_entities(db: Session, model: Type, filters: Optional[Dict] = None, single: bool = False) -> Optional[List]:
    logger.debug(
        f"Reading {model.__name__}: filters={filters}, single={single}"
    )
    try:
        query = db.query(model)
        if filters:
            query = query.filter_by(**filters)
        result = query.first() if single else query.all()
        logger.debug(
            f"Read complete: returned {1 if single else len(result)} items."
        )
        return result
    except SQLAlchemyError as e:
        logger.exception(f"Read failed for model {model.__name__}: {str(e)}")
        raise
    
#----------------------------------------------------------------------
# работа с юзерами

 

