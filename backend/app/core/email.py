"""Email sending service — SMTP with async fallback to console in dev."""

from __future__ import annotations

import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_message(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> MIMEMultipart:
    """Build a multipart email message."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _send_sync(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> None:
    """Synchronously send an email via SMTP."""
    msg = _build_message(to_email, subject, html_body, text_body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        logger.info("Email sent to %s (subject: %s)", to_email, subject)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        raise


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> None:
    """Send an email. In development without SMTP config, log to console."""
    if not settings.smtp_host or not settings.email_verification_enabled:
        logger.info(
            "[DEV EMAIL] To: %s | Subject: %s\n%s",
            to_email,
            subject,
            html_body,
        )
        return

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _send_sync,
        to_email,
        subject,
        html_body,
        text_body,
    )


def build_verification_email(to_email: str, token: str) -> tuple[str, str, str]:
    """Build subject, text_body, html_body for email verification.

    Returns (subject, text_body, html_body).
    """
    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    subject = "Verify your email — Trainer Platform"

    text_body = (
        f"Welcome to Trainer Platform!\n\n"
        f"Please verify your email address by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in {settings.email_verification_token_expire_hours} hours.\n\n"
        f"If you did not register, you can ignore this email."
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 40px 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 32px;">
    <h2 style="margin-top: 0; color: #1a1a2e;">Welcome to Trainer Platform</h2>
    <p style="color: #555; line-height: 1.6;">
      Please verify your email address to access the simulator.
    </p>
    <a href="{verify_url}"
       style="display: inline-block; background: #6c5ce7; color: #fff; text-decoration: none;
              padding: 12px 28px; border-radius: 8px; font-weight: bold; margin: 16px 0;">
      Verify Email
    </a>
    <p style="color: #999; font-size: 13px; margin-top: 24px;">
      This link expires in {settings.email_verification_token_expire_hours} hours.
      If you did not register, you can ignore this email.
    </p>
  </div>
</body>
</html>"""

    return subject, text_body, html_body
