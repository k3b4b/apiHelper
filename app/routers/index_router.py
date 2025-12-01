from fastapi import APIRouter, Request, Depends
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db import models
from app.templates.templates import templates
from app.services.main_service import pass_essentials_api_keys

VERSION = "0.5.0"

router = APIRouter()

@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    api_keys = pass_essentials_api_keys(db)
    #organizations = db.query(models.Organization).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "api_keys": api_keys,
            "organizations": [],
            "version": VERSION
        }
    )
