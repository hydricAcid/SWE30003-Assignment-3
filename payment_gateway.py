from typing import Tuple
import uuid


class PaymentGateway:
    """Payment simulator."""

    @staticmethod
    def process_online_payment(
        request_id: str, amount: float
    ) -> Tuple[bool, str]:
        """It is assumed that payments will always succeed."""
        if amount <= 0:
            return False, "Invalid payment amount."
        reference = f"PAY-{request_id}-{uuid.uuid4().hex[:6].upper()}"
        return True, reference
