from datetime import datetime
import re
from typing import Tuple


class InputValidator:
    """Validates user inputs before domain operations occur."""

    NAME_PATTERN = re.compile(r"^[A-Za-z\s\-']{2,60}$")
    PHONE_PATTERN = re.compile(r"^0[23478]\d{8}$")
    VIC_POSTCODE_PATTERN = re.compile(r"\b3\d{3}\b")
    DATETIME_FORMAT = "%Y-%m-%d %H:%M"

    @classmethod
    def validate_name(cls, name: str, label: str = "Name") -> Tuple[bool, str]:
        """Validate person names (2-60 alphabetic characters)."""
        cleaned = (name or "").strip()
        if not cls.NAME_PATTERN.match(cleaned):
            return (
                False,
                f"{label} must be 2-60 letters, spaces, hyphens, or "
                "apostrophes.",
            )
        return True, ""

    @classmethod
    def validate_phone(cls, phone: str) -> Tuple[bool, str]:
        """Validate standard 10-digit Australian phone numbers."""
        cleaned = re.sub(r"\s+", "", phone or "")
        if not cls.PHONE_PATTERN.match(cleaned):
            return (
                False,
                "Phone number must be a valid 10-digit Australian number "
                "(e.g., 0412345678).",
            )
        return True, ""

    @classmethod
    def validate_melbourne_address(
        cls, address: str, label: str = "Address"
    ) -> Tuple[bool, str]:
        """Ensure address is non-empty and includes a Victoria 3xxx postcode."""
        cleaned = (address or "").strip()
        if len(cleaned) < 8:
            return False, f"{label} is too short."
        if not cls.VIC_POSTCODE_PATTERN.search(cleaned):
            return (
                False,
                f"{label} must include a valid Melbourne/Victoria "
                "postcode (3000-3999).",
            )
        return True, ""

    @classmethod
    def validate_positive_float(
        cls, value_str: str, label: str, max_val: float = 10000.0
    ) -> Tuple[bool, str]:
        """Validate numeric strings as positive floats within bounds."""
        try:
            val = float(value_str)
        except (ValueError, TypeError):
            return False, f"{label} must be a valid number."
        if val <= 0 or val > max_val:
            return (
                False,
                f"{label} must be greater than 0 and at most {max_val}.",
            )
        return True, ""

    @classmethod
    def validate_schedule_times(
        cls, pickup_str: str, delivery_str: str
    ) -> Tuple[bool, str]:
        """Validate pickup and delivery timestamps (YYYY-MM-DD HH:MM)."""
        try:
            pickup_dt = datetime.strptime(
                (pickup_str or "").strip(), cls.DATETIME_FORMAT
            )
            delivery_dt = datetime.strptime(
                (delivery_str or "").strip(), cls.DATETIME_FORMAT
            )
        except ValueError:
            return (
                False,
                "Timestamps must follow YYYY-MM-DD HH:MM "
                "(e.g., 2026-03-07 14:30).",
            )

        if delivery_dt <= pickup_dt:
            return (
                False,
                "Estimated delivery time must be later than pickup time.",
            )
        return True, ""
