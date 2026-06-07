"""API routes for Item management — with answer key protection for learners."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from app.certification_core.schemas.item_schemas import (
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse,
)
from app.certification_core.repositories.item_repository import ItemRepository, ItemFamilyRepository
from app.certification_core.validators.item_validator import ItemValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_permission,
    AuthorizationService,
)
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/certification-core/items", tags=["Certification-Core"])


from fastapi.responses import JSONResponse


def _filter_item_response(item, role: str) -> dict:
    """Filter out answer keys for learner-facing roles. Returns JSON-safe dict."""
    resp = ItemResponse.model_validate(item)
    data = resp.model_dump(mode="json")
    if not AuthorizationService.can_read_answer_keys(role):
        data.pop("answer_key", None)
    return data


@router.get("")
async def list_items(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    status: str = Query(None), domain_pack_id: str = Query(None),
    item_type: str = Query(None), item_family_id: str = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    role = AuthorizationService.get_role_from_token(credentials)
    repo = ItemRepository(db)
    items, total = await repo.list_items(
        skip=skip, limit=limit, status=status,
        domain_pack_id=domain_pack_id, item_type=item_type,
        item_family_id=item_family_id,
    )
    filtered = [_filter_item_response(it, role) for it in items]
    return {"items": filtered, "total": total, "skip": skip, "limit": limit}


@router.get("/{item_id}")
async def get_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    role = AuthorizationService.get_role_from_token(credentials)
    repo = ItemRepository(db)
    item = await repo.get_by_item_id(item_id)
    if not item:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Item not found")
    return _filter_item_response(item, role)


@router.post("", status_code=HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    errors = ItemValidator.validate_item(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = ItemRepository(db)
    audit = AuditService(db)

    item_data = body.model_dump()
    item = await repo.create(**item_data)

    await repo.create_snapshot(item.id, change_reason="Initial creation", created_by=body.created_by)
    await db.refresh(item)

    await audit.record_create(
        entity_type="item", entity_id=item.item_id,
        actor_id=body.created_by, actor_role=role,
    )
    resp_data = _filter_item_response(item, role)
    return JSONResponse(content=resp_data, status_code=HTTP_201_CREATED)


@router.patch("/{item_id}")
async def update_item(
    item_id: str, body: ItemUpdate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    repo = ItemRepository(db)
    audit = AuditService(db)

    item = await repo.get_by_item_id(item_id)
    if not item:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Item not found")

    # Immutability: active/published/exam-eligible items cannot be modified
    IMMUTABLE_STATUSES = {"active", "published", "exam_eligible", "approved_for_pilot", "pilot"}
    if item.status in IMMUTABLE_STATUSES:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            detail=f"Items with status '{item.status}' are immutable; create a new version instead",
        )

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="No fields to update")

    item = await repo.update_entity(item.id, **update_data)
    if item:
        await repo.create_snapshot(item.id, change_reason="Item updated", created_by=role)

    await audit.record_update(
        entity_type="item", entity_id=item_id,
        actor_id=role, actor_role=role,
    )
    return _filter_item_response(item, role)
