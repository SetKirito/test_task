from fastapi import FastAPI

from app.api.contact import router as contact_router
from app.core.config import settings
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)
app.include_router(contact_router)
