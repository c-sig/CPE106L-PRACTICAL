"""
Route model representing a scheduled bus transit route.
Follows Lab3/Lab4 encapsulation and property validation patterns.
"""
from typing import Dict, Any


class Route:
    """
    Represents an intercity or suburban bus transit route.

    Attributes:
        _route_id (str): Unique route identifier (e.g., 'RT-101').
        _origin (str): Departure terminal / city.
        _destination (str): Arrival terminal / city.
        _distance_km (float): Total route distance in kilometers.
        _base_fare (float): Standard one-way passenger ticket price.
        _departure_time (str): Scheduled departure time (e.g., '08:00 AM').
        _bus_id (str): Bus assigned to service this route.
    """

    def __init__(
        self,
        route_id: str,
        origin: str,
        destination: str,
        distance_km: float,
        base_fare: float,
        departure_time: str,
        bus_id: str,
    ) -> None:
        """
        Initialize a Route instance with strict type and boundary validations.
        """
        if not isinstance(route_id, str):
            raise TypeError("Route ID must be a string")
        if not route_id.strip():
            raise ValueError("Route ID cannot be empty")
        self._route_id = route_id.strip()

        # Enforce validation rules via property setters
        self.origin = origin
        self.destination = destination
        self.distance_km = distance_km
        self.base_fare = base_fare
        self.departure_time = departure_time
        self.bus_id = bus_id

    @property
    def route_id(self) -> str:
        """Return the unique route identifier (read-only)."""
        return self._route_id

    @property
    def origin(self) -> str:
        """Return the departure city/terminal."""
        return self._origin

    @origin.setter
    def origin(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Origin must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Origin cannot be empty")
        self._origin = cleaned

    @property
    def destination(self) -> str:
        """Return the arrival destination city/terminal."""
        return self._destination

    @destination.setter
    def destination(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Destination must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Destination cannot be empty")
        self._destination = cleaned

    @property
    def distance_km(self) -> float:
        """Return route distance in kilometers."""
        return self._distance_km

    @distance_km.setter
    def distance_km(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Distance must be a numeric value")
        if value <= 0:
            raise ValueError("Distance must be strictly positive (> 0 km)")
        self._distance_km = float(value)

    @property
    def base_fare(self) -> float:
        """Return base ticket fare."""
        return self._base_fare

    @base_fare.setter
    def base_fare(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Base fare must be a numeric value")
        if value < 0:
            raise ValueError("Base fare cannot be negative")
        self._base_fare = round(float(value), 2)

    @property
    def departure_time(self) -> str:
        """Return scheduled departure time."""
        return self._departure_time

    @departure_time.setter
    def departure_time(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Departure time must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Departure time cannot be empty")
        self._departure_time = cleaned

    @property
    def bus_id(self) -> str:
        """Return the assigned bus ID."""
        return self._bus_id

    @bus_id.setter
    def bus_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Bus ID must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Bus ID cannot be empty")
        self._bus_id = cleaned

    def get_summary(self) -> str:
        """Return a formatted route itinerary string."""
        return f"{self._origin} -> {self._destination} ({self._departure_time}, PHP {self._base_fare:.2f})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert route attributes into a dictionary for serialization/display."""
        return {
            "route_id": self._route_id,
            "origin": self._origin,
            "destination": self._destination,
            "distance_km": self._distance_km,
            "base_fare": self._base_fare,
            "departure_time": self._departure_time,
            "bus_id": self._bus_id,
        }

    def __str__(self) -> str:
        return f"Route [{self._route_id}]: {self._origin} -> {self._destination} @ {self._departure_time}"

    def __repr__(self) -> str:
        return f"<Route route_id='{self._route_id}' origin='{self._origin}' dest='{self._destination}'>"
