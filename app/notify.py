import smtplib
from email.message import EmailMessage

from .config import settings


def send_enquiry_email(name: str, email: str, topic: str, message: str) -> None:
    """Email the author about a new enquiry. Does nothing if SMTP is not configured."""
    if not (settings.smtp_host and settings.notify_to):
        return
    msg = EmailMessage()
    msg["Subject"] = f"New website enquiry: {topic}"
    msg["From"] = settings.smtp_user or settings.notify_to
    msg["To"] = settings.notify_to
    msg["Reply-To"] = email
    msg.set_content(f"From: {name} <{email}>\nTopic: {topic}\n\n{message}")
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    except Exception as exc:  # never break the visitor's request because email failed
        print(f"[notify] email failed: {exc}")
