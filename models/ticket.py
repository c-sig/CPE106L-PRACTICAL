"""
Ticket model and TicketStatus enumeration for transit reservations.
Includes tamper-resistant booking reference generation (NFR-1) and full lifecycle tracking (FR-2).
"""
import hashlib
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class TicketStatus(Enum):
    """Lifecycle statuses for a transit ticket."""
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class Ticket:
    """
    Represents an issued bus transit ticket.

    Attributes:
        _ticket_id (str): Primary ticket ID (e.g., 'TKT-1001').
        _booking_reference (str): Tamper-resistant 8-10 character alphanumeric verification code (NFR-1).
        _route_id (str): Foreign key to Route.
        _bus_id (str): Foreign key to Bus.
        _passenger_id (str): Foreign key to Passenger.
        _seat_number (int): Assigned seat index.
        _travel_date (str): Date of travel in ISO format (YYYY-MM-DD).
        _base_fare (float): Undiscounted ticket fare.
        _discount_amount (float): Deduction applied (e.g., 20% concession).
        _final_fare (float): Amount charged/paid.
        _status (TicketStatus): Current lifecycle state.
        _booking_time (str): Timestamp of reservation creation.
        _cancellation_time (Optional[str]): Timestamp when cancelled if applicable.
        _cancellation_reason (Optional[str]): Reason documented for cancellation.
    """

    def __init__(
        self,
        ticket_id: str,
        booking_reference: str,
        route_id: str,
        bus_id: str,
        passenger_id: str,
        seat_number: int,
        travel_date: str,
        base_fare: float,
        discount_amount: float,
        final_fare: float,
        status: TicketStatus = TicketStatus.CONFIRMED,
        booking_time: Optional[str] = None,
        cancellation_time: Optional[str] = None,
        cancellation_reason: Optional[str] = None,
    ) -> None:
        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError("Ticket ID must be a non-empty string")
        self._ticket_id = ticket_id.strip()

        if not isinstance(booking_reference, str) or not booking_reference.strip():
            raise ValueError("Booking reference code must be a non-empty string")
        self._booking_reference = booking_reference.strip().upper()

        self.route_id = route_id
        self.bus_id = bus_id
        self.passenger_id = passenger_id
        self.seat_number = seat_number
        self.travel_date = travel_date
        self.base_fare = base_fare
        self.discount_amount = discount_amount
        self.final_fare = final_fare
        self.status = status

        self._booking_time = booking_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._cancellation_time = cancellation_time
        self._cancellation_reason = cancellation_reason

    @property
    def ticket_id(self) -> str:
        """Return unique ticket ID (read-only)."""
        return self._ticket_id

    @property
    def booking_reference(self) -> str:
        """Return tamper-resistant booking reference code (read-only)."""
        return self._booking_reference

    @property
    def route_id(self) -> str:
        return self._route_id

    @route_id.setter
    def route_id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Route ID cannot be empty")
        self._route_id = value.strip()

    @property
    def bus_id(self) -> str:
        return self._bus_id

    @bus_id.setter
    def bus_id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Bus ID cannot be empty")
        self._bus_id = value.strip()

    @property
    def passenger_id(self) -> str:
        return self._passenger_id

    @passenger_id.setter
    def passenger_id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Passenger ID cannot be empty")
        self._passenger_id = value.strip()

    @property
    def seat_number(self) -> int:
        return self._seat_number

    @seat_number.setter
    def seat_number(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Seat number must be a positive integer")
        self._seat_number = value

    @property
    def travel_date(self) -> str:
        return self._travel_date

    @travel_date.setter
    def travel_date(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Travel date must be a string")
        cleaned = value.strip()
        try:
            datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid travel date '{value}'. Expected ISO format (YYYY-MM-DD)")
        self._travel_date = cleaned

    @property
    def base_fare(self) -> float:
        return self._base_fare

    @base_fare.setter
    def base_fare(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Base fare must be a non-negative number")
        self._base_fare = round(float(value), 2)

    @property
    def discount_amount(self) -> float:
        return self._discount_amount

    @discount_amount.setter
    def discount_amount(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Discount amount must be a non-negative number")
        self._discount_amount = round(float(value), 2)

    @property
    def final_fare(self) -> float:
        return self._final_fare

    @final_fare.setter
    def final_fare(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Final fare must be a non-negative number")
        self._final_fare = round(float(value), 2)

    @property
    def status(self) -> TicketStatus:
        return self._status

    @status.setter
    def status(self, value: TicketStatus) -> None:
        if not isinstance(value, TicketStatus):
            raise TypeError(f"Status must be a TicketStatus enum member, got {type(value)}")
        self._status = value

    @property
    def booking_time(self) -> str:
        return self._booking_time

    @property
    def cancellation_time(self) -> Optional[str]:
        return self._cancellation_time

    @property
    def cancellation_reason(self) -> Optional[str]:
        return self._cancellation_reason

    def cancel(self, reason: str = "Passenger request") -> None:
        """Cancel this ticket and timestamp the action."""
        if self._status == TicketStatus.CANCELLED:
            raise ValueError("Ticket is already cancelled")
        self._status = TicketStatus.CANCELLED
        self._cancellation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._cancellation_reason = reason.strip() or "Passenger cancellation"

    @classmethod
    def generate_reference_code(cls, route_id: str, seat_num: int) -> str:
        """
        Generate a cryptographically secure, tamper-resistant 8-character verification code (NFR-1).
        Format: 'BTK-' + 6 hex chars derived from timestamp, salt, and route.
        """
        salt = uuid.uuid4().hex
        raw = f"{route_id}-{seat_num}-{datetime.now().isoformat()}-{salt}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:6].upper()
        return f"BTK-{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ticket attributes to dictionary."""
        return {
            "ticket_id": self._ticket_id,
            "booking_reference": self._booking_reference,
            "route_id": self._route_id,
            "bus_id": self._bus_id,
            "passenger_id": self._passenger_id,
            "seat_number": self._seat_number,
            "travel_date": self._travel_date,
            "base_fare": self._base_fare,
            "discount_amount": self._discount_amount,
            "final_fare": self._final_fare,
            "status": self._status.value,
            "booking_time": self._booking_time,
            "cancellation_time": self._cancellation_time,
            "cancellation_reason": self._cancellation_reason,
        }

    def __str__(self) -> str:
        return (
            f"Ticket [{self._ticket_id}] Ref: {self._booking_reference} | "
            f"Seat {self._seat_number} on {self._travel_date} ({self._status.value}) - PHP {self._final_fare:.2f}"
        )

    def __repr__(self) -> str:
        return f"<Ticket id='{self._ticket_id}' ref='{self._booking_reference}' status='{self._status.value}'>"
