"""Utility functions for receipt APIs."""
import json
from typing import Dict

from fastapi import HTTPException
from fastapi import Request

from lib.core.receipt_processor import ReceiptProcessor


def get_processor(request: Request) -> ReceiptProcessor:
    """Get receipt processor from context.

    Args:
        request: FastAPI request object

    Returns:
        Configured receipt processor

    Raises:
        HTTPException: If rules configuration is invalid
    """
    context = request.state.context
    rules_json = context.redis.get_key("rules_config")

    try:
        rules: Dict = json.loads(rules_json) if rules_json else {"rules": []}
        return ReceiptProcessor(rules, logger=context.logger)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid rules configuration format: {str(e)}",
        ) from e
