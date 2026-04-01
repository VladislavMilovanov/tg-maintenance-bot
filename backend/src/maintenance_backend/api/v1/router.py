"""Versioned API router composition."""

from fastapi import APIRouter

from maintenance_backend.api.assistant import router as assistant_router
from maintenance_backend.api.equipment_state_records import (
    router as equipment_state_records_router,
)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(equipment_state_records_router)
