"""Get points endpoint."""
import json
from typing import Dict

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from rest_server.api.receipts.models import PointsResponse

router = APIRouter()


@router.get("/{receipt_id}/points", response_model=PointsResponse)
async def get_points(receipt_id: str, request: Request) -> Dict[str, int]:
    """Get points for a receipt.

    Args:
        receipt_id: ID of the receipt
        request: FastAPI request object

    Returns:
        Dictionary containing points

    Raises:
        HTTPException: If receipt data is invalid
    """
    context = request.state.context
    receipt_data = context.redis.get_key(f"receipt:{receipt_id}")

    if not receipt_data:
        raise HTTPException(
            status_code=404,
            detail="No receipt found for that ID.",
        )

    try:
        data = json.loads(receipt_data)
        return {"points": data.get("points", 0)}
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid receipt data format: {str(e)}",
        ) from e
