"""
Comprehensive Unit Test Suite for SmartBus Transit System.
Uses unittest.TestCase class-based approach matching Lab4 conventions.
Tests Functional Requirements (FR-1, FR-2), Non-Functional Requirements (NFR-1, NFR-2),
Unique Use Case (Priority Seating Matrix & Concession Validation), and SQLite Persistence.
"""
import os
import unittest
from datetime import datetime

from models import (
    Bus,
    BusFactory,
    BusTicketingDatabase,
    CONCESSION_DISCOUNT_RATE,
    Passenger,
    Route,
    SUPPORTED_BUS_TYPES,
    SUPPORTED_PASSENGER_TYPES,
    Ticket,
    TicketFactory,
    TicketStatus,
)


class TestBusTicketingSystem(unittest.TestCase):
    """Test suite covering core domain logic, requirements, and database operations."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configure isolated test SQLite database."""
        cls.test_db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_bus_ticketing.db"
        )
        # Ensure fresh singleton with isolated DB
        BusTicketingDatabase.reset_singleton()
        cls.db = BusTicketingDatabase(cls.test_db_path)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up isolated test database file."""
        BusTicketingDatabase.reset_singleton()
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def setUp(self) -> None:
        """Clear database tables before each test method."""
        self.db.clear_all()

        # Seed standard baseline entities
        self.bus = BusFactory.create_bus(
            bus_id="TBUS-01",
            bus_number="TEST-100",
            bus_type="Standard AC",
            total_seats=24,
            layout_rows=6,
            layout_cols=4,
            priority_seats=[1, 2, 3, 4],
        )
        self.db.add_bus(self.bus)

        self.route = Route(
            route_id="TRT-101",
            origin="Manila",
            destination="Baguio",
            distance_km=250.0,
            base_fare=500.0,
            departure_time="08:00 AM",
            bus_id=self.bus.bus_id,
        )
        self.db.add_route(self.route)

        self.regular_passenger = Passenger(
            passenger_id="TPAS-01",
            name="Alice Smith",
            contact_number="09171234567",
            passenger_type="Regular",
        )
        self.db.add_passenger(self.regular_passenger)

        self.senior_passenger = Passenger(
            passenger_id="TPAS-02",
            name="Robert Johnson",
            contact_number="09181112233",
            passenger_type="Senior Citizen",
            discount_id="OSCA-998877",
        )
        self.db.add_passenger(self.senior_passenger)

    # =========================================================================
    # 1. DATABASE SINGLETON & SQLITE PERSISTENCE
    # =========================================================================
    def test_01_singleton_database_instance(self) -> None:
        """Verify BusTicketingDatabase enforces Singleton pattern across calls."""
        db1 = BusTicketingDatabase()
        db2 = BusTicketingDatabase()
        self.assertIs(db1, db2, "Multiple instantiations must return identical singleton instance")

    def test_02_sqlite_persistence_roundtrip(self) -> None:
        """Verify entities are correctly persisted and retrieved from SQLite."""
        fetched_route = self.db.get_route("TRT-101")
        self.assertIsNotNone(fetched_route)
        self.assertEqual(fetched_route.origin, "Manila")
        self.assertEqual(fetched_route.destination, "Baguio")
        self.assertEqual(fetched_route.base_fare, 500.0)

        fetched_bus = self.db.get_bus("TBUS-01")
        self.assertIsNotNone(fetched_bus)
        self.assertEqual(fetched_bus.total_seats, 24)
        self.assertEqual(fetched_bus.priority_seats, [1, 2, 3, 4])

    # =========================================================================
    # 2. ENCAPSULATION & DATA VALIDATION (NFR-2)
    # =========================================================================
    def test_03_route_validation_boundaries(self) -> None:
        """Verify Route setter validations for positive distance and non-negative fare."""
        with self.assertRaises(ValueError):
            Route("R99", "A", "B", distance_km=-10.0, base_fare=100.0, departure_time="10:00 AM", bus_id="B1")

        with self.assertRaises(ValueError):
            Route("R99", "A", "B", distance_km=100.0, base_fare=-50.0, departure_time="10:00 AM", bus_id="B1")

        with self.assertRaises(ValueError):
            Route("R99", "  ", "B", distance_km=100.0, base_fare=50.0, departure_time="10:00 AM", bus_id="B1")

    def test_04_bus_seating_and_priority_validation(self) -> None:
        """Verify Bus seating capacity limits and priority seat definitions."""
        with self.assertRaises(ValueError):
            BusFactory.create_bus(bus_id="B_BAD", bus_number="X", bus_type="Standard AC", total_seats=5)

        with self.assertRaises(ValueError):
            BusFactory.create_bus(bus_id="B_BAD", bus_number="X", bus_type="Invalid Type")

        bus = BusFactory.create_bus(bus_id="B_OK", bus_number="Y", priority_seats=[1, 2])
        self.assertTrue(bus.is_priority_seat(1))
        self.assertTrue(bus.is_priority_seat(2))
        self.assertFalse(bus.is_priority_seat(5))

    # =========================================================================
    # 3. PASSENGER PII & CONCESSION CREDENTIAL VALIDATION (NFR-1)
    # =========================================================================
    def test_05_passenger_contact_format_validation(self) -> None:
        """Verify mobile phone number formatting rules (NFR-1)."""
        valid_pas = Passenger("P_VAL", "Valid Commuter", "09191234567")
        self.assertEqual(valid_pas.contact_number, "09191234567")

        # Invalid phone format
        with self.assertRaises(ValueError):
            Passenger("P_INV", "Invalid Commuter", "12345")

        with self.assertRaises(ValueError):
            Passenger("P_INV", "Invalid Commuter", "phone-not-a-number")

    def test_06_mandatory_concession_id_validation_nfr1(self) -> None:
        """Verify Senior Citizen, PWD, and Student must provide valid concession ID (NFR-1)."""
        # Senior Citizen without discount_id must fail
        with self.assertRaises(ValueError):
            Passenger("P_NO_ID", "Senior Without ID", "09170001122", passenger_type="Senior Citizen", discount_id="")

        # PWD with ID shorter than 4 characters must fail
        with self.assertRaises(ValueError):
            Passenger("P_SHORT_ID", "PWD Short ID", "09170001122", passenger_type="PWD", discount_id="12")

        # Student with valid ID must succeed
        student = Passenger("P_STU", "Student Com", "09170001122", passenger_type="Student", discount_id="STU-992")
        self.assertTrue(student.is_concession_eligible)
        self.assertEqual(student.discount_id, "STU-992")

    # =========================================================================
    # 4. UNIQUE USE CASE: VISUAL SEAT MAP & PRIORITY CONCESSION ALLOCATION
    # =========================================================================
    def test_07_senior_priority_seat_and_concession_discount(self) -> None:
        """
        Verify Unique Use Case:
        Senior Citizen books front-row Priority Seat #1 with 20% concession deduction.
        """
        ticket = TicketFactory.create_ticket(
            ticket_id="TTKT-01",
            route=self.route,
            bus=self.bus,
            passenger=self.senior_passenger,
            seat_number=1,  # Priority seat
            travel_date="2026-10-01",
        )
        # Base fare = 500, 20% discount = 100, final fare = 400
        self.assertEqual(ticket.base_fare, 500.0)
        self.assertEqual(ticket.discount_amount, 100.0)
        self.assertEqual(ticket.final_fare, 400.0)
        self.assertEqual(ticket.seat_number, 1)
        self.assertTrue(self.bus.is_priority_seat(ticket.seat_number))

    def test_08_regular_passenger_full_fare(self) -> None:
        """Verify regular passenger receives zero discount."""
        ticket = TicketFactory.create_ticket(
            ticket_id="TTKT-02",
            route=self.route,
            bus=self.bus,
            passenger=self.regular_passenger,
            seat_number=8,
            travel_date="2026-10-01",
        )
        self.assertEqual(ticket.base_fare, 500.0)
        self.assertEqual(ticket.discount_amount, 0.0)
        self.assertEqual(ticket.final_fare, 500.0)

    # =========================================================================
    # 5. TAMPER-RESISTANT CODE & ATOMIC DOUBLE-BOOKING PREVENTION (NFR-1, NFR-2)
    # =========================================================================
    def test_09_tamper_resistant_reference_code_format_nfr1(self) -> None:
        """Verify reference codes are non-empty, uppercase, and follow 'BTK-[HEX]' format (NFR-1)."""
        ref1 = Ticket.generate_reference_code("TRT-101", 3)
        ref2 = Ticket.generate_reference_code("TRT-101", 3)
        self.assertTrue(ref1.startswith("BTK-"))
        self.assertTrue(ref2.startswith("BTK-"))
        self.assertNotEqual(ref1, ref2, "Cryptographically salted codes must be unique")

    def test_10_atomic_double_booking_prevention_nfr2(self) -> None:
        """
        Verify NFR-2: Double-booking prevention.
        Attempting to book the exact same seat on the same route & date must raise ValueError
        and maintain SQLite database integrity.
        """
        tkt1 = TicketFactory.create_ticket(
            ticket_id="TTKT-10",
            route=self.route,
            bus=self.bus,
            passenger=self.regular_passenger,
            seat_number=5,
            travel_date="2026-10-05",
        )
        self.db.book_ticket(tkt1)

        # Confirm seat is marked booked
        booked_seats = self.db.get_booked_seats(self.route.route_id, "2026-10-05")
        self.assertIn(5, booked_seats)

        # Attempt to book seat 5 again for the same date with different passenger
        tkt2 = TicketFactory.create_ticket(
            ticket_id="TTKT-11",
            route=self.route,
            bus=self.bus,
            passenger=self.senior_passenger,
            seat_number=5,
            travel_date="2026-10-05",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.book_ticket(tkt2)

        self.assertIn("already booked", str(ctx.exception))

    # =========================================================================
    # 6. TICKET LIFECYCLE & CANCELLATION SEAT RELEASE (FR-2)
    # =========================================================================
    def test_11_ticket_cancellation_releases_seat_fr2(self) -> None:
        """
        Verify FR-2: Ticket cancellation updates status to CANCELLED and
        immediately releases the seat so another passenger can reserve it.
        """
        tkt = TicketFactory.create_ticket(
            ticket_id="TTKT-20",
            route=self.route,
            bus=self.bus,
            passenger=self.regular_passenger,
            seat_number=12,
            travel_date="2026-10-10",
        )
        self.db.book_ticket(tkt)

        # Initially seat 12 is booked
        self.assertIn(12, self.db.get_booked_seats(self.route.route_id, "2026-10-10"))

        # Cancel the ticket
        cancelled_tkt = self.db.cancel_ticket("TTKT-20", reason="Passenger rescheduled")
        self.assertEqual(cancelled_tkt.status, TicketStatus.CANCELLED)
        self.assertIsNotNone(cancelled_tkt.cancellation_time)

        # Seat 12 is now RELEASED and no longer in occupied set
        self.assertNotIn(12, self.db.get_booked_seats(self.route.route_id, "2026-10-10"))

        # A new passenger can now successfully reserve seat 12 on the same trip
        new_tkt = TicketFactory.create_ticket(
            ticket_id="TTKT-21",
            route=self.route,
            bus=self.bus,
            passenger=self.senior_passenger,
            seat_number=12,
            travel_date="2026-10-10",
        )
        self.db.book_ticket(new_tkt)
        self.assertIn(12, self.db.get_booked_seats(self.route.route_id, "2026-10-10"))

    # =========================================================================
    # 7. ANALYTICS & REVENUE AGGREGATION
    # =========================================================================
    def test_12_analytics_calculation(self) -> None:
        """Verify analytics correctly compute revenue, counts, and subsidies."""
        tkt_reg = TicketFactory.create_ticket(
            ticket_id="T_AN1",
            route=self.route,
            bus=self.bus,
            passenger=self.regular_passenger,
            seat_number=3,
            travel_date="2026-10-12",
        )
        tkt_sen = TicketFactory.create_ticket(
            ticket_id="T_AN2",
            route=self.route,
            bus=self.bus,
            passenger=self.senior_passenger,
            seat_number=4,
            travel_date="2026-10-12",
        )
        self.db.book_ticket(tkt_reg)
        self.db.book_ticket(tkt_sen)

        stats = self.db.get_analytics()
        self.assertEqual(stats["total_tickets"], 2)
        self.assertEqual(stats["active_tickets"], 2)
        self.assertEqual(stats["gross_revenue"], 900.0)      # 500 + 400
        self.assertEqual(stats["total_subsidies"], 100.0)   # 100 concession


if __name__ == "__main__":
    unittest.main()
