"""Application configuration via pydantic-settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "TrainerPlatform"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-random-secret-key-in-production"
    request_id_header: str = "X-Request-ID"

    # Database
    database_url: str = "postgresql+asyncpg://trainer:trainer_pass@localhost:5432/trainer_platform"
    database_sync_url: str = "postgresql://trainer:trainer_pass@localhost:5432/trainer_platform"

    # Auth
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    # AI Gateway
    ai_gateway_provider: str = "mock"
    ai_gateway_api_key: Optional[str] = None
    ai_gateway_model: str = "gpt-4o-mini"
    ai_gateway_timeout_seconds: int = 30
    ai_gateway_max_retries: int = 1
    ai_gateway_fallback_placeholder_enabled: bool = True

    # OpenAI
    openai_api_key: Optional[str] = None

    # Analytics
    analytics_enabled: bool = True

    # Feature flags
    ff_trainer_qa_interview_visible: bool = True
    ff_trainer_qa_interview_enrollment_enabled: bool = True
    ff_scenario_runtime_enabled: bool = True
    ff_ai_evaluation_enabled: bool = True
    ff_ai_evaluation_real_provider_enabled: bool = False
    ff_analytics_enabled: bool = True
    ff_locale_en_us_enabled: bool = True
    ff_beta_access_enabled: bool = False

    # Localization
    default_locale: str = "ru-RU"
    fallback_locale: str = "en-US"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Admin
    admin_api_key: str = "change-me-admin-key"


settings = Settings()

# Resolve paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGES_DIR = ROOT_DIR.parent / "trainer_packages"
