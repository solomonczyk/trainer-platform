"""Shared test fixtures with per-test data cleanup.

Tables are created once per session.  Between tests, all rows are deleted
to provide isolation.  Each test gets its own file-based SQLite database
to avoid any cross-test contamination from connection pooling.
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.rate_limiter import reset_store
from app.db.base import Base
from app.db.session import get_db
import app.main as main_app_module
fastapi_app = main_app_module.app
from app.db.models import (
    User, UserProfile, Domain, TrainerProduct, Scenario, Rubric, RubricCriterion,
)
# Import certification-grade models so tables are created in test databases
import app.certification_core.models  # noqa: F401
from app.core.security import hash_password, create_access_token


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Disable rate limiter and clear its state before every test."""
    settings.rate_limit_enabled = False
    reset_store()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _make_db():
    """Create a fresh engine + session factory for one test."""
    fname = f"test_{uuid.uuid4().hex}.db"
    url = f"sqlite+aiosqlite:///{fname}"
    eng = create_async_engine(url, echo=False, poolclass=NullPool)
    sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    return eng, sf, fname


# State kept per-test by the autouse fixture
_current_engine = None
_current_session_factory = None
_current_db_file = None


@pytest_asyncio.fixture(autouse=True)
async def per_test_db(request):
    """Create a fresh database for every test (except E2E tests which manage their own)."""
    global _current_engine, _current_session_factory, _current_db_file

    # Skip for E2E tests that manage their own DB
    if "e2e" in str(request.fspath):
        # Still provide fallback override for other tests in the file
        yield
        return

    eng, sf, fname = _make_db()
    _current_engine = eng
    _current_session_factory = sf
    _current_db_file = fname

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Override FastAPI dependency
    async def _override_get_db():
        async with sf() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = _override_get_db

    yield

    await eng.dispose()
    try:
        import os
        os.remove(fname)
    except Exception:
        pass


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    assert _current_session_factory is not None
    async with _current_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Data fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        role="registered_user",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    profile = UserProfile(user_id=user.id, display_name="Test User", preferred_locale="ru-RU")
    db.add(profile)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def test_admin(db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    profile = UserProfile(user_id=user.id, display_name="Admin")
    db.add(profile)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    token = create_access_token(user_id=test_user.id, role=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin: User) -> dict:
    token = create_access_token(user_id=test_admin.id, role=test_admin.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_domain(db: AsyncSession) -> Domain:
    domain = Domain(slug="it", name="IT", description="IT domain", is_active=True, sort_order=0)
    db.add(domain)
    await db.commit()
    return domain


@pytest_asyncio.fixture
async def test_trainer(db: AsyncSession, test_domain: Domain) -> TrainerProduct:
    trainer = TrainerProduct(
        trainer_product_id="qa_engineer_interview_trainer",
        domain_id=test_domain.id,
        slug="qa-engineer-interview-trainer",
        name="QA Engineer Interview Trainer",
        product_type="interview_simulator",
        default_locale="ru-RU",
        supported_locales=["ru-RU", "en-US"],
        status="published_seed",
        is_published=True,
    )
    db.add(trainer)
    await db.commit()
    return trainer


@pytest_asyncio.fixture
async def test_scenario(db: AsyncSession, test_trainer: TrainerProduct) -> Scenario:
    scenario = Scenario(
        scenario_id="qa_bug_report_structure_v1",
        trainer_product_id=test_trainer.id,
        title_key="scenario.qa_bug_report.title",
        goal_key="scenario.qa_bug_report.goal",
        difficulty="junior_basic",
        estimated_duration_minutes=8,
        target_skills=["bug_reporting", "technical_accuracy"],
        user_role="candidate",
        ai_role="interviewer",
        rubric_id="qa_bug_report_rubric_v1",
        steps=[{"step_id": "step_1", "order": 1, "prompt_key": "scenario.qa_bug_report.step_1.prompt"}],
        critical_errors=["qa_crit_steps_not_needed"],
        hints=["hint.qa_bug_report.direction"],
        status="published_seed",
    )
    db.add(scenario)
    await db.commit()
    return scenario
