"""Configuration API routes."""
from fastapi import APIRouter

from rest_server.api.config.get_rules import router as get_rules_router
from rest_server.api.config.update_rules import router as update_rules_router

# Create main router
router = APIRouter(prefix="/config", tags=["config"])

# Include all config-related routers
router.include_router(get_rules_router)
router.include_router(update_rules_router)
