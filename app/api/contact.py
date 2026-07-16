from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.contact_controller import ContactController
from app.database import SessionLocal
from app.schemas.contact import ContactRequest
from app.services.contact_service import ContactService
from app.repositories.contact_repository import ContactRepository

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/health")
def health():
    return {"status": "ok"}


@router.post("/api/contact")
def create_contact(data: ContactRequest, db: Session = Depends(get_db)):
    repository = ContactRepository(db)
    service = ContactService(repository)
    controller = ContactController(service)
    return controller.create_contact(data)
