"""Module for handling receipt validation and points calculation."""
import re
from datetime import time
from typing import Any
from typing import cast
from typing import Dict
from typing import List

import structlog
import yaml

from rest_server.api.receipts.models import Item
from rest_server.api.receipts.models import Receipt


class ReceiptProcessor:
    """Receipt processor for calculating points based on rules."""

    def __init__(
        self,
        rules_config: Dict[str, Any],
        logger: structlog.BoundLogger | None = None,
    ) -> None:
        """Initialize receipt processor with rules configuration.

        Args:
            rules_config: Dictionary containing rules configuration
            logger: Structured logger instance
        """
        self.rules = rules_config.get("rules", [])
        self.logger = logger or structlog.get_logger()

    @staticmethod
    async def load_rules_from_yaml(file_path: str) -> Dict[str, Any]:
        """Load rules configuration from YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            Dictionary containing rules configuration
        """
        with open(file_path, encoding="utf-8") as file:
            return yaml.safe_load(file)

    async def calculate_points(self, receipt: Receipt) -> int:
        """Calculate points for a receipt based on configured rules.

        Args:
            receipt: Receipt object to calculate points for

        Returns:
            Total points earned for the receipt
        """
        await self.logger.info(
            "Starting points calculation",
            retailer=receipt.retailer,
            date=receipt.purchaseDate,
            time=receipt.purchaseTime,
            total=receipt.total,
            items_count=len(receipt.items),
        )

        total_points = 0

        for rule in self.rules:
            rule_name = rule.get("name", "unnamed_rule")
            points = await self._apply_rule(rule, receipt)
            total_points += points

            await self.logger.info(
                "Rule points calculated",
                rule_name=rule_name,
                rule_type=rule.get("input_check", {}).get("type"),
                points=points,
                running_total=total_points,
            )

        await self.logger.info(
            "Points calculation completed",
            total_points=total_points,
        )
        return total_points

    async def _apply_rule(self, rule: Dict[str, Any], receipt: Receipt) -> int:
        """Apply a single rule to calculate points.

        Args:
            rule: Rule configuration dictionary
            receipt: Receipt to apply rule to

        Returns:
            Points earned from this rule
        """
        input_check = rule.get("input_check", {})
        points_calc = rule.get("points_calculation", {})
        rule_type = input_check.get("type")
        rule_name = rule.get("name", "unnamed_rule")

        # Skip if missing required configuration
        if not rule_type or not input_check.get("target_field"):
            await self.logger.warning(
                "Skipping rule due to missing configuration",
                rule_name=rule_name,
                rule_type=rule_type,
                target_field=input_check.get("target_field"),
            )
            return 0

        # Handle item-related rules differently
        if rule_type in ["item_description", "items_count"]:
            if not receipt.items:
                await self.logger.warning(
                    "No items found in receipt",
                    rule_name=rule_name,
                    rule_type=rule_type,
                )
                return 0

            if rule_type == "items_count":
                return await self._check_items_count(
                    receipt.items,
                    input_check,
                    points_calc,
                )
            else:
                return await self._check_description(
                    receipt.items,
                    input_check,
                    points_calc,
                )

        # Get target field value for non-item rules
        target_field = input_check["target_field"]
        field_value = getattr(receipt, target_field, None)

        if field_value is None:
            await self.logger.warning(
                "Target field not found in receipt",
                rule_name=rule_name,
                target_field=target_field,
            )
            return 0

        # Apply rule based on type
        try:
            value = cast(str, field_value)
            if rule_type == "character_count":
                return await self._check_character_count(
                    value,
                    input_check,
                    points_calc,
                )
            elif rule_type == "cents_check":
                return await self._check_cents(value, input_check, points_calc)
            elif rule_type == "total_check":
                return await self._check_total(value, input_check, points_calc)
            elif rule_type == "date_check":
                return await self._check_date(value, input_check, points_calc)
            elif rule_type == "time_check":
                return await self._check_time(value, input_check, points_calc)
        except Exception as e:
            await self.logger.error(
                "Error applying rule",
                rule_name=rule_name,
                rule_type=rule_type,
                error=str(e),
                exc_info=True,
            )
            return 0

        await self.logger.warning(
            "Unknown rule type",
            rule_name=rule_name,
            rule_type=rule_type,
        )
        return 0

    async def _check_character_count(
        self,
        value: str,
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check character count in a string value.

        Args:
            value: String to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        if input_check.get("condition") == "alphanumeric":
            # Only count letters and numbers
            char_count = len(re.findall(r"[a-zA-Z0-9]", value))
            points = char_count * points_calc.get("points_per_char", 0)
            return points
        return 0

    async def _check_cents(
        self,
        value: str,
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check cents value in a price string.

        Args:
            value: Price string to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        try:
            total = float(value)
            cents = round((total % 1) * 100)

            if input_check.get("condition") == "matches":
                input_value = input_check.get("input_value", 0)
                target_cents = round((input_value % 1) * 100)
                if cents == target_cents:
                    return points_calc.get("extra_points", 0)
        except (ValueError, TypeError) as e:
            await self.logger.warning(
                "Invalid price format",
                value=value,
                error=str(e),
            )
        return 0

    async def _check_total(
        self,
        value: str,
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check total amount conditions.

        Args:
            value: Total amount string to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        try:
            total = float(value)
            condition = input_check.get("condition")
            check_value = input_check.get("input_value", 0)

            if condition == "divisible" and total % check_value == 0:
                return points_calc.get("extra_points", 0)
            elif condition == "matches":
                total_cents = round((total % 1) * 100)
                check_cents = round((check_value % 1) * 100)
                if total_cents != check_cents:
                    return 0
                return points_calc.get("extra_points", 0)

        except (ValueError, TypeError) as e:
            await self.logger.warning(
                "Invalid total format",
                value=value,
                error=str(e),
            )
        return 0

    async def _check_items_count(
        self,
        items: List[Item],
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check items count conditions.

        Args:
            items: List of items to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        if input_check.get("condition") == "group_size":
            group_size = input_check.get("input_value", 2)
            groups = len(items) // group_size
            return groups * points_calc.get("points_per_group", 0)
        return 0

    async def _check_description(
        self,
        items: List[Item],
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check item description conditions.

        Args:
            items: List of items to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        total_points = 0
        qualifying_items = []

        if input_check.get("condition") == "divisible":
            divisor = input_check.get("input_value", 3)
            multiplier = points_calc.get("price_multiplier", 0)

            for item in items:
                desc_length = len(item.shortDescription.strip())
                if desc_length % divisor == 0:
                    try:
                        price = float(item.price)
                        # Multiply price by 0.2 and round up
                        points = int(price * multiplier + 0.99)
                        total_points += points

                        qualifying_items.append(
                            {
                                "description": item.shortDescription,
                                "length": desc_length,
                                "price": price,
                                "points": points,
                            },
                        )

                    except (ValueError, TypeError) as e:
                        await self.logger.warning(
                            "Invalid price format for item",
                            description=item.shortDescription,
                            price=item.price,
                            error=str(e),
                        )
                        continue

        return total_points

    async def _check_date(
        self,
        value: str,
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check date conditions.

        Args:
            value: Date string to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        try:
            day = int(value.split("-")[2])
            if input_check.get("condition") == "parity":
                parity = input_check.get("parity")
                if (parity == "odd" and day % 2 == 1) or (
                    parity == "even" and day % 2 == 0
                ):
                    return points_calc.get("extra_points", 0)
        except (IndexError, ValueError) as e:
            await self.logger.warning(
                "Invalid date format",
                value=value,
                error=str(e),
            )
        return 0

    async def _check_time(
        self,
        value: str,
        input_check: Dict[str, Any],
        points_calc: Dict[str, Any],
    ) -> int:
        """Check time conditions.

        Args:
            value: Time string to check
            input_check: Input validation configuration
            points_calc: Points calculation configuration

        Returns:
            Points earned
        """
        try:
            if input_check.get("condition") == "between":
                time_range = input_check.get("input_range", {})
                purchase_time = time.fromisoformat(value)
                start_time = time.fromisoformat(
                    time_range.get("start", "00:00"),
                )
                end_time = time.fromisoformat(time_range.get("end", "23:59"))

                if start_time <= purchase_time <= end_time:
                    return points_calc.get("extra_points", 0)
        except (ValueError, TypeError) as e:
            await self.logger.warning(
                "Invalid time format",
                value=value,
                error=str(e),
            )
        return 0
