"""
Bus model representing a fleet vehicle in the transit system.
Features cabin seating configuration and priority seat designations.
"""
from typing import Dict, List, Any


SUPPORTED_BUS_TYPES = ("Standard AC", "Executive Deluxe", "Super Sleeper")


class Bus:
    """
    Represents a bus unit in the ticketing fleet.

    Attributes:
        _bus_id (str): Unique bus identifier (e.g., 'BUS-01').
        _bus_number (str): Plate or fleet number (e.g., 'DLTB-8012').
        _bus_type (str): Bus category from SUPPORTED_BUS_TYPES.
        _total_seats (int): Number of total passenger seats.
        _layout_rows (int): Number of rows in cabin (e.g., 6).
        _layout_cols (int): Number of columns in cabin (e.g., 4: 2 left, aisle, 2 right).
        _priority_seats (List[int]): Seat numbers reserved for Senior Citizens / PWDs / Pregnant.
    """

    def __init__(
        self,
        bus_id: str,
        bus_number: str,
        bus_type: str,
        total_seats: int = 24,
        layout_rows: int = 6,
        layout_cols: int = 4,
        priority_seats: List[int] = None,
    ) -> None:
        if not isinstance(bus_id, str):
            raise TypeError("Bus ID must be a string")
        if not bus_id.strip():
            raise ValueError("Bus ID cannot be empty")
        self._bus_id = bus_id.strip()

        self.bus_number = bus_number
        self.bus_type = bus_type
        self.total_seats = total_seats
        self.layout_rows = layout_rows
        self.layout_cols = layout_cols

        # Default priority seats to front row (seats 1, 2, 3, 4) if not specified
        if priority_seats is None:
            self._priority_seats = [1, 2, 3, 4]
        else:
            self.priority_seats = priority_seats

    @property
    def bus_id(self) -> str:
        """Return the unique bus ID (read-only)."""
        return self._bus_id

    @property
    def bus_number(self) -> str:
        """Return the fleet/plate number."""
        return self._bus_number

    @bus_number.setter
    def bus_number(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Bus number must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Bus number cannot be empty")
        self._bus_number = cleaned

    @property
    def bus_type(self) -> str:
        """Return the bus class/type."""
        return self._bus_type

    @bus_type.setter
    def bus_type(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Bus type must be a string")
        cleaned = value.strip()
        if cleaned not in SUPPORTED_BUS_TYPES:
            raise ValueError(
                f"Bus type '{cleaned}' invalid. Must be one of: {', '.join(SUPPORTED_BUS_TYPES)}"
            )
        self._bus_type = cleaned

    @property
    def total_seats(self) -> int:
        """Return total seat count."""
        return self._total_seats

    @total_seats.setter
    def total_seats(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Total seats must be an integer")
        if value < 8 or value > 60:
            raise ValueError("Total seats must be between 8 and 60")
        self._total_seats = value

    @property
    def layout_rows(self) -> int:
        """Return number of seating rows."""
        return self._layout_rows

    @layout_rows.setter
    def layout_rows(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Layout rows must be an integer")
        if value <= 0:
            raise ValueError("Layout rows must be positive")
        self._layout_rows = value

    @property
    def layout_cols(self) -> int:
        """Return number of seating columns."""
        return self._layout_cols

    @layout_cols.setter
    def layout_cols(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Layout columns must be an integer")
        if value != 4 and value != 3:
            raise ValueError("Layout columns must be 3 (2+1) or 4 (2+2)")
        self._layout_cols = value

    @property
    def priority_seats(self) -> List[int]:
        """Return list of priority seat numbers."""
        return list(self._priority_seats)

    @priority_seats.setter
    def priority_seats(self, value: List[int]) -> None:
        if not isinstance(value, list):
            raise TypeError("Priority seats must be a list of seat numbers")
        for seat in value:
            if not isinstance(seat, int) or seat < 1 or seat > self._total_seats:
                raise ValueError(f"Priority seat {seat} is out of valid range (1-{self._total_seats})")
        self._priority_seats = sorted(list(set(value)))

    def is_priority_seat(self, seat_num: int) -> bool:
        """Check if a specific seat number is designated as priority."""
        return seat_num in self._priority_seats

    def to_dict(self) -> Dict[str, Any]:
        """Convert bus attributes to dictionary representation."""
        return {
            "bus_id": self._bus_id,
            "bus_number": self._bus_number,
            "bus_type": self._bus_type,
            "total_seats": self._total_seats,
            "layout_rows": self._layout_rows,
            "layout_cols": self._layout_cols,
            "priority_seats": self._priority_seats,
        }

    def __str__(self) -> str:
        return f"Bus [{self._bus_id}]: {self._bus_number} ({self._bus_type}, {self._total_seats} seats)"

    def __repr__(self) -> str:
        return f"<Bus bus_id='{self._bus_id}' number='{self._bus_number}'>"
