from fastapi import HTTPException

from app.schemas.contact import ContactRequest
from app.services.contact_service import ContactService


class ContactController:
    def __init__(self, service: ContactService):
        self.service = service

    async def get_metrics(self) -> dict[str, int]:
        return await self.service.get_metrics()

    async def create_contact(self, data: ContactRequest) -> dict:
        return await self.service.create_contact(data)
