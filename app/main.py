from fastapi import FastAPI

from app.core.logging import configure_logging
from app.interfaces.api.routes import router

configure_logging()

app = FastAPI(title="HRM Automation AI", version="0.1.0")
app.include_router(router)
