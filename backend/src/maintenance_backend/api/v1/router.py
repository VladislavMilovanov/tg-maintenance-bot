"""Versioned API router composition."""

from fastapi import APIRouter

from maintenance_backend.api.assistant import router as assistant_router
from maintenance_backend.api.equipment_state_records import (
    router as equipment_state_records_router,
)
from maintenance_backend.api.v1.admin import admin_router
from maintenance_backend.api.v1.auth import auth_router
from maintenance_backend.api.v1.dashboard import dashboard_router
from maintenance_backend.api.v1.equipment import equipment_router
from maintenance_backend.api.v1.locations import locations_router
from maintenance_backend.api.v1.sensor_groups import sensor_groups_router
from maintenance_backend.api.v1.text_to_sql import text_to_sql_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(equipment_state_records_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(equipment_router)
api_v1_router.include_router(sensor_groups_router)
api_v1_router.include_router(locations_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(text_to_sql_router)
