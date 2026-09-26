"""
Models package for the Bus Ticketing System.
Exports core domain entities, enumerations, database singleton, and factories.
"""
from .bus import Bus, SUPPORTED_BUS_TYPES
from .database import BusTicketingDatabase
from .factory import BusFactory, TicketFactory
from .passenger import (
    Passenger,
    SUPPORTED_PASSENGER_TYPES,
    CONCESSION_DISCOUNT_RATE,
)
from .route import Route
from .ticket import Ticket, TicketStatus

__all__ = [
    "Bus",
    "SUPPORTED_BUS_TYPES",
    "BusTicketingDatabase",
    "BusFactory",
    "TicketFactory",
    "Passenger",
    "SUPPORTED_PASSENGER_TYPES",
    "CONCESSION_DISCOUNT_RATE",
    "Route",
    "Ticket",
    "TicketStatus",
]
