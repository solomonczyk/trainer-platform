"""Email sending service — abstract sender, SMTP real sender, in-memory fake sender.

Usage (production):
    from app.core.email import send_email
    await send_email(to, subject, html, text)

Usage (tests):
    from app.core.email import set_email_sender, InMemoryEmailSender
    sender = InMemoryEmailSender()
    set_email_sender(sender)
    # ... run test ...
    assert sender.sent_count == 1
    assert sender.sent_emails[0]["to"] == "user@example.com"
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Email normalization helper — single canonical function used everywhere
# ---------------------------------------------------------------------------

def normalize_email(email: str) -> str:
    """Canonical email normalization: strip whitespace and lowercase."""
    return email.strip().lower()


# ---------------------------------------------------------------------------
# Fake / test domains that must never receive real SMTP emails
# ---------------------------------------------------------------------------

BLOCKED_REAL_SMTP_DOMAINS: set[str] = {
    "test.com",
    "example.com",
    "example.org",
    "example.net",
    "invalid",
    "localhost",
}


def is_blocked_test_email(email: str) -> bool:
    """Return True if the email domain is a known test/fake domain.

    This is a safety guard to prevent real SMTP sends in staging/test
    environments from reaching fake addresses.
    """
    domain = email.split("@")[-1].lower().strip()
    if domain in BLOCKED_REAL_SMTP_DOMAINS:
        return True
    if domain.endswith(".test"):
        return True
    return False


# ---------------------------------------------------------------------------
# Abstract sender
# ---------------------------------------------------------------------------

class EmailSender:
    """Abstract email sender. Subclasses must implement send()."""

    async def send(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Real SMTP sender (production / staging)
# ---------------------------------------------------------------------------

class RealSmtpEmailSender(EmailSender):
    """Sends email via SMTP with safety guard for fake domains."""

    def _build_message(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        return msg

    def _send_sync(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> None:
        msg = self._build_message(to_email, subject, html_body, text_body)
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
            logger.info("Email sent to %s (subject: %s)", _mask_email(to_email), subject)
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", _mask_email(to_email), exc)
            raise

    async def send(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> None:
        """Send email via SMTP, blocking fake domains in staging/test environments."""
        # Safety guard: block fake/test domains in staging/test
        if settings.app_env in {"staging", "test"} and is_blocked_test_email(to_email):
            domain = to_email.split("@")[-1]
            logger.warning(
                "Blocked real verification email to test/fake domain",
                extra={"domain": domain},
            )
            return

        if not settings.smtp_host or not settings.email_verification_enabled:
            logger.info(
                "[DEV EMAIL] To: %s | Subject: %s\n%s",
                to_email,
                subject,
                html_body,
            )
            return

        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._send_sync,
            to_email,
            subject,
            html_body,
            text_body,
        )


# ---------------------------------------------------------------------------
# In-memory fake sender (tests)
# ---------------------------------------------------------------------------

class InMemoryEmailSender(EmailSender):
    """Captures sent emails in memory for test assertions.

    Usage:
        sender = InMemoryEmailSender()
        set_email_sender(sender)
        # ... run test ...
        assert sender.sent_count == 1
        assert sender.sent_emails[0]["to"] == "user@example.com"
    """

    def __init__(self) -> None:
        self.sent_emails: list[dict] = []

    async def send(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> None:
        self.sent_emails.append({
            "to": to_email,
            "subject": subject,
            "html": html_body,
            "text": text_body,
        })

    @property
    def sent_count(self) -> int:
        return len(self.sent_emails)

    def reset(self) -> None:
        self.sent_emails.clear()


# ---------------------------------------------------------------------------
# Module-level sender — default to real SMTP, can be overridden for tests
# ---------------------------------------------------------------------------

_sender: EmailSender = RealSmtpEmailSender()


def set_email_sender(sender: EmailSender) -> None:
    """Override the module-level email sender (used in tests)."""
    global _sender
    _sender = sender


def get_email_sender() -> EmailSender:
    """Return the current module-level email sender."""
    return _sender


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> None:
    """Send an email using the configured sender.

    This is the canonical send function used throughout the app.
    """
    await _sender.send(to_email, subject, html_body, text_body)


# ---------------------------------------------------------------------------
# Verification email builder with localization
# ---------------------------------------------------------------------------

VERIFICATION_EMAIL_TEMPLATES: dict[str, dict[str, str]] = {
    "ru-RU": {
        "subject": "Подтвердите email — Trainer Platform",
        "text_body_template": (
            "Добро пожаловать в Trainer Platform!\n\n"
            "Пожалуйста, подтвердите ваш email, перейдя по ссылке ниже:\n\n"
            "{verify_url}\n\n"
            "Ссылка действительна в течение {expire_hours} часов.\n\n"
            "Если вы не регистрировались, просто проигнорируйте это письмо."
        ),
        "button_text": "Подтвердить Email",
        "html_body_template": """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 40px 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 32px;">
    <h2 style="margin-top: 0; color: #1a1a2e;">Добро пожаловать в Trainer Platform</h2>
    <p style="color: #555; line-height: 1.6;">
      Пожалуйста, подтвердите ваш email, чтобы получить доступ к тренажёру.
    </p>
    <a href="{verify_url}"
       style="display: inline-block; background: #6c5ce7; color: #fff; text-decoration: none;
              padding: 12px 28px; border-radius: 8px; font-weight: bold; margin: 16px 0;">
      Подтвердить Email
    </a>
    <p style="color: #999; font-size: 13px; margin-top: 24px;">
      Ссылка действительна в течение {expire_hours} часов.
      Если вы не регистрировались, просто проигнорируйте это письмо.
    </p>
  </div>
</body>
</html>""",
    },
    "en-US": {
        "subject": "Verify your email — Trainer Platform",
        "text_body_template": (
            "Welcome to Trainer Platform!\n\n"
            "Please verify your email address by clicking the link below:\n\n"
            "{verify_url}\n\n"
            "This link expires in {expire_hours} hours.\n\n"
            "If you did not register, you can ignore this email."
        ),
        "button_text": "Verify Email",
        "html_body_template": """<!DOCTYPE html>
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
      This link expires in {expire_hours} hours.
      If you did not register, you can ignore this email.
    </p>
  </div>
</body>
</html>""",
    },
}


def build_verification_email(
    to_email: str,
    token: str,
    locale: str = "ru-RU",
) -> tuple[str, str, str]:
    """Build subject, text_body, html_body for email verification.

    Uses locale-specific templates. Falls back to en-US if locale is unknown.

    Returns (subject, text_body, html_body).
    """
    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    template = VERIFICATION_EMAIL_TEMPLATES.get(locale) or VERIFICATION_EMAIL_TEMPLATES["en-US"]

    subject = template["subject"]
    text_body = template["text_body_template"].format(
        verify_url=verify_url,
        expire_hours=settings.email_verification_token_expire_hours,
    )
    html_body = template["html_body_template"].format(
        verify_url=verify_url,
        expire_hours=settings.email_verification_token_expire_hours,
    )

    return subject, text_body, html_body


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask_email(email: str) -> str:
    """Mask email for safe logging (show domain only)."""
    parts = email.split("@")
    if len(parts) == 2:
        local, domain = parts
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"
    return "***@" + email.split("@")[-1] if "@" in email else "***"
