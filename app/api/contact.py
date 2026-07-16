from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.controllers.contact_controller import ContactController
from app.core.database import SessionLocal
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactRequest
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.core.config import settings

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_contact_controller(db: Session = Depends(get_db)) -> ContactController:
    repository = ContactRepository(db)
    service = ContactService(repository, ai_service=AIService(), email_service=EmailService())
    return ContactController(service)


@router.get("/api/health", summary="Health check", description="Returns service health status for database and AI readiness.")
async def health(db: Session = Depends(get_db)):
    database_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    ai_service = AIService()
    ai_status = "available" if ai_service.ping() else "degraded"

    return {
        "status": "ok",
        "database": database_status,
        "ai": ai_status,
    }


@router.get("/api/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    repository = ContactRepository(db)
    service = ContactService(repository, ai_service=AIService(), email_service=EmailService())
    controller = ContactController(service)
    return await controller.get_metrics()


@router.post(
    "/api/contact",
    status_code=201,
    summary="Create contact request",
    description="Creates a contact message, stores it in the database, runs AI sentiment analysis, and schedules email notifications.",
)
async def create_contact(
    data: ContactRequest,
    background_tasks: BackgroundTasks,
    controller: ContactController = Depends(get_contact_controller),
):
    result = await controller.create_contact(data)

    try:
        email_service = controller.service.email_service
        background_tasks.add_task(
            email_service.send_contact_notification_async,
            name=data.name,
            phone=data.phone,
            email=str(data.email),
            comment=data.comment,
        )
        background_tasks.add_task(
            email_service.send_thank_you_email_async,
            email=str(data.email),
        )
    except Exception:
        pass

    return result
