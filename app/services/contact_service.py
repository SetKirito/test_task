from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactRequest


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    def create_contact(self, data: ContactRequest) -> dict:
        contact = self.repository.create(
            name=data.name,
            email=str(data.email),
            phone=data.phone,
            comment=data.comment,
        )
        return {
            "success": True,
            "id": contact.id,
        }
