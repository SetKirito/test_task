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


@router.get("/api/health")
async def health(db: Session = Depends(get_db)):
    status = {"status": "ok"}
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception:
        status["database"] = "unavailable"

    ai_service = AIService()
    status["ai"] = "available" if ai_service.ping() else "unavailable"

    return status


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    repository = ContactRepository(db)
    service = ContactService(repository, ai_service=AIService(), email_service=EmailService())
    controller = ContactController(service)
    return await controller.get_metrics()


@router.post("/api/contact", status_code=201)
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
