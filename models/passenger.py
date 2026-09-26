"""
Passenger model representing a commuter booking transit.
Includes PII sanitization, contact format validation, and concession ID verification (NFR-1).
"""
import re
from typing import Dict, Any, Optional

SUPPORTED_PASSENGER_TYPES = ("Regular", "Senior Citizen", "PWD", "Student")
CONCESSION_DISCOUNT_RATE = 0.20  # 20% statutory discount for Senior / PWD / Student


class Passenger:
    """
    Represents a transit passenger with validation and concession credentials.

    Attributes:
        _passenger_id (str): Unique passenger ID (e.g., 'PAS-1001').
        _name (str): Full legal name.
        _contact_number (str): Valid phone/mobile number.
        _passenger_type (str): Category from SUPPORTED_PASSENGER_TYPES.
        _discount_id (Optional[str]): Government/Institutional ID proving discount eligibility.
    """

    PHONE_REGEX = re.compile(r"^(\+639\d{9}|09\d{9}|\+?[1-9]\d{7,14})$")

    def __init__(
        self,
        passenger_id: str,
        name: str,
        contact_number: str,
        passenger_type: str = "Regular",
        discount_id: Optional[str] = None,
    ) -> None:
        if not isinstance(passenger_id, str):
            raise TypeError("Passenger ID must be a string")
        if not passenger_id.strip():
            raise ValueError("Passenger ID cannot be empty")
        self._passenger_id = passenger_id.strip()

        self.name = name
        self.contact_number = contact_number
        self.passenger_type = passenger_type
        self.discount_id = discount_id

    @property
    def passenger_id(self) -> str:
        """Return unique passenger ID (read-only)."""
        return self._passenger_id

    @property
    def name(self) -> str:
        """Return passenger full name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Passenger name must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Passenger name cannot be empty")
        if len(cleaned) < 2:
            raise ValueError("Passenger name must be at least 2 characters long")
        self._name = cleaned

    @property
    def contact_number(self) -> str:
        """Return validated contact number."""
        return self._contact_number

    @contact_number.setter
    def contact_number(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Contact number must be a string")
        # Strip spaces and hyphens for unified validation
        cleaned = re.sub(r"[\s\-]", "", value)
        if not self.PHONE_REGEX.match(cleaned):
            raise ValueError(
                f"Invalid contact number '{value}'. Expected standard mobile format (e.g., 09171234567 or +639171234567)"
            )
        self._contact_number = cleaned

    @property
    def passenger_type(self) -> str:
        """Return passenger classification category."""
        return self._passenger_type

    @passenger_type.setter
    def passenger_type(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Passenger type must be a string")
        cleaned = value.strip()
        if cleaned not in SUPPORTED_PASSENGER_TYPES:
            raise ValueError(
                f"Passenger type '{cleaned}' invalid. Must be one of: {', '.join(SUPPORTED_PASSENGER_TYPES)}"
            )
        self._passenger_type = cleaned

    @property
    def discount_id(self) -> Optional[str]:
        """Return government/institutional discount ID proof."""
        return self._discount_id

    @discount_id.setter
    def discount_id(self, value: Optional[str]) -> None:
        if self._passenger_type in ("Senior Citizen", "PWD", "Student"):
            if not value or not str(value).strip():
                raise ValueError(
                    f"A valid government/institutional ID is required for {self._passenger_type} fare discount (NFR-1)."
                )
            cleaned = str(value).strip()
            if len(cleaned) < 4:
                raise ValueError("Concession ID must be at least 4 characters long")
            self._discount_id = cleaned
        else:
            self._discount_id = str(value).strip() if value else None

    @property
    def is_concession_eligible(self) -> bool:
        """Check if passenger qualifies for concession discount."""
        return self._passenger_type in ("Senior Citizen", "PWD", "Student")

    @property
    def is_priority_passenger(self) -> bool:
        """Check if passenger qualifies for priority seating (Senior Citizen / PWD)."""
        return self._passenger_type in ("Senior Citizen", "PWD")

    def get_discount_rate(self) -> float:
        """Return fractional fare discount rate (e.g., 0.20 for 20%)."""
        return CONCESSION_DISCOUNT_RATE if self.is_concession_eligible else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert passenger to dictionary representation."""
        return {
            "passenger_id": self._passenger_id,
            "name": self._name,
            "contact_number": self._contact_number,
            "passenger_type": self._passenger_type,
            "discount_id": self._discount_id,
            "is_priority": self.is_priority_passenger,
        }

    def __str__(self) -> str:
        concession_info = f" [{self._discount_id}]" if self._discount_id else ""
        return f"{self._name} ({self._passenger_type}{concession_info}, {self._contact_number})"

    def __repr__(self) -> str:
        return f"<Passenger id='{self._passenger_id}' name='{self._name}' type='{self._passenger_type}'>"
