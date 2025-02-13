"""Import routes from different modules."""
from fastapi import FastAPI

from rest_server.api.config import router as config_router
from rest_server.api.receipts import router as receipts_router


def import_routes(app: FastAPI) -> None:
    """Import routes from different modules and add them to the app.

    Args:
        app: FastAPI application
    """
    app.include_router(receipts_router)
    app.include_router(config_router)
