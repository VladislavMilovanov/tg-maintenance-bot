"""Domain and infrastructure exceptions mapped to API responses."""

from maintenance_backend.schemas.errors import ErrorDetail


class BackendError(Exception):
    """Base exception with optional API payload details."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "Internal server error."

    def __init__(
        self,
        *,
        details: list[ErrorDetail] | None = None,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(self.message)
        self.details = details
        self.trace_id = trace_id


class EquipmentNotFound(BackendError):
    """Raised when equipment reference does not exist."""

    status_code = 404
    code = "equipment_not_found"
    message = "Equipment was not found."


class IdempotencyConflict(BackendError):
    """Raised when idempotency key is reused with different payload."""

    status_code = 409
    code = "idempotency_conflict"
    message = "Idempotency key conflicts with an existing record."


class AssistantContextValidationError(BackendError):
    """Raised when assistant request business-context is invalid."""

    status_code = 422
    code = "validation_error"
    message = "Request validation failed."


class AssistantUnavailable(BackendError):
    """Raised when assistant flow cannot produce any response."""

    status_code = 503
    code = "assistant_unavailable"
    message = "Assistant is temporarily unavailable."


class ReadinessError(BackendError):
    """Raised when readiness check fails."""

    status_code = 503
    code = "service_unavailable"
    message = "Service is not ready."
