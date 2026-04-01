"""Backend runtime entry point."""

import uvicorn

from maintenance_backend.app import create_app
from maintenance_backend.config import Settings


def main() -> None:
    """Run backend development server."""

    settings = Settings()
    app = create_app(settings)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
