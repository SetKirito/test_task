import asyncio

from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactRequest
from app.services.ai_service import AIService
from app.services.email_service import EmailService


class ContactService:
    def __init__(self, repository: ContactRepository, ai_service: AIService | None = None, email_service: EmailService | None = None):
        self.repository = repository
        self.ai_service = ai_service or AIService()
        self.email_service = email_service or EmailService()

    async def get_metrics(self) -> dict[str, int]:
        return await asyncio.to_thread(self.repository.get_metrics)

    async def create_contact(self, data: ContactRequest) -> dict:
        contact = await asyncio.to_thread(
            self.repository.create,
            name=data.name,
            email=str(data.email),
            phone=data.phone,
            comment=data.comment,
        )

        ai_result = await self.ai_service.analyze_async(text=data.comment)
        await asyncio.to_thread(self.repository.update_ai_result, contact.id, ai_result["sentiment"])

        return {
            "success": True,
            "id": contact.id,
            "ai": ai_result,
        }
