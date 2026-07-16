from fastapi import HTTPException

from app.schemas.contact import ContactRequest
from app.services.contact_service import ContactService


class ContactController:
    def __init__(self, service: ContactService):
        self.service = service

    def create_contact(self, data: ContactRequest) -> dict:
        try:
            return self.service.create_contact(data)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
