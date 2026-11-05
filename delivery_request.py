from datetime import datetime
from typing import Dict, Optional


class DeliveryRequest:
    """Information holder for a single parcel delivery order."""

    STATUS_REQUESTED = "Requested"
    STATUS_QUOTED = "Quoted"
    STATUS_ACCEPTED = "Accepted & Paid"
    STATUS_ASSIGNED = "Assigned"
    STATUS_DELIVERED = "Delivered"

    def __init__(
        self,
        request_id: str,
        customer_name: str,
        customer_phone: str,
        pickup_address: str,
        dropoff_address: str,
        parcel_weight_kg: float,
        status: str = STATUS_REQUESTED,
        quote_cost: float = 0.0,
        est_pickup_time: str = "",
        est_delivery_time: str = "",
        assigned_staff_id: str = "",
        payment_reference: str = "",
        created_at: Optional[str] = None,
        delivered_at: str = "",
    ) -> None:
        self.request_id = request_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.pickup_address = pickup_address
        self.dropoff_address = dropoff_address
        self.parcel_weight_kg = float(parcel_weight_kg)
        self.status = status
        self.quote_cost = float(quote_cost)
        self.est_pickup_time = est_pickup_time
        self.est_delivery_time = est_delivery_time
        self.assigned_staff_id = assigned_staff_id
        self.payment_reference = payment_reference
        self.created_at = created_at or datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        self.delivered_at = delivered_at

    def apply_quote(
        self, cost: float, pickup_time: str, delivery_time: str
    ) -> None:
        """Assign quote details and update status to quoted."""
        self.quote_cost = round(float(cost), 2)
        self.est_pickup_time = pickup_time
        self.est_delivery_time = delivery_time
        self.status = self.STATUS_QUOTED

    def mark_accepted_and_paid(self, payment_ref: str) -> None:
        """Record online payment reference and mark order as accepted."""
        self.payment_reference = payment_ref
        self.status = self.STATUS_ACCEPTED

    def assign_driver(self, staff_id: str) -> None:
        """Allocate a delivery staff member to this order."""
        self.assigned_staff_id = staff_id
        self.status = self.STATUS_ASSIGNED

    def mark_delivered(self) -> None:
        """Complete the delivery and timestamp completion."""
        self.status = self.STATUS_DELIVERED
        self.delivered_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self) -> Dict[str, str]:
        """Serialise the delivery request for csv persistence."""
        return {
            "request_id": self.request_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "pickup_address": self.pickup_address,
            "dropoff_address": self.dropoff_address,
            "parcel_weight_kg": f"{self.parcel_weight_kg:.2f}",
            "status": self.status,
            "quote_cost": f"{self.quote_cost:.2f}",
            "est_pickup_time": self.est_pickup_time,
            "est_delivery_time": self.est_delivery_time,
            "assigned_staff_id": self.assigned_staff_id,
            "payment_reference": self.payment_reference,
            "created_at": self.created_at,
            "delivered_at": self.delivered_at,
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "DeliveryRequest":
        """Instantiate a DeliveryRequest from a csv dictionary row."""
        return cls(
            request_id=row["request_id"],
            customer_name=row["customer_name"],
            customer_phone=row["customer_phone"],
            pickup_address=row["pickup_address"],
            dropoff_address=row["dropoff_address"],
            parcel_weight_kg=float(row["parcel_weight_kg"] or 0.0),
            status=row["status"],
            quote_cost=float(row["quote_cost"] or 0.0),
            est_pickup_time=row["est_pickup_time"],
            est_delivery_time=row["est_delivery_time"],
            assigned_staff_id=row["assigned_staff_id"],
            payment_reference=row["payment_reference"],
            created_at=row["created_at"],
            delivered_at=row["delivered_at"],
        )
