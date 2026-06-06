"""Tests for the BA trainer activities API endpoints.

Covers:
- Activity resolution and correct-answer hiding
- Submission with deterministic validation
- Authorization and user isolation
- Idempotency
- Retry handling
- Progress updates
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    User, Domain, TrainerProduct, Activity, Attempt, DeterministicEvaluation,
    UserTrainerEnrollment,
)
from app.core.security import create_access_token


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest_asyncio.fixture
async def ba_trainer(db: AsyncSession, test_domain: Domain) -> TrainerProduct:
    """Create a BA trainer product for testing."""
    trainer = TrainerProduct(
        trainer_product_id="business_analyst_interview_trainer",
        domain_id=test_domain.id,
        slug="business-analyst-interview-trainer",
        name="Business Analyst Interview Trainer",
        product_type="interview_simulator",
        default_locale="ru-RU",
        status="staging",
        is_published=True,
    )
    db.add(trainer)
    await db.commit()
    return trainer


@pytest_asyncio.fixture
async def ba_activity(db: AsyncSession, ba_trainer: TrainerProduct) -> Activity:
    """Create a single_choice activity for testing."""
    activity = Activity(
        activity_id="ba_test_q1_single",
        trainer_product_id=ba_trainer.id,
        module_id="ba_hr_screening",
        activity_type="single_choice",
        evaluation_mode="deterministic",
        difficulty="junior",
        title_key="ba_test_q1_title",
        payload={
            "options": ["Option A", "Option B", "Option C"],
            "correct": "Option B",
        },
        explanation_key="ba_test_q1_explanation",
        order=1,
        version="0.1.0",
    )
    db.add(activity)
    await db.commit()
    return activity


@pytest_asyncio.fixture
async def ba_enrollment(db: AsyncSession, test_user: User, ba_trainer: TrainerProduct):
    """Enroll test user in BA trainer."""
    enrollment = UserTrainerEnrollment(
        user_id=test_user.id,
        trainer_product_id=ba_trainer.id,
        is_active=True,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


# ==============================================================================
# Correct Answer Hiding Tests
# ==============================================================================

class TestCorrectAnswerHiding:
    @pytest.mark.asyncio
    async def test_activity_list_hides_correct_answers(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
        ba_enrollment, auth_headers,
    ):
        """GET /modules/{module_id}/activities must NOT include correct answers."""
        response = await client.get(
            f"/api/v1/trainers/{ba_trainer.slug}/modules/{ba_activity.module_id}/activities",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 1

        for activity in data["activities"]:
            assert "correct" not in activity["payload"], "Correct answer leaked in list!"

    @pytest.mark.asyncio
    async def test_activity_start_hides_correct_answers(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
        auth_headers,
    ):
        """GET /activities/{id}/start must NOT include correct answers."""
        response = await client.get(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/{ba_activity.activity_id}/start",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        prompt = data.get("prompt", {})
        assert "correct" not in prompt, "Correct answer leaked in start response!"
        assert "options" in prompt  # Public data should be present


# ==============================================================================
# Single Choice Activity Flow
# ==============================================================================

class TestSingleChoiceSubmission:
    @pytest.mark.asyncio
    async def test_correct_submission(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
        ba_enrollment, auth_headers,
    ):
        """Submitting the correct answer returns status=correct, score=100."""
        response = await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "correct"
        assert data["score"] == 100
        assert data["passed"] is True
        assert data["evaluation_mode"] == "deterministic"
        assert data["activity_id"] == ba_activity.activity_id

    @pytest.mark.asyncio
    async def test_incorrect_submission(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
        ba_enrollment, auth_headers,
    ):
        """Submitting the wrong answer returns status=incorrect, score=0."""
        response = await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option A",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "incorrect"
        assert data["score"] == 0
        assert data["passed"] is False

    @pytest.mark.asyncio
    async def test_unauthorized_submission_rejected(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
    ):
        """Submitting without auth must be rejected."""
        response = await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
            },
        )
        assert response.status_code == 401


# ==============================================================================
# User Isolation Tests
# ==============================================================================

class TestUserIsolation:
    @pytest.mark.asyncio
    async def test_other_user_cannot_access_submission(
        self, client: AsyncClient, db: AsyncSession, ba_trainer: TrainerProduct,
        ba_activity: Activity, ba_enrollment, auth_headers,
    ):
        """Another user submitting to same activity should work but be isolated."""
        # Create second user
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            role="registered_user",
        )
        db.add(other_user)
        await db.flush()

        # Enroll other user
        other_enrollment = UserTrainerEnrollment(
            user_id=other_user.id,
            trainer_product_id=ba_trainer.id,
            is_active=True,
        )
        db.add(other_enrollment)
        await db.commit()

        other_token = create_access_token(user_id=other_user.id)
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Both users submit
        for headers in [auth_headers, other_headers]:
            response = await client.post(
                f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
                headers=headers,
                json={
                    "activity_id": ba_activity.activity_id,
                    "answer": "Option B",
                },
            )
            assert response.status_code == 200

        # Verify both attempts exist
        from sqlalchemy import select
        result = await db.execute(
            select(Attempt).where(Attempt.activity_id == ba_activity.id)
        )
        attempts = result.scalars().all()
        assert len(attempts) == 2
        assert attempts[0].user_id != attempts[1].user_id  # Different users


# ==============================================================================
# Idempotency Tests
# ==============================================================================

class TestIdempotency:
    @pytest.mark.asyncio
    async def test_duplicate_idempotency_key_returns_same_result(
        self, client: AsyncClient, ba_trainer: TrainerProduct, ba_activity: Activity,
        ba_enrollment, auth_headers,
    ):
        """Using same idempotency_key returns same result without creating duplicate attempt."""
        idem_key = "test-idem-001"

        # First submission
        response1 = await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
                "idempotency_key": idem_key,
            },
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second submission with same key
        response2 = await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
                "idempotency_key": idem_key,
            },
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Same result
        assert data1["attempt_id"] == data2["attempt_id"]
        assert data1["status"] == data2["status"]
        assert data1["score"] == data2["score"]


# ==============================================================================
# Attempt Persistence Tests
# ==============================================================================

class TestAttemptPersistence:
    @pytest.mark.asyncio
    async def test_attempt_persisted_after_submission(
        self, client: AsyncClient, db: AsyncSession, ba_trainer: TrainerProduct,
        ba_activity: Activity, ba_enrollment, auth_headers,
    ):
        """After submission, attempt and evaluation records should exist."""
        await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
            },
        )

        from sqlalchemy import select
        result = await db.execute(
            select(Attempt).where(Attempt.activity_id == ba_activity.id)
        )
        attempt = result.scalar_one_or_none()
        assert attempt is not None
        assert attempt.status == "completed"
        assert attempt.activity_type == "single_choice"
        assert attempt.evaluation_mode == "deterministic"
        assert attempt.submitted_answer == "Option B"

        # Check deterministic evaluation exists
        eval_result = await db.execute(
            select(DeterministicEvaluation).where(
                DeterministicEvaluation.attempt_id == attempt.id
            )
        )
        evaluation = eval_result.scalar_one_or_none()
        assert evaluation is not None
        assert evaluation.status == "correct"
        assert evaluation.score == 100
        assert evaluation.passed is True

    @pytest.mark.asyncio
    async def test_retry_creates_separate_attempt(
        self, client: AsyncClient, db: AsyncSession, ba_trainer: TrainerProduct,
        ba_activity: Activity, ba_enrollment, auth_headers,
    ):
        """Retrying an activity creates a new attempt, doesn't overwrite previous."""
        # First attempt (wrong)
        await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option A",
            },
        )

        # Second attempt (correct)
        await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
            },
        )

        from sqlalchemy import select
        result = await db.execute(
            select(Attempt)
            .where(Attempt.activity_id == ba_activity.id)
            .order_by(Attempt.created_at)
        )
        attempts = result.scalars().all()
        assert len(attempts) == 2
        assert attempts[0].submitted_answer == "Option A"
        assert attempts[1].submitted_answer == "Option B"
        assert attempts[1].is_retry is True
        assert attempts[1].retry_of_attempt_id == attempts[0].id


# ==============================================================================
# Progress Update Tests
# ==============================================================================

class TestProgressUpdates:
    @pytest.mark.asyncio
    async def test_progress_updated_after_submission(
        self, client: AsyncClient, db: AsyncSession, ba_trainer: TrainerProduct,
        ba_activity: Activity, ba_enrollment, auth_headers, test_user: User,
    ):
        """Progress record should be created/updated after submission."""
        await client.post(
            f"/api/v1/trainers/{ba_trainer.slug}/activities/submit",
            headers=auth_headers,
            json={
                "activity_id": ba_activity.activity_id,
                "answer": "Option B",
            },
        )

        from app.db.models import TrainerProgress
        from sqlalchemy import select
        result = await db.execute(
            select(TrainerProgress).where(
                TrainerProgress.user_id == test_user.id,
                TrainerProgress.trainer_product_id == ba_trainer.id,
            )
        )
        progress = result.scalar_one_or_none()
        assert progress is not None
        assert progress.total_attempts == 1
        assert progress.completed_scenarios == 1  # passed
        assert progress.average_score == 100.0
