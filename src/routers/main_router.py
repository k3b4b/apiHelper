from functools import wraps
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.logger import logger

from src.core.rate_limit import request_is_limited
from src.db.database import get_db
from src.db import models
from src.services.main_service import download_nomenclature, get_token, pass_organizations, refresh_discount_types, refresh_order_types, refresh_organizations, refresh_payment_types, refresh_terminals, process_new_key, pass_entities
from src.services.db_service import delete_api_key, update_api_key_description
from src.core.token_management import delete_token as delete_cached_token

router = APIRouter(prefix="/api")

#------------------------------------------------------------------------------
# роутер на добавление новых апи ключей
@router.post("/add_api_key")
def add_api_key(api_key: str = Form(...),
                description: str = Form(None),
                db: Session = Depends(get_db)):
    try:
        masked = api_key[:4] + "****" + api_key[-4:]
        logger.info(f"Processing new API key: {masked} with description: {description}")
        process_new_key(api_key, description, db)
    except ValueError as e:
        logger.error(f"Error processing new API key: {e}")
        return HTMLResponse(f"<h3>Ошибка: {e}</h3><a href='/'>Назад</a>")
    return RedirectResponse("/", status_code=303)  # после добавления редирект на главную

#------------------------------------------------------------------------------
@router.post("/update_api_key/{key_id}")
def update_api_key_route(key_id: int, description: str = Form(...), db: Session = Depends(get_db)):
    description = description.strip()
    if not description:
        raise HTTPException(status_code=400, detail="Название ключа не может быть пустым")
    updated = update_api_key_description(db, key_id, description)
    if not updated:
        raise HTTPException(status_code=404, detail="API-ключ не найден")
    return {"id": updated.id, "description": updated.description}

@router.delete("/delete_api_key/{key_id}")
def delete_api_key_route(key_id: int, db: Session = Depends(get_db)):
    if not delete_api_key(db, key_id):
        raise HTTPException(status_code=404, detail="API-ключ не найден")
    delete_cached_token(key_id)
    return {"status": "ok"}

#------------------------------------------------------------------------------
# роутеры на вытягивание данных с базы
@router.get("/get_organizations/{key_id}")
def get_organizations_route(key_id: int, db: Session = Depends(get_db)):
    organizations = pass_entities(db, models.Organization, filters={"api_key_id": key_id}) or []
    logger.info(f"Successfully passed organization list for key_id {key_id}")
    org_list = [{"internal_id": org.id, "id": org.organization_id, "name": org.name} for org in organizations]
    return JSONResponse(content=org_list)

@router.post("/get_terminals/{org_id}", )
def get_terminals_route(org_id: int, db: Session = Depends(get_db)):
    terminals = pass_entities(db, models.Terminal, filters={"organization_id": org_id})
    term_list = [{"terminal_id": t.terminal_id, "name": t.name} for t in terminals]
    return JSONResponse(content=term_list)

@router.post("/get_payment_types/{org_id}")
def get_payment_types_route(org_id: int, db: Session = Depends(get_db)):
    payment_types = pass_entities(db, models.PaymentType, filters={"organization_id": org_id})
    pay_list = [{"payment_type_id": p.payment_type_id, "name": p.name, "payment_type_kind": p.payment_type_kind, "code": p.code} for p in payment_types]
    return JSONResponse(content=pay_list)

@router.post("/get_order_types/{org_id}")
def get_order_types_route(org_id: int, db: Session = Depends(get_db)):
    order_types = pass_entities(db, models.OrderType, filters={"organization_id": org_id})
    order_list = [{"order_type_id": o.order_type_id, "name": o.name, "order_service_type": o.order_service_type} for o in order_types]
    return JSONResponse(content=order_list)

@router.post("/get_discount_types/{org_id}")
def get_discount_types_route(org_id: int, db: Session = Depends(get_db)):
    discount_types = pass_entities(db, models.DiscountType, filters={"organization_id": org_id})
    discount_list = [{"discount_type_id": d.discount_type_id, "name": d.name} for d in discount_types]
    return JSONResponse(content=discount_list)

#------------------------------------------------------------------------------
# роутеры на обновление данных c апи
@router.get("/update_organizations/{key_id}")
def update_organizations_route(key_id: int, db: Session = Depends(get_db)):
    if request_is_limited("update_organizations", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_organizations(db, key_id)
    return {"status": "ok", "message": "Организации загружены"}

@router.get("/get/nomenclature/{key_id}/{org_id}")
def get_nomenclature_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("get_nomenclature", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    return download_nomenclature(db, org_id, key_id)

@router.post("/refresh_terminals/{key_id}/{org_id}")
def refresh_terminals_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("refresh_terminals", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_terminals(db, org_id, key_id)
    return {"status": "ok", "message": "Терминалы обновлены"}

@router.post("/refresh_payment_types/{key_id}/{org_id}")
def refresh_payment_types_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("refresh_payment_types", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_payment_types(db, org_id, key_id)
    return {"status": "ok", "message": "Типы оплат обновлены"}

@router.post("/refresh_order_types/{key_id}/{org_id}")
def refresh_order_types_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("refresh_order_types", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_order_types(db, org_id, key_id)
    return {"status": "ok", "message": "Типы заказов обновлены"}

@router.post("/refresh_discount_types/{key_id}/{org_id}")
def refresh_discount_types_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("refresh_discount_types", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_discount_types(db, org_id, key_id)
    return {"status": "ok", "message": "Типы скидок обновлены"}

@router.post("/refresh_all/{key_id}/{org_id}")
def refresh_all_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    if request_is_limited("refresh_all", key_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    refresh_terminals(db, org_id, key_id)
    refresh_payment_types(db, org_id, key_id)
    refresh_order_types(db, org_id, key_id)
    refresh_discount_types(db, org_id, key_id)
    return {"status": "ok", "message": "Данные обновлены"}

