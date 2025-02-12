"""Receipt API models."""
import re
from datetime import date
from datetime import time
from typing import Any
from typing import List

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class Item(BaseModel):
    """Item model with validation based on API spec."""

    shortDescription: str = Field(
        description="The Short Product Description for the item.",
        examples=["Mountain Dew 12PK"],
    )
    price: str = Field(
        description="The total price paid for this item.",
        examples=["6.49"],
    )

    @field_validator("shortDescription")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate short description format."""
        if not re.match(r"^[\w\s\-]+$", v):
            raise ValueError(
                "Description can only contain alphanumeric, spaces, "
                "and hyphens",
            )
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: str) -> str:
        """Validate price format and value."""
        if not re.match(r"^\d+\.\d{2}$", v):
            raise ValueError("Price must be in format '0.00'")
        return v


class Receipt(BaseModel):
    """Receipt model with validation based on API spec."""

    retailer: str = Field(
        description="The name of the retailer or store.",
        examples=["M&M Corner Market"],
    )
    purchaseDate: str = Field(
        description="The date of the purchase printed on the receipt.",
        examples=["2022-01-01"],
    )
    purchaseTime: str = Field(
        description="The time of the purchase (24-hour).",
        examples=["13:01"],
    )
    items: List[Item] = Field(
        description="The items purchased.",
        min_length=1,
    )
    total: str = Field(
        description="The total amount paid on the receipt.",
        examples=["6.49"],
    )

    @field_validator("retailer")
    @classmethod
    def validate_retailer(cls, v: str) -> str:
        """Validate retailer name format."""
        if not re.match(r"^[\w\s\-&]+$", v):
            raise ValueError(
                "Retailer can only contain alphanumeric, spaces, "
                "hyphens, and &",
            )
        return v

    @field_validator("purchaseDate")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate purchase date format."""
        # Check exact format YYYY-MM-DD
        if not re.match(
            r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$",
            v,
        ):
            raise ValueError("Purchase date must be in YYYY-MM-DD format")

        try:
            # Validate it's a real date
            date.fromisoformat(v)
            return v
        except ValueError as exc:
            raise ValueError(
                "Purchase date must be in YYYY-MM-DD format",
            ) from exc

    @field_validator("purchaseTime")
    @classmethod
    def validate_time(cls, v: str) -> str:
        """Validate purchase time format."""
        # Check exact format HH:MM in 24-hour
        if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", v):
            raise ValueError("Purchase time must be in HH:MM format (24-hour)")

        try:
            # Validate it's a real time
            time.fromisoformat(v)
            return v
        except ValueError as exc:
            raise ValueError(
                "Purchase time must be in HH:MM format (24-hour)",
            ) from exc

    @field_validator("total")
    @classmethod
    def validate_total(cls, v: str, info: Any) -> str:
        """Validate total format and check against item prices."""
        if not re.match(r"^\d+\.\d{2}$", v):
            raise ValueError("Total must be in format '0.00'")

        # Validate total matches sum of items if items are present
        data = info.data
        if "items" in data:
            items_total = sum(float(item.price) for item in data["items"])
            receipt_total = float(v)
            if abs(items_total - receipt_total) > 0.01:  # Allow rounding diffs
                raise ValueError(
                    "Total does not match sum of items "
                    f"({receipt_total} != {items_total})",
                )
        return v


class PointsResponse(BaseModel):
    """Points response model."""

    points: int = Field(
        description="The number of points awarded.",
        examples=[100],
    )


class ReceiptResponse(BaseModel):
    """Receipt response model."""

    id: str = Field(
        description="The ID assigned to the receipt.",
        pattern=r"^\S+$",
        examples=["adb6b560-0eef-42bc-9d16-df48f30e89b2"],
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate receipt ID format."""
        if not re.match(r"^\S+$", v):
            raise ValueError("ID cannot contain whitespace")
        return v
