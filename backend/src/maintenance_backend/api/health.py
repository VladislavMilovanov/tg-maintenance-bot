"""Health check endpoints."""

from fastapi import APIRouter, Depends

from maintenance_backend.database import DatabaseGateway
from maintenance_backend.dependencies import get_database
from maintenance_backend.exceptions import ReadinessError

router = APIRouter(tags=["service"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    """Return minimal service health status for local smoke checks."""

    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(
    database: DatabaseGateway = Depends(get_database),
) -> dict[str, str]:
    """Return readiness status that depends on PostgreSQL availability."""

    try:
        await database.ping()
    except Exception as exc:  # pragma: no cover - backend readiness integration
        raise ReadinessError() from exc
    return {"status": "ok"}
