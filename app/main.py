import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.logger_config import setup_logging
from app.api.routes import router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="TravelAgent — Подбор туров")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)


@app.on_event("startup")
async def on_startup():
    logger.info("Application started")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown")
