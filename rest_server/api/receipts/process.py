"""Process receipt endpoint."""
import json
import uuid
from typing import Dict

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from pydantic import ValidationError

from lib.core.receipt_processor import ReceiptProcessor
from rest_server.api.receipts.models import Receipt
from rest_server.api.receipts.models import ReceiptResponse
from rest_server.api.receipts.utils import get_processor

router = APIRouter()

processor_dependency = Depends(get_processor)


@router.post("/process", response_model=ReceiptResponse)
async def process_receipt(
    receipt: Receipt,
    request: Request,
    processor: ReceiptProcessor = processor_dependency,
) -> Dict[str, str]:
    """Process a receipt and return its ID.

    Args:
        receipt: Receipt to process
        request: FastAPI request object
        processor: Receipt processor instance

    Returns:
        Dictionary containing receipt ID

    Raises:
        HTTPException: If receipt validation fails or processing fails
    """
    try:
        # Calculate points
        points = await processor.calculate_points(receipt)

        # Generate receipt ID
        receipt_id = str(uuid.uuid4())

        # Store receipt and points
        context = request.state.context
        context.redis.set_key(
            f"receipt:{receipt_id}",
            json.dumps(
                {
                    "receipt": receipt.dict(),
                    "points": points,
                },
            ),
        )

        return {"id": receipt_id}

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail="The receipt is invalid.",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}",
        ) from e
