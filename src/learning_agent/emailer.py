import smtplib
from email.message import EmailMessage

from .config import Settings


def send_html_email(settings: Settings, subject: str, html: str) -> None:
    required = [settings.recipient_email, settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.smtp_from_email]
    if not all(required):
        raise ValueError("Email configuration is incomplete. Fill the SMTP and recipient values in .env.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = settings.recipient_email
    message.set_content("Your daily lesson is best viewed in an HTML-capable email client.")
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
