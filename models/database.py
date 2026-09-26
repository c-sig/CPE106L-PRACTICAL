"""
BusTicketingDatabase singleton with SQLite relational persistence.
Provides ACID-compliant transactions, conflict prevention (preventing double booking),
and comprehensive analytics querying.
"""
import json
import os
import sqlite3
from typing import Dict, List, Optional, Set, Tuple, Any

from contextlib import contextmanager

from .bus import Bus
from .passenger import Passenger
from .route import Route
from .ticket import Ticket, TicketStatus


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bus_ticketing.db")


class BusTicketingDatabase:
    """
    Singleton database controller managing SQLite persistence for the Bus Ticketing System.
    Guarantees data integrity, atomic transactions, and zero double-booking (NFR-2).
    """

    _instance: Optional["BusTicketingDatabase"] = None
    _initialized: bool = False

    def __new__(cls, db_path: Optional[str] = None) -> "BusTicketingDatabase":
        """Enforce the Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(BusTicketingDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize database connection and tables once."""
        if not self._initialized:
            self._db_path = db_path if db_path is not None else DEFAULT_DB_PATH
            self._setup_schema()
            self._initialized = True

    @contextmanager
    def get_connection(self):
        """Create and manage connection lifecycle to the SQLite database."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _setup_schema(self) -> None:
        """Create relational tables and partial unique indexes for seat collision prevention."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Routes Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS routes (
                    route_id TEXT PRIMARY KEY,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    distance_km REAL NOT NULL,
                    base_fare REAL NOT NULL,
                    departure_time TEXT NOT NULL,
                    bus_id TEXT NOT NULL
                );
                """
            )

            # 2. Buses Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS buses (
                    bus_id TEXT PRIMARY KEY,
                    bus_number TEXT NOT NULL,
                    bus_type TEXT NOT NULL,
                    total_seats INTEGER NOT NULL,
                    layout_rows INTEGER NOT NULL,
                    layout_cols INTEGER NOT NULL,
                    priority_seats_json TEXT NOT NULL
                );
                """
            )

            # 3. Passengers Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS passengers (
                    passenger_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_number TEXT NOT NULL,
                    passenger_type TEXT NOT NULL,
                    discount_id TEXT
                );
                """
            )

            # 4. Tickets Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    booking_reference TEXT UNIQUE NOT NULL,
                    route_id TEXT NOT NULL,
                    bus_id TEXT NOT NULL,
                    passenger_id TEXT NOT NULL,
                    seat_number INTEGER NOT NULL,
                    travel_date TEXT NOT NULL,
                    base_fare REAL NOT NULL,
                    discount_amount REAL NOT NULL,
                    final_fare REAL NOT NULL,
                    status TEXT NOT NULL,
                    booking_time TEXT NOT NULL,
                    cancellation_time TEXT,
                    cancellation_reason TEXT,
                    FOREIGN KEY (route_id) REFERENCES routes(route_id),
                    FOREIGN KEY (bus_id) REFERENCES buses(bus_id),
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
                );
                """
            )

            # NFR-2 & ACID: Enforce unique seat reservation per trip for active tickets
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_seat
                ON tickets (route_id, travel_date, seat_number)
                WHERE status = 'Confirmed';
                """
            )
            conn.commit()

    # =========================================================================
    # ROUTE OPERATIONS
    # =========================================================================
    def add_route(self, route: Route) -> None:
        """Persist a new route in the database."""
        if not isinstance(route, Route):
            raise TypeError("Expected Route instance")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO routes (route_id, origin, destination, distance_km, base_fare, departure_time, bus_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(route_id) DO UPDATE SET
                    origin=excluded.origin,
                    destination=excluded.destination,
                    distance_km=excluded.distance_km,
                    base_fare=excluded.base_fare,
                    departure_time=excluded.departure_time,
                    bus_id=excluded.bus_id;
                """,
                (
                    route.route_id,
                    route.origin,
                    route.destination,
                    route.distance_km,
                    route.base_fare,
                    route.departure_time,
                    route.bus_id,
                ),
            )
            conn.commit()

    def get_route(self, route_id: str) -> Optional[Route]:
        """Fetch a route by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM routes WHERE route_id = ?", (route_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Route(
                route_id=row["route_id"],
                origin=row["origin"],
                destination=row["destination"],
                distance_km=row["distance_km"],
                base_fare=row["base_fare"],
                departure_time=row["departure_time"],
                bus_id=row["bus_id"],
            )

    def get_all_routes(self) -> List[Route]:
        """Fetch all registered routes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM routes ORDER BY route_id")
            routes = []
            for row in cursor.fetchall():
                routes.append(
                    Route(
                        route_id=row["route_id"],
                        origin=row["origin"],
                        destination=row["destination"],
                        distance_km=row["distance_km"],
                        base_fare=row["base_fare"],
                        departure_time=row["departure_time"],
                        bus_id=row["bus_id"],
                    )
                )
            return routes

    # =========================================================================
    # BUS OPERATIONS
    # =========================================================================
    def add_bus(self, bus: Bus) -> None:
        """Persist a bus fleet unit."""
        if not isinstance(bus, Bus):
            raise TypeError("Expected Bus instance")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO buses (bus_id, bus_number, bus_type, total_seats, layout_rows, layout_cols, priority_seats_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bus_id) DO UPDATE SET
                    bus_number=excluded.bus_number,
                    bus_type=excluded.bus_type,
                    total_seats=excluded.total_seats,
                    layout_rows=excluded.layout_rows,
                    layout_cols=excluded.layout_cols,
                    priority_seats_json=excluded.priority_seats_json;
                """,
                (
                    bus.bus_id,
                    bus.bus_number,
                    bus.bus_type,
                    bus.total_seats,
                    bus.layout_rows,
                    bus.layout_cols,
                    json.dumps(bus.priority_seats),
                ),
            )
            conn.commit()

    def get_bus(self, bus_id: str) -> Optional[Bus]:
        """Fetch a bus by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM buses WHERE bus_id = ?", (bus_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Bus(
                bus_id=row["bus_id"],
                bus_number=row["bus_number"],
                bus_type=row["bus_type"],
                total_seats=row["total_seats"],
                layout_rows=row["layout_rows"],
                layout_cols=row["layout_cols"],
                priority_seats=json.loads(row["priority_seats_json"]),
            )

    def get_all_buses(self) -> List[Bus]:
        """Fetch all registered buses."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM buses ORDER BY bus_id")
            buses = []
            for row in cursor.fetchall():
                buses.append(
                    Bus(
                        bus_id=row["bus_id"],
                        bus_number=row["bus_number"],
                        bus_type=row["bus_type"],
                        total_seats=row["total_seats"],
                        layout_rows=row["layout_rows"],
                        layout_cols=row["layout_cols"],
                        priority_seats=json.loads(row["priority_seats_json"]),
                    )
                )
            return buses

    # =========================================================================
    # PASSENGER OPERATIONS
    # =========================================================================
    def add_passenger(self, passenger: Passenger) -> None:
        """Persist a passenger record."""
        if not isinstance(passenger, Passenger):
            raise TypeError("Expected Passenger instance")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO passengers (passenger_id, name, contact_number, passenger_type, discount_id)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(passenger_id) DO UPDATE SET
                    name=excluded.name,
                    contact_number=excluded.contact_number,
                    passenger_type=excluded.passenger_type,
                    discount_id=excluded.discount_id;
                """,
                (
                    passenger.passenger_id,
                    passenger.name,
                    passenger.contact_number,
                    passenger.passenger_type,
                    passenger.discount_id,
                ),
            )
            conn.commit()

    def get_passenger(self, passenger_id: str) -> Optional[Passenger]:
        """Fetch passenger by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM passengers WHERE passenger_id = ?", (passenger_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Passenger(
                passenger_id=row["passenger_id"],
                name=row["name"],
                contact_number=row["contact_number"],
                passenger_type=row["passenger_type"],
                discount_id=row["discount_id"],
            )

    def get_all_passengers(self) -> List[Passenger]:
        """Fetch all registered passengers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM passengers ORDER BY passenger_id")
            passengers = []
            for row in cursor.fetchall():
                passengers.append(
                    Passenger(
                        passenger_id=row["passenger_id"],
                        name=row["name"],
                        contact_number=row["contact_number"],
                        passenger_type=row["passenger_type"],
                        discount_id=row["discount_id"],
                    )
                )
            return passengers

    # =========================================================================
    # TICKET & BOOKING OPERATIONS (FR-1, FR-2, NFR-2)
    # =========================================================================
    def get_booked_seats(self, route_id: str, travel_date: str) -> Set[int]:
        """Return the set of currently occupied seat numbers for a route on a specific date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT seat_number FROM tickets
                WHERE route_id = ? AND travel_date = ? AND status = 'Confirmed'
                """,
                (route_id, travel_date),
            )
            return {row["seat_number"] for row in cursor.fetchall()}

    def book_ticket(self, ticket: Ticket) -> None:
        """
        Record a new ticket booking in SQLite within an ACID transaction.
        Enforces double-booking prevention at both application and database engine layers (NFR-2).

        Raises:
            ValueError: If the seat is already booked or transaction conflicts.
        """
        if not isinstance(ticket, Ticket):
            raise TypeError("Expected Ticket instance")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Pre-check active seat booking
            cursor.execute(
                """
                SELECT ticket_id, booking_reference FROM tickets
                WHERE route_id = ? AND travel_date = ? AND seat_number = ? AND status = 'Confirmed'
                """,
                (ticket.route_id, ticket.travel_date, ticket.seat_number),
            )
            existing = cursor.fetchone()
            if existing:
                raise ValueError(
                    f"Conflict: Seat {ticket.seat_number} on {ticket.travel_date} is already booked under ticket '{existing['ticket_id']}'."
                )

            try:
                cursor.execute(
                    """
                    INSERT INTO tickets (
                        ticket_id, booking_reference, route_id, bus_id, passenger_id,
                        seat_number, travel_date, base_fare, discount_amount, final_fare,
                        status, booking_time, cancellation_time, cancellation_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ticket.ticket_id,
                        ticket.booking_reference,
                        ticket.route_id,
                        ticket.bus_id,
                        ticket.passenger_id,
                        ticket.seat_number,
                        ticket.travel_date,
                        ticket.base_fare,
                        ticket.discount_amount,
                        ticket.final_fare,
                        ticket.status.value,
                        ticket.booking_time,
                        ticket.cancellation_time,
                        ticket.cancellation_reason,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Booking failed due to database constraint violation: {e}")

    def get_ticket(self, identifier: str) -> Optional[Ticket]:
        """
        Retrieve a ticket by either its Ticket ID (e.g. 'TKT-1001')
        or its unique Booking Reference Code (e.g. 'BTK-ABC123').
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tickets
                WHERE ticket_id = ? OR UPPER(booking_reference) = UPPER(?)
                """,
                (identifier.strip(), identifier.strip()),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_ticket(row)

    def get_all_tickets(self) -> List[Ticket]:
        """Fetch all tickets in descending order of booking time."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets ORDER BY booking_time DESC, ticket_id DESC")
            return [self._row_to_ticket(row) for row in cursor.fetchall()]

    def cancel_ticket(self, identifier: str, reason: str = "Passenger request") -> Ticket:
        """
        Cancel a ticket by Ticket ID or Booking Reference, releasing the seat back to the inventory (FR-2).

        Returns:
            The updated Ticket object.

        Raises:
            ValueError: If ticket is not found or already cancelled.
        """
        ticket = self.get_ticket(identifier)
        if not ticket:
            raise ValueError(f"No ticket found matching identifier '{identifier}'")

        ticket.cancel(reason=reason)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE tickets
                SET status = ?, cancellation_time = ?, cancellation_reason = ?
                WHERE ticket_id = ?
                """,
                (ticket.status.value, ticket.cancellation_time, ticket.cancellation_reason, ticket.ticket_id),
            )
            conn.commit()
        return ticket

    def _row_to_ticket(self, row: sqlite3.Row) -> Ticket:
        """Helper to convert a sqlite3.Row into a Ticket domain object."""
        status_map = {
            "Confirmed": TicketStatus.CONFIRMED,
            "Cancelled": TicketStatus.CANCELLED,
            "Completed": TicketStatus.COMPLETED,
        }
        status_enum = status_map.get(row["status"], TicketStatus.CONFIRMED)
        return Ticket(
            ticket_id=row["ticket_id"],
            booking_reference=row["booking_reference"],
            route_id=row["route_id"],
            bus_id=row["bus_id"],
            passenger_id=row["passenger_id"],
            seat_number=row["seat_number"],
            travel_date=row["travel_date"],
            base_fare=row["base_fare"],
            discount_amount=row["discount_amount"],
            final_fare=row["final_fare"],
            status=status_enum,
            booking_time=row["booking_time"],
            cancellation_time=row["cancellation_time"],
            cancellation_reason=row["cancellation_reason"],
        )

    # =========================================================================
    # SYSTEM ANALYTICS & METRICS
    # =========================================================================
    def get_analytics(self) -> Dict[str, Any]:
        """Compute operational analytics and fleet revenue KPI metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Ticket counts and revenue
            cursor.execute("SELECT COUNT(*) AS total FROM tickets")
            total_tickets = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS active FROM tickets WHERE status = 'Confirmed'")
            active_tickets = cursor.fetchone()["active"]

            cursor.execute("SELECT COUNT(*) AS cancelled FROM tickets WHERE status = 'Cancelled'")
            cancelled_tickets = cursor.fetchone()["cancelled"]

            cursor.execute("SELECT COALESCE(SUM(final_fare), 0.0) AS rev FROM tickets WHERE status = 'Confirmed'")
            gross_revenue = cursor.fetchone()["rev"]

            cursor.execute("SELECT COALESCE(SUM(discount_amount), 0.0) AS subsidies FROM tickets WHERE status = 'Confirmed'")
            total_subsidies = cursor.fetchone()["subsidies"]

            # Route breakdown
            cursor.execute(
                """
                SELECT r.route_id, r.origin, r.destination, b.total_seats,
                       COUNT(CASE WHEN t.status = 'Confirmed' THEN 1 END) as confirmed_count
                FROM routes r
                JOIN buses b ON r.bus_id = b.bus_id
                LEFT JOIN tickets t ON r.route_id = t.route_id
                GROUP BY r.route_id
                """
            )
            route_stats = []
            for r_row in cursor.fetchall():
                tot_seats = r_row["total_seats"]
                confirmed = r_row["confirmed_count"]
                occupancy_rate = (confirmed / tot_seats * 100.0) if tot_seats > 0 else 0.0
                route_stats.append({
                    "route_id": r_row["route_id"],
                    "origin": r_row["origin"],
                    "destination": r_row["destination"],
                    "capacity": tot_seats,
                    "confirmed_seats": confirmed,
                    "occupancy_rate": occupancy_rate,
                })

            return {
                "total_tickets": total_tickets,
                "active_tickets": active_tickets,
                "cancelled_tickets": cancelled_tickets,
                "gross_revenue": round(gross_revenue, 2),
                "total_subsidies": round(total_subsidies, 2),
                "route_stats": route_stats,
            }

    # =========================================================================
    # TEST ISOLATION & RESET
    # =========================================================================
    def clear_all(self) -> None:
        """Purge all table records for test suite reset."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tickets")
            cursor.execute("DELETE FROM passengers")
            cursor.execute("DELETE FROM routes")
            cursor.execute("DELETE FROM buses")
            conn.commit()

    @classmethod
    def reset_singleton(cls, db_path: Optional[str] = None) -> None:
        """Reset the singleton instance (primarily for test fixture isolation)."""
        cls._instance = None
        cls._initialized = False
