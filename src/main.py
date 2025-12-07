from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.db.init_db import init_db
from src.routers import index_router, main_router
from src.core.logger import logger

logger.info("Starting apiHelper application...")
apiHelper = FastAPI()

@apiHelper.on_event("startup")
def startup():
    init_db()

apiHelper.mount("/static", StaticFiles(directory="src/static"), name="static")

apiHelper.include_router(index_router.router)
apiHelper.include_router(main_router.router)
logger.info("apiHelper application started.")
