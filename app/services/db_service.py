from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models

TOKEN_TTL = 3600 # TTL токена, 3600 сек или 1 час

# проверка свежести токена в бд
def check_token(db: Session, api_key_obj: models.ApiKey):
    now = datetime.utcnow()
    if api_key_obj.access_token and api_key_obj.token_ttl and api_key_obj.token_ttl > now:
        return api_key_obj.access_token
    return None
    
# обновление токена в бд
def update_token(db: Session, api_key_obj: models.ApiKey, new_token: str): 
    api_key_obj.access_token = new_token
    api_key_obj.token_ttl = datetime.utcnow() + timedelta(seconds=TOKEN_TTL)
    db.commit()
    db.refresh(api_key_obj)

def create_api_key(db: Session, api_key: str, description: str):
    new_key = models.ApiKey(api_key=api_key, description=description)
    db.add(new_key)
    db.commit()
    db.refresh(new_key)

# обновление организаций
def update_organizations(db: Session, api_key_obj: models.ApiKey, organizations: list[dict]):
    for org in organizations:
        org_id = org["id"]
        org_name = org.get("name")

        existing = (
            db.query(models.Organization)
            .filter_by(api_key_id=api_key_obj.id, organization_id=org_id)
            .first()
        )

        # --- 1. CREATE ---
        if not existing:
            new_org = models.Organization(
                api_key_id=api_key_obj.id,
                organization_id=org_id,
                name=org_name,
            )
            db.add(new_org)
            continue

        # --- 2. UPDATE (если изменилось имя) ---
        if existing.name != org_name:
            existing.name = org_name

    db.commit()

def update_terminals(db: Session, organization_obj: models.Organization, terminal_groups: list[dict]):
    for group in terminal_groups:
        for terminal in group["items"]:
            terminal_id = terminal["id"]
            terminal_name = terminal.get("name")

            existing = (
                db.query(models.Terminal)
                .filter_by(organization_id=organization_obj.id, terminal_id=terminal_id)
                .first()
            )

            if not existing:
                new_terminal = models.Terminal(
                    organization_id=organization_obj.id,
                    terminal_id=terminal_id,
                    name=terminal_name,
                )
                db.add(new_terminal)
                continue

            if existing.name != terminal_name:
                existing.name = terminal_name

    db.commit()

def update_payment_types(db: Session, organization_obj: models.Organization, payment_types: list[dict]):
    for payment_type in payment_types:
        payment_type_id = payment_type["id"]
        payment_type_name = payment_type.get("name")
        payment_type_kind = payment_type.get("paymentTypeKind")
        payment_type_code = payment_type.get("code")

        existing = (
            db.query(models.PaymentType)
            .filter_by(organization_id=organization_obj.id, payment_type_id=payment_type_id)
            .first()
        )
        if not existing:
            new_payment_type = models.PaymentType(
                organization_id=organization_obj.id,
                payment_type_id=payment_type_id,
                name=payment_type_name,
                payment_type_kind=payment_type_kind,
                code=payment_type_code,
            )
            db.add(new_payment_type)
            continue

        if existing.name != payment_type_name:
            existing.name = payment_type_name

    db.commit()

def update_order_types(db: Session, organization_obj: models.Organization, order_types: list[dict]):
    for group in order_types:
        for order_type in group.get("items", []):
            order_type_id = order_type["id"]
            order_type_name = order_type.get("name")
            order_service_type = order_type.get("orderServiceType")
            
            existing = (
                db.query(models.OrderType)
                .filter_by(organization_id=organization_obj.id, order_type_id=order_type_id)
                .first()
            )

            if existing:
                # UPDATE
                if existing.name != order_type_name:
                    existing.name = order_type_name
            else:
                # CREATE
                new_order_type = models.OrderType(
                    organization_id=organization_obj.id,
                    order_type_id=order_type_id,
                    name=order_type_name,
                    order_service_type=order_service_type,
                )
                db.add(new_order_type)

    db.commit()


def update_discount_types(db: Session, organization_obj: models.Organization, discount_types: list[dict]):
    for group in discount_types:
        for discount_type in group.get("items", []):
            discount_type_id = discount_type["id"]
            discount_type_name = discount_type.get("name")

            existing = (
                db.query(models.DiscountType)
                .filter_by(organization_id=organization_obj.id, discount_type_id=discount_type_id)
                .first()
            )

            if existing:
                # UPDATE
                if existing.name != discount_type_name:
                    existing.name = discount_type_name
            else:
                # CREATE
                new_discount_type = models.DiscountType(
                    organization_id=organization_obj.id,
                    discount_type_id=discount_type_id,
                    name=discount_type_name,
                )
                db.add(new_discount_type)

    db.commit()


def read_api_keys(db: Session):
    return db.query(models.ApiKey).all()

def check_exact_key(db: Session, api_key: str):
    return db.query(models.ApiKey).filter(models.ApiKey.api_key == api_key).first()

def read_exact_key(db: Session, key_id: int):
    return db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()

def read_exact_organization(db: Session, org_id: int):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def read_organizations(db: Session, key_id: int):
    return db.query(models.Organization).filter(models.Organization.api_key_id == key_id).all()

def read_terminals(db: Session, org_id: int):
    result = db.query(models.Terminal).filter(models.Terminal.organization_id == org_id).all()
    return result

def read_payment_types(db: Session, org_id: int):
    result = db.query(models.PaymentType).filter(models.PaymentType.organization_id == org_id).all()
    return result

def read_order_types(db: Session, org_id: int):
    result = db.query(models.OrderType).filter(models.OrderType.organization_id == org_id).all()
    print(org_id)
    print("read_order_types:", result)
    return result

def read_discount_types(db: Session, org_id: int):
    return db.query(models.DiscountType).filter(models.DiscountType.organization_id == org_id).all()
 

