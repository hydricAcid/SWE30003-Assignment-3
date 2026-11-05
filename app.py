from flask import Flask, flash, redirect, render_template, request, url_for

from data_repository import DataRepository
from delivery_controller import DeliverySystemController
from statistics_service import StatisticsService


class DeliveryWebPortal:
    """Web interface layer connecting HTML forms to system services."""

    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.app.secret_key = "SWE30003-105343454"
        self.repository = DataRepository()
        self.controller = DeliverySystemController(self.repository)
        self.stats_service = StatisticsService(self.repository)
        self._register_routes()

    def _register_routes(self) -> None:
        """Bind URL endpoints to handler methods."""
        self.app.add_url_rule("/", "dashboard", self.dashboard, methods=["GET"])
        self.app.add_url_rule(
            "/request/new",
            "create_request",
            self.create_request,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/request/quote",
            "quote_request",
            self.quote_request,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/request/accept",
            "accept_quote",
            self.accept_quote,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/staff/new",
            "add_staff",
            self.add_staff,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/staff/status",
            "update_staff",
            self.update_staff,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/delivery/allocate",
            "allocate_delivery",
            self.allocate_delivery,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/delivery/complete",
            "complete_delivery",
            self.complete_delivery,
            methods=["POST"],
        )

    def dashboard(self) -> str:
        """Render the unified operational dashboard."""
        period = request.args.get("period", "month")
        staff_filter = request.args.get("staff_id", "").strip() or None
        stats = self.stats_service.generate_report(
            period=period, staff_id=staff_filter
        )
        deliveries = self.repository.get_all_deliveries()
        staff_list = self.repository.get_all_staff()
        return render_template(
            "index.html",
            deliveries=deliveries,
            staff_list=staff_list,
            stats=stats,
            selected_period=period,
            selected_staff=staff_filter or "",
        )

    def create_request(self):
        """Handle form submission for logging a new delivery request."""
        success, message = self.controller.create_delivery_request(
            customer_name=request.form.get("customer_name", ""),
            customer_phone=request.form.get("customer_phone", ""),
            pickup_address=request.form.get("pickup_address", ""),
            dropoff_address=request.form.get("dropoff_address", ""),
            weight_str=request.form.get("parcel_weight_kg", ""),
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def quote_request(self):
        """Handle form submission for issuing a delivery quote."""
        success, message = self.controller.provide_quote(
            request_id=request.form.get("request_id", ""),
            cost_str=request.form.get("quote_cost", ""),
            est_pickup_time=request.form.get("est_pickup_time", ""),
            est_delivery_time=request.form.get("est_delivery_time", ""),
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def accept_quote(self):
        """Handle customer quote acceptance and online payment."""
        success, message = self.controller.accept_quote_and_pay(
            request_id=request.form.get("request_id", "")
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def add_staff(self):
        """Handle onboarding a new delivery driver."""
        success, message = self.controller.register_staff(
            full_name=request.form.get("full_name", ""),
            phone=request.form.get("phone", ""),
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def update_staff(self):
        """Handle staff availability and offboarding updates."""
        success, message = self.controller.update_staff_availability(
            staff_id=request.form.get("staff_id", ""),
            availability=request.form.get("availability", ""),
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def allocate_delivery(self):
        """Handle assigning an available driver to a paid order."""
        success, message = self.controller.allocate_staff_to_order(
            request_id=request.form.get("request_id", ""),
            staff_id=request.form.get("staff_id", ""),
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def complete_delivery(self):
        """Handle marking an order as Delivered."""
        success, message = self.controller.complete_delivery(
            request_id=request.form.get("request_id", "")
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("dashboard"))

    def run(self) -> None:
        """Start the web server."""
        self.app.run(debug=True, port=5000)


if __name__ == "__main__":
    portal = DeliveryWebPortal()
    portal.run()
