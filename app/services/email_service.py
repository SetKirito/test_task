import asyncio
import smtplib
from email.message import EmailMessage

from app.core.logging import error_logger
from app.core.config import settings


class EmailService:
    def __init__(self) -> None:
        self.smtp_host = settings.SMTP_HOST or ""
        self.smtp_port = int(settings.SMTP_PORT or 587)
        self.smtp_user = settings.SMTP_USER or ""
        self.smtp_password = settings.SMTP_PASSWORD or ""
        self.owner_email = settings.OWNER_EMAIL or "owner@example.com"
        self.smtp_timeout = 5
        self.smtp_use_ssl = bool(settings.SMTP_USE_SSL)

    async def send_contact_notification_async(self, *, name: str, phone: str, email: str, comment: str) -> bool:
        return await asyncio.to_thread(self.send_contact_notification, name=name, phone=phone, email=email, comment=comment)

    async def send_thank_you_email_async(self, *, email: str) -> bool:
        return await asyncio.to_thread(self.send_thank_you_email, email=email)

    def _send_message(self, msg: EmailMessage) -> None:
        if not self.smtp_host:
            raise ValueError("SMTP host is not configured")

        attempts = []
        if self.smtp_use_ssl:
            attempts.append((True, 465))
        attempts.append((False, self.smtp_port))

        last_error: Exception | None = None
        for use_ssl, port in attempts:
            try:
                if use_ssl:
                    with smtplib.SMTP_SSL(self.smtp_host, port, timeout=self.smtp_timeout) as smtp:
                        if self.smtp_user and self.smtp_password:
                            smtp.login(self.smtp_user, self.smtp_password)
                        smtp.send_message(msg)
                else:
                    with smtplib.SMTP(self.smtp_host, port, timeout=self.smtp_timeout) as smtp:
                        smtp.starttls()
                        if self.smtp_user and self.smtp_password:
                            smtp.login(self.smtp_user, self.smtp_password)
                        smtp.send_message(msg)
                return
            except Exception as exc:
                last_error = exc
                error_logger.warning("SMTP attempt failed via port %s: %s", port, exc)

        if last_error is not None:
            raise last_error

    def send_contact_notification(self, *, name: str, phone: str, email: str, comment: str) -> bool:
        if not self.smtp_host:
            error_logger.warning("SMTP not configured; skipping owner email")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = "Новая заявка"
            msg["From"] = self.smtp_user or self.owner_email
            msg["To"] = self.owner_email
            msg.set_content(
                f"Новая заявка\n\n"
                f"Имя: {name}\n"
                f"Телефон: {phone}\n"
                f"Email: {email}\n"
                f"Комментарий: {comment}"
            )
            self._send_message(msg)
            return True
        except Exception as exc:
            error_logger.exception("Failed to send owner email: %s", exc)
            return False

    def send_thank_you_email(self, *, email: str) -> bool:
        if not self.smtp_host:
            error_logger.warning("SMTP not configured; skipping user email")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = "Спасибо за обращение"
            msg["From"] = self.smtp_user or self.owner_email
            msg["To"] = email
            msg.set_content("Спасибо за обращение.\n\nМы получили вашу заявку.")
            self._send_message(msg)
            return True
        except Exception as exc:
            error_logger.exception("Failed to send thank-you email: %s", exc)
            return False
