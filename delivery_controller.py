from typing import Tuple

from data_repository import DataRepository
from delivery_request import DeliveryRequest
from delivery_staff import DeliveryStaff
from payment_gateway import PaymentGateway
from validator import InputValidator


class DeliverySystemController:
    """Coordinates validation, domain logic, and repository persistence."""

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository


    def create_delivery_request(
        self,
        customer_name: str,
        customer_phone: str,
        pickup_address: str,
        dropoff_address: str,
        weight_str: str,
    ) -> Tuple[bool, str]:
        """Validate inputs and log a new delivery request."""
        checks = [
            InputValidator.validate_name(customer_name, "Customer name"),
            InputValidator.validate_phone(customer_phone),
            InputValidator.validate_melbourne_address(
                pickup_address, "Pickup address"
            ),
            InputValidator.validate_melbourne_address(
                dropoff_address, "Drop-off address"
            ),
            InputValidator.validate_positive_float(
                weight_str, "Parcel weight (kg)", max_val=500.0
            ),
        ]
        for is_valid, error_msg in checks:
            if not is_valid:
                return False, error_msg

        existing = self.repository.get_all_deliveries()
        next_id = f"ORD-{len(existing) + 1001}"
        new_request = DeliveryRequest(
            request_id=next_id,
            customer_name=customer_name.strip(),
            customer_phone=customer_phone.strip(),
            pickup_address=pickup_address.strip(),
            dropoff_address=dropoff_address.strip(),
            parcel_weight_kg=float(weight_str),
        )
        self.repository.upsert_delivery(new_request)
        return True, f"Delivery request {next_id} logged."

    def provide_quote(
        self,
        request_id: str,
        cost_str: str,
        est_pickup_time: str,
        est_delivery_time: str,
    ) -> Tuple[bool, str]:
        """Validate and attach an office quote to a pending request."""
        order = self.repository.get_delivery_by_id(request_id)
        if not order:
            return False, f"Order {request_id} not found."

        valid_cost, cost_err = InputValidator.validate_positive_float(
            cost_str, "Quote cost ($)", max_val=50000.0
        )
        if not valid_cost:
            return False, cost_err

        valid_time, time_err = InputValidator.validate_schedule_times(
            est_pickup_time, est_delivery_time
        )
        if not valid_time:
            return False, time_err

        order.apply_quote(
            float(cost_str),
            est_pickup_time.strip(),
            est_delivery_time.strip(),
        )
        self.repository.upsert_delivery(order)
        return True, f"Quote of ${order.quote_cost:.2f} issued for {request_id}."

    def accept_quote_and_pay(self, request_id: str) -> Tuple[bool, str]:
        """Process online payment and transition order to Accepted & Paid."""
        order = self.repository.get_delivery_by_id(request_id)
        if not order:
            return False, f"Order {request_id} not found."
        if order.status != DeliveryRequest.STATUS_QUOTED:
            return (
                False,
                f"Order {request_id} must be in 'Quoted' state to accept.",
            )

        paid, payment_ref = PaymentGateway.process_online_payment(
            order.request_id, order.quote_cost
        )
        if not paid:
            return False, payment_ref

        order.mark_accepted_and_paid(payment_ref)
        self.repository.upsert_delivery(order)
        return (
            True,
            f"Quote accepted for {request_id}. Online payment confirmed "
            f"({payment_ref}).",
        )



    def register_staff(
        self, full_name: str, phone: str
    ) -> Tuple[bool, str]:
        """Validate and onboard a new delivery staff member."""
        valid_name, name_err = InputValidator.validate_name(
            full_name, "Staff full name"
        )
        if not valid_name:
            return False, name_err

        valid_phone, phone_err = InputValidator.validate_phone(phone)
        if not valid_phone:
            return False, phone_err

        staff_list = self.repository.get_all_staff()
        next_id = f"STF-{len(staff_list) + 101}"
        new_member = DeliveryStaff(
            staff_id=next_id,
            full_name=full_name.strip(),
            phone=phone.strip(),
        )
        self.repository.upsert_staff(new_member)
        return True, f"Delivery staff {new_member.full_name} ({next_id}) added."

    def update_staff_availability(
        self, staff_id: str, availability: str
    ) -> Tuple[bool, str]:
        """Change a staff member's availability or mark them as departed."""
        member = self.repository.get_staff_by_id(staff_id)
        if not member:
            return False, f"Staff {staff_id} not found."

        if availability == "Departed":
            member.deactivate_staff()
            self.repository.upsert_staff(member)
            return True, f"Staff {staff_id} marked as departed (Inactive)."

        allowed = {
            DeliveryStaff.AVAILABILITY_AVAILABLE,
            DeliveryStaff.AVAILABILITY_BUSY,
        }
        if availability not in allowed:
            return False, "Invalid availability status selected."

        if not member.is_employed:
            return False, "Cannot activate a departed staff member."

        member.set_availability(availability)
        self.repository.upsert_staff(member)
        return True, f"Staff {staff_id} status updated to {availability}."



    def allocate_staff_to_order(
        self, request_id: str, staff_id: str
    ) -> Tuple[bool, str]:
        """Assign an available driver to an Accepted & Paid order."""
        order = self.repository.get_delivery_by_id(request_id)
        if not order:
            return False, f"Order {request_id} not found."
        if order.status != DeliveryRequest.STATUS_ACCEPTED:
            return (
                False,
                "Only 'Accepted & Paid' orders can be allocated to a driver.",
            )

        driver = self.repository.get_staff_by_id(staff_id)
        if not driver or not driver.is_employed:
            return False, "Selected delivery staff is invalid or inactive."
        if driver.availability != DeliveryStaff.AVAILABILITY_AVAILABLE:
            return (
                False,
                f"Driver {driver.full_name} is currently {driver.availability}.",
            )

        order.assign_driver(driver.staff_id)
        driver.set_availability(DeliveryStaff.AVAILABILITY_BUSY)
        self.repository.upsert_delivery(order)
        self.repository.upsert_staff(driver)
        return (
            True,
            f"Order {request_id} assigned to {driver.full_name} ({staff_id}).",
        )

    def complete_delivery(self, request_id: str) -> Tuple[bool, str]:
        """Mark an assigned delivery as Delivered and free up the driver."""
        order = self.repository.get_delivery_by_id(request_id)
        if not order:
            return False, f"Order {request_id} not found."
        if order.status != DeliveryRequest.STATUS_ASSIGNED:
            return (
                False,
                "Only 'Assigned' orders can be marked as Delivered.",
            )

        order.mark_delivered()
        self.repository.upsert_delivery(order)

        if order.assigned_staff_id:
            driver = self.repository.get_staff_by_id(order.assigned_staff_id)
            if driver and driver.is_employed:
                driver.set_availability(DeliveryStaff.AVAILABILITY_AVAILABLE)
                self.repository.upsert_staff(driver)

        return True, f"Order {request_id} marked as Delivered."
