from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from data_repository import DataRepository
from delivery_request import DeliveryRequest


class StatisticsService:
    """Computes delivery metrics across Day, Week, Month, Year, and YTD."""

    VALID_PERIODS = ("day", "week", "month", "year", "ytd")

    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def _get_cutoff_datetime(
        self, period: str, now: datetime
    ) -> datetime:
        """Determine the start timestamp for the requested reporting window."""
        period_key = period.lower()
        if period_key == "day":
            return now - timedelta(days=1)
        if period_key == "week":
            return now - timedelta(days=7)
        if period_key == "month":
            return now - timedelta(days=30)
        if period_key == "year":
            return now - timedelta(days=365)
        if period_key == "ytd":
            return datetime(now.year, 1, 1, 0, 0)
        return now - timedelta(days=30)

    def generate_report(
        self, period: str = "month", staff_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate delivery totals and revenue for the given filter."""
        now = datetime.now()
        cutoff = self._get_cutoff_datetime(period, now)
        all_deliveries = self.repository.get_all_deliveries()

        filtered = []
        for item in all_deliveries:
            if staff_id and item.assigned_staff_id != staff_id:
                continue

            timestamp_str = item.delivered_at or item.created_at
            try:
                record_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            if record_dt >= cutoff:
                filtered.append(item)

        completed = [
            d for d in filtered
            if d.status == DeliveryRequest.STATUS_DELIVERED
        ]
        in_progress = [
            d for d in filtered
            if d.status != DeliveryRequest.STATUS_DELIVERED
        ]
        total_revenue = sum(d.quote_cost for d in completed)

        return {
            "period": period.upper(),
            "staff_filter": staff_id or "All Delivery Staff",
            "total_logged_in_period": len(filtered),
            "completed_deliveries": len(completed),
            "active_pipeline_deliveries": len(in_progress),
            "completed_revenue": round(total_revenue, 2),
        }
