from typing import Dict
from user import User

class DeliveryStaff(User):
    """Information holder for delivery staff identity and availability."""

    AVAILABILITY_AVAILABLE = "Available"
    AVAILABILITY_BUSY = "Busy"
    AVAILABILITY_INACTIVE = "Inactive"

    def __init__(
        self,
        staff_id: str,
        full_name: str,
        phone: str,
        availability: str = AVAILABILITY_AVAILABLE,
        is_employed: bool = True,
    ) -> None:
        super().__init__(user_id=staff_id, full_name=full_name, phone=phone)
        self.availability = availability
        self.is_employed = is_employed

    @property
    def staff_id(self) -> str:
        """Return the user_id as staff_id for domain compatibility."""
        return self.user_id

    @staff_id.setter
    def staff_id(self, value: str) -> None:
        """Update the underlying user_id when staff_id is modified."""
        self.user_id = value

    def set_availability(self, new_status: str) -> None:
        """Update driver availability status if actively employed."""
        if not self.is_employed:
            self.availability = self.AVAILABILITY_INACTIVE
            return
        self.availability = new_status

    def deactivate_staff(self) -> None:
        """Mark a staff member as having left the business."""
        self.is_employed = False
        self.availability = self.AVAILABILITY_INACTIVE

    def to_dict(self) -> Dict[str, str]:
        """Serialise staff details for csv storage."""
        return {
            "staff_id": self.staff_id,
            "full_name": self.full_name,
            "phone": self.phone,
            "availability": self.availability,
            "is_employed": str(self.is_employed),
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "DeliveryStaff":
        """Instantiate a DeliveryStaff object from a CSV row."""
        return cls(
            staff_id=row["staff_id"],
            full_name=row["full_name"],
            phone=row["phone"],
            availability=row["availability"],
            is_employed=row["is_employed"].lower() == "true",
        )
