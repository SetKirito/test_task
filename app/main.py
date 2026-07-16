from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.contact import router as contact_router
from app.core.config import settings
from app.core.database import lifespan
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limiter import RateLimitMiddleware

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, limit=settings.RATE_LIMIT, window_seconds=settings.RATE_WINDOW)
register_exception_handlers(app)
app.include_router(contact_router)
