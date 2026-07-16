from sqlalchemy.orm import Session

from app.models.contact import Contact


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, name: str, email: str, phone: str, comment: str) -> Contact:
        contact = Contact(
            name=name,
            email=email,
            phone=phone,
            comment=comment,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact
