from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import index_router, main_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(index_router.router)
app.include_router(main_router.router)
