"""API routers for certification-grade core."""

from app.certification_core.routers.competency_router import router as competency_router
from app.certification_core.routers.blueprint_router import router as blueprint_router
from app.certification_core.routers.knowledge_source_router import router as knowledge_source_router
from app.certification_core.routers.item_family_router import router as item_family_router
from app.certification_core.routers.item_router import router as item_router
from app.certification_core.routers.rubric_router import router as rubric_router
from app.certification_core.routers.domain_pack_router import router as domain_pack_router
from app.certification_core.routers.audit_router import router as audit_router
from app.certification_core.routers.transition_router import router as transition_router

__all__ = [
    "competency_router",
    "blueprint_router",
    "knowledge_source_router",
    "item_family_router",
    "item_router",
    "rubric_router",
    "domain_pack_router",
    "audit_router",
    "transition_router",
]
