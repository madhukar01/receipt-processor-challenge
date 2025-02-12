"""Configuration API models."""
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class RoundingMethod(str, Enum):
    """Rounding method for calculations."""

    UP = "up"
    DOWN = "down"


class Parity(str, Enum):
    """Parity options for date checks."""

    ODD = "odd"
    EVEN = "even"


class RuleCondition(str, Enum):
    """Available rule conditions."""

    ALPHANUMERIC = "alphanumeric"
    DIVISIBLE = "divisible"
    MATCHES = "matches"
    BETWEEN = "between"
    PARITY = "parity"
    GROUP_SIZE = "group_size"


class RuleType(str, Enum):
    """Available rule types."""

    CHARACTER_COUNT = "character_count"
    CENTS_CHECK = "cents_check"
    TOTAL_CHECK = "total_check"
    ITEMS_COUNT = "items_count"
    ITEM_DESCRIPTION = "item_description"
    DATE_CHECK = "date_check"
    TIME_CHECK = "time_check"


class RoundingConfig(BaseModel):
    """Rounding configuration for points calculation."""

    method: RoundingMethod
    precision: float = Field(ge=0)  # Precision in decimal places


class TimeRange(BaseModel):
    """Time range configuration."""

    start: str  # HH:MM format
    end: str  # HH:MM format


class InputCheck(BaseModel):
    """Input validation configuration."""

    type: RuleType
    target_field: str
    condition: RuleCondition
    input_value: Optional[float] = None
    input_range: Optional[TimeRange] = None
    parity: Optional[Parity] = None


class PointsCalculation(BaseModel):
    """Points calculation configuration."""

    points_per_char: Optional[int] = None
    extra_points: Optional[int] = None
    points_per_group: Optional[int] = None
    price_multiplier: Optional[float] = None
    rounding: Optional[RoundingConfig] = None


class Rule(BaseModel):
    """Rule configuration."""

    name: str
    input_check: InputCheck
    points_calculation: PointsCalculation


class RulesConfig(BaseModel):
    """Rules configuration model."""

    rules: List[Rule]

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True
