from fastapi import APIRouter, Request, Depends
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db import models
from src.templates.templates import templates
from src.services.main_service import pass_essentials_api_keys
from src.core.config import RATE_LIMIT_SECONDS

VERSION = "1.0.0"

router = APIRouter()

# роутер основной страницы - передаёт в неё список ключей (ВНУТРЕННИЕ АЙДИ и названия)
@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    api_keys = pass_essentials_api_keys(db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "api_keys": api_keys,
            "organizations": [],
            "version": VERSION,
            "timeout_seconds": RATE_LIMIT_SECONDS
        }
    )
