import csv
import os
from typing import List, Optional

from delivery_request import DeliveryRequest
from delivery_staff import DeliveryStaff


class DataRepository:
    """Manages shared persistent CSV storage for all system components."""

    DELIVERY_FIELDS = [
        "request_id",
        "customer_name",
        "customer_phone",
        "pickup_address",
        "dropoff_address",
        "parcel_weight_kg",
        "status",
        "quote_cost",
        "est_pickup_time",
        "est_delivery_time",
        "assigned_staff_id",
        "payment_reference",
        "created_at",
        "delivered_at",
    ]

    STAFF_FIELDS = [
        "staff_id",
        "full_name",
        "phone",
        "availability",
        "is_employed",
    ]

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.deliveries_file = os.path.join(data_dir, "deliveries.csv")
        self.staff_file = os.path.join(data_dir, "staff.csv")
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        """Create CSV files with headers if they do not yet exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.deliveries_file):
            with open(
                self.deliveries_file, mode="w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=self.DELIVERY_FIELDS)
                writer.writeheader()

        if not os.path.exists(self.staff_file):
            with open(
                self.staff_file, mode="w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=self.STAFF_FIELDS)
                writer.writeheader()

    def get_all_deliveries(self) -> List[DeliveryRequest]:
        """Read and return all delivery requests from CSV storage."""
        deliveries: List[DeliveryRequest] = []
        with open(
            self.deliveries_file, mode="r", newline="", encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                deliveries.append(DeliveryRequest.from_dict(row))
        return deliveries

    def save_all_deliveries(self, deliveries: List[DeliveryRequest]) -> None:
        """Overwrite the deliveries CSV with the updated object list."""
        with open(
            self.deliveries_file, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=self.DELIVERY_FIELDS)
            writer.writeheader()
            for item in deliveries:
                writer.writerow(item.to_dict())

    def get_delivery_by_id(
        self, request_id: str
    ) -> Optional[DeliveryRequest]:
        """Find a specific delivery request by its ID."""
        for delivery in self.get_all_deliveries():
            if delivery.request_id == request_id:
                return delivery
        return None

    def upsert_delivery(self, target: DeliveryRequest) -> None:
        """Insert a new delivery or update an existing one."""
        deliveries = self.get_all_deliveries()
        updated = False
        for idx, item in enumerate(deliveries):
            if item.request_id == target.request_id:
                deliveries[idx] = target
                updated = True
                break
        if not updated:
            deliveries.append(target)
        self.save_all_deliveries(deliveries)

    def get_all_staff(self) -> List[DeliveryStaff]:
        """Read and return all staff records from CSV storage."""
        staff_list: List[DeliveryStaff] = []
        with open(
            self.staff_file, mode="r", newline="", encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                staff_list.append(DeliveryStaff.from_dict(row))
        return staff_list

    def save_all_staff(self, staff_list: List[DeliveryStaff]) -> None:
        """Overwrite the staff CSV with the updated staff list."""
        with open(
            self.staff_file, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=self.STAFF_FIELDS)
            writer.writeheader()
            for member in staff_list:
                writer.writerow(member.to_dict())

    def get_staff_by_id(self, staff_id: str) -> Optional[DeliveryStaff]:
        """Retrieve a specific staff member by ID."""
        for member in self.get_all_staff():
            if member.staff_id == staff_id:
                return member
        return None

    def upsert_staff(self, target: DeliveryStaff) -> None:
        """Insert a new staff member or update an existing record."""
        staff_list = self.get_all_staff()
        updated = False
        for idx, member in enumerate(staff_list):
            if member.staff_id == target.staff_id:
                staff_list[idx] = target
                updated = True
                break
        if not updated:
            staff_list.append(target)
        self.save_all_staff(staff_list)
