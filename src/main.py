from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routers import index_router, main_router

apiHelper = FastAPI()

apiHelper.mount("/static", StaticFiles(directory="src/static"), name="static")

apiHelper.include_router(index_router.router)
apiHelper.include_router(main_router.router)
