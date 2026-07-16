from datetime import datetime, timedelta

from sqlalchemy import case, func
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

    def update_ai_result(self, contact_id: int, ai_result: str) -> None:
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact is not None:
            contact.ai_result = ai_result
            self.db.commit()

    def get_metrics(self) -> dict[str, int]:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        result = (
            self.db.query(
                func.count(Contact.id).label("total_contacts"),
                func.sum(case((Contact.ai_result == "positive", 1), else_=0)).label("positive"),
                func.sum(case((Contact.ai_result == "negative", 1), else_=0)).label("negative"),
            )
            .first()
        )

        today_result = (
            self.db.query(func.count(Contact.id).label("today"))
            .filter(Contact.created_at >= today_start, Contact.created_at < today_end)
            .first()
        )

        return {
            "total_contacts": int(result.total_contacts or 0),
            "today": int(today_result.today or 0),
            "positive": int(result.positive or 0),
            "negative": int(result.negative or 0),
        }
