"""Receipt API routes."""
from fastapi import APIRouter

from rest_server.api.receipts.points import router as points_router
from rest_server.api.receipts.process import router as process_router

# Create main router
router = APIRouter(prefix="/receipts", tags=["receipts"])

# Include all receipt-related routers
router.include_router(process_router)
router.include_router(points_router)
