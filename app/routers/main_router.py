from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.limits import limit_api_calls
from app.db.database import get_db
from app.db import models
from app.services.main_service import download_nomenclature, get_token, pass_order_types, pass_organizations, pass_payment_types, pass_terminals, pass_discount_types, refresh_discount_types, refresh_order_types, refresh_organizations, refresh_payment_types, refresh_terminals, process_new_key
from app.core.redis import allow_request

router = APIRouter(prefix="/api")

@router.get("/get_token/{key_id}")
def api_get_token(key_id: int, db: Session = Depends(get_db)):
    token = get_token(db, key_id)
    if not token:
        return HTMLResponse("<tr><td colspan='2'>Ошибка: ключ API не найден или токен не получен</td></tr>")
    return {"token": token}

@router.get("/get_organizations/{key_id}")
def get_organizations_route(key_id: int, db: Session = Depends(get_db)):
    organizations = pass_organizations(db, key_id) or []
    #organizations = refresh_organizations(db, key_id)
    # добавить проверку на None
    org_list = [{"internal_id": org.id, "id": org.organization_id, "name": org.name} for org in organizations]
    return JSONResponse(content=org_list)

@router.get("/update_organizations/{key_id}",
            dependencies=[Depends(limit_api_calls())])
def update_organizations_route(key_id: int, db: Session = Depends(get_db)):
    data = refresh_organizations(db, key_id)
    return {"status": "ok", "message": "Организации загружены"}
    #return JSONResponse(content=data)

@router.get("/get/nomenclature/{key_id}/{org_id}", dependencies=[Depends(limit_api_calls())])
def get_nomenclature_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    return download_nomenclature(db, org_id, key_id)

@router.post("/get_terminals/{org_id}")
def get_terminals_route(org_id: int, db: Session = Depends(get_db)):
    terminals = pass_terminals(db, org_id)
    term_list = [{"terminal_id": t.terminal_id, "name": t.name} for t in terminals]
    return JSONResponse(content=term_list)

@router.post("/get_payment_types/{org_id}")
def get_payment_types_route(org_id: int, db: Session = Depends(get_db)):
    payment_types = pass_payment_types(db, org_id)
    pay_list = [{"payment_type_id": p.payment_type_id, "name": p.name, "payment_type_kind": p.payment_type_kind, "code": p.code} for p in payment_types]
    return JSONResponse(content=pay_list)

@router.post("/get_order_types/{org_id}")
def get_order_types_route(org_id: int, db: Session = Depends(get_db)):
    order_types = pass_order_types(db, org_id)
    order_list = [{"order_type_id": o.order_type_id, "name": o.name, "order_service_type": o.order_service_type} for o in order_types]
    print(f"DEBUG: order_list = {order_list}")
    return JSONResponse(content=order_list)

@router.post("/get_discount_types/{org_id}")
def get_discount_types_route(org_id: int, db: Session = Depends(get_db)):
    discount_types = pass_discount_types(db, org_id)
    discount_list = [{"discount_type_id": d.discount_type_id, "name": d.name} for d in discount_types]
    return JSONResponse(content=discount_list)

@router.post("/refresh_all/{key_id}/{org_id}",
            dependencies=[Depends(limit_api_calls())])
def refresh_all_route(key_id: int, org_id: int, db: Session = Depends(get_db)):
    terminals = refresh_terminals(db, org_id, key_id)
    payment_types = refresh_payment_types(db, org_id, key_id)
    order_types = refresh_order_types(db, org_id, key_id)
    discount_types = refresh_discount_types(db, org_id, key_id)
    return {"status": "ok", "message": "Данные обновлены"}

@router.post("/add_api_key")
def add_api_key(api_key: str = Form(...),
                description: str = Form(None),
                db: Session = Depends(get_db)):
    try:
        process_new_key(api_key, description, db)
    except ValueError as e:
        return HTMLResponse(f"<h3>Ошибка: {e}</h3><a href='/'>Назад</a>")
    return RedirectResponse("/", status_code=303)  # После добавления редирект на главную


