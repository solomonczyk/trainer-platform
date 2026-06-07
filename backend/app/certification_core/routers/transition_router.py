"""API routes for item lifecycle transitions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from app.certification_core.schemas.transition_schemas import (
    ItemTransitionRequest, ItemTransitionResponse,
)
from app.certification_core.repositories.item_repository import ItemRepository
from app.certification_core.state_machine.item_lifecycle import (
    validate_transition, LLM_ACTOR_PREFIX,
)
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    AuthorizationService,
)
from app.db.session import get_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/certification-core/items", tags=["Certification-Core"])


@router.post("/{item_id}/transitions", response_model=ItemTransitionResponse)
async def transition_item(
    item_id: str,
    body: ItemTransitionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Transition an item through its lifecycle."""
    role = AuthorizationService.get_role_from_token(credentials)
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    repo = ItemRepository(db)
    audit = AuditService(db)

    # Get the current item
    item = await repo.get_by_item_id(item_id)
    if not item:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Item not found")

    from_status = item.status
    to_status = body.to_status

    # Validate the transition
    result = validate_transition(
        from_status=from_status,
        to_status=to_status,
        actor_role=body.actor_role,
        actor_id=body.actor_id,
    )

    if not result["allowed"]:
        status_code = HTTP_403_FORBIDDEN if "role" in result.get("message", "").lower() or "llm" in result.get("message", "").lower() else HTTP_400_BAD_REQUEST
        raise HTTPException(status_code, detail=result["message"])

    # Execute transition
    updated = await repo.update_status(item.id, to_status)

    # Record in audit
    await audit.record_transition(
        entity_type="item",
        entity_id=item_id,
        from_status=from_status,
        to_status=to_status,
        actor_id=body.actor_id,
        actor_role=body.actor_role,
        reason=body.reason,
    )

    return ItemTransitionResponse(
        item_id=item_id,
        from_status=from_status,
        to_status=to_status,
        allowed=True,
        reason=body.reason,
        message=result["message"],
    )
