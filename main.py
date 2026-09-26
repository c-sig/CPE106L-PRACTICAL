"""
Main entry point for the SmartBus Intercity Bus Ticketing System.
Pre-loads comprehensive sample routes, fleet buses, passengers, and bookings into SQLite,
then initializes and launches the BusTicketingApp GUI.
Matches the structure and conventions of Lab3 and Lab4.
"""
from typing import Optional

from models import (
    Bus,
    BusFactory,
    BusTicketingDatabase,
    Passenger,
    Route,
    Ticket,
    TicketFactory,
    TicketStatus,
)
from app import BusTicketingApp


def initialize_sample_data(database: Optional[BusTicketingDatabase] = None) -> BusTicketingDatabase:
    """
    Initialize and populate the SQLite database singleton with sample operational data:
      - 4 Transit Routes across major intercity destinations
      - 4 Fleet Buses with configured seating layouts and priority seat rows
      - 4 Sample Passengers (Regular, Senior Citizen, PWD, and Student with ID credentials)
      - 3 Initial Bookings demonstrating priority seating, statutory discounts, and normal fares

    Args:
        database: Optional BusTicketingDatabase instance. Defaults to the singleton.

    Returns:
        BusTicketingDatabase: The populated database instance.
    """
    db = database if database is not None else BusTicketingDatabase()
    # Reset database records for idempotent execution
    db.clear_all()

    # -------------------------------------------------------------------------
    # 1. Register Fleet Buses (4 Buses)
    # -------------------------------------------------------------------------
    bus1 = BusFactory.create_bus(
        bus_id="BUS-01",
        bus_number="DLTB-8012",
        bus_type="Standard AC",
        total_seats=24,
        layout_rows=6,
        layout_cols=4,
        priority_seats=[1, 2, 3, 4],  # Front row designated priority
    )
    bus2 = BusFactory.create_bus(
        bus_id="BUS-02",
        bus_number="JAC-3045",
        bus_type="Standard AC",
        total_seats=24,
        layout_rows=6,
        layout_cols=4,
        priority_seats=[1, 2, 3, 4],
    )
    bus3 = BusFactory.create_bus(
        bus_id="BUS-03",
        bus_number="VCT-9910",
        bus_type="Executive Deluxe",
        total_seats=24,
        layout_rows=6,
        layout_cols=4,
        priority_seats=[1, 2, 3, 4],
    )
    bus4 = BusFactory.create_bus(
        bus_id="BUS-04",
        bus_number="PARTAS-550",
        bus_type="Super Sleeper",
        total_seats=24,
        layout_rows=6,
        layout_cols=4,
        priority_seats=[1, 2, 3, 4],
    )

    db.add_bus(bus1)
    db.add_bus(bus2)
    db.add_bus(bus3)
    db.add_bus(bus4)

    # -------------------------------------------------------------------------
    # 2. Register Transit Routes (4 Intercity Routes)
    # -------------------------------------------------------------------------
    route1 = Route(
        route_id="RT-101",
        origin="Manila (Cubao)",
        destination="Baguio City",
        distance_km=245.0,
        base_fare=580.0,
        departure_time="08:00 AM",
        bus_id=bus1.bus_id,
    )
    route2 = Route(
        route_id="RT-102",
        origin="Manila (Buendia)",
        destination="Batangas Port",
        distance_km=105.0,
        base_fare=230.0,
        departure_time="09:30 AM",
        bus_id=bus2.bus_id,
    )
    route3 = Route(
        route_id="RT-103",
        origin="Manila (Cubao)",
        destination="Naga City",
        distance_km=380.0,
        base_fare=850.0,
        departure_time="08:30 PM",
        bus_id=bus3.bus_id,
    )
    route4 = Route(
        route_id="RT-104",
        origin="Manila (Pasay)",
        destination="La Union (San Juan)",
        distance_km=270.0,
        base_fare=620.0,
        departure_time="10:00 AM",
        bus_id=bus4.bus_id,
    )

    db.add_route(route1)
    db.add_route(route2)
    db.add_route(route3)
    db.add_route(route4)

    # -------------------------------------------------------------------------
    # 3. Register Passengers (4 diverse commuter classifications)
    # -------------------------------------------------------------------------
    pas1 = Passenger(
        passenger_id="PAS-1001",
        name="Maria Santos",
        contact_number="09171234567",
        passenger_type="Senior Citizen",
        discount_id="OSCA-77491",
    )
    pas2 = Passenger(
        passenger_id="PAS-1002",
        name="Juan Dela Cruz",
        contact_number="09189876543",
        passenger_type="Regular",
    )
    pas3 = Passenger(
        passenger_id="PAS-1003",
        name="Grace Ramos",
        contact_number="09205556677",
        passenger_type="PWD",
        discount_id="PWD-44120",
    )
    pas4 = Passenger(
        passenger_id="PAS-1004",
        name="Mark Bautista",
        contact_number="09083332211",
        passenger_type="Student",
        discount_id="STU-2023-9081",
    )

    db.add_passenger(pas1)
    db.add_passenger(pas2)
    db.add_passenger(pas3)
    db.add_passenger(pas4)

    # -------------------------------------------------------------------------
    # 4. Issue Sample Bookings
    # -------------------------------------------------------------------------
    travel_date = "2026-09-28"

    # Ticket 1: Senior Citizen reserving Priority Seat 1 on RT-101 (20% Concession)
    ticket1 = TicketFactory.create_ticket(
        ticket_id="TKT-1001",
        route=route1,
        bus=bus1,
        passenger=pas1,
        seat_number=1,
        travel_date=travel_date,
        booking_reference="BTK-8F3A29",
    )

    # Ticket 2: Regular passenger booking Seat 7 on RT-101 (Standard Fare)
    ticket2 = TicketFactory.create_ticket(
        ticket_id="TKT-1002",
        route=route1,
        bus=bus1,
        passenger=pas2,
        seat_number=7,
        travel_date=travel_date,
        booking_reference="BTK-4C91E2",
    )

    # Ticket 3: PWD passenger booking Priority Seat 2 on RT-102 (20% Concession)
    ticket3 = TicketFactory.create_ticket(
        ticket_id="TKT-1003",
        route=route2,
        bus=bus2,
        passenger=pas3,
        seat_number=2,
        travel_date=travel_date,
        booking_reference="BTK-1D77A0",
    )

    db.book_ticket(ticket1)
    db.book_ticket(ticket2)
    db.book_ticket(ticket3)

    return db


def main() -> None:
    """Entry point: initialize SQLite sample database and launch GUI."""
    db = initialize_sample_data()
    app = BusTicketingApp(db)
    app.mainloop()


if __name__ == "__main__":
    main()
