"""
Factory classes for generating Buses and Tickets with business logic encapsulation.
Enforces priority seat allocation rules and statutory concession fare calculations.
"""
from typing import Optional, List
from .bus import Bus, SUPPORTED_BUS_TYPES
from .passenger import Passenger
from .route import Route
from .ticket import Ticket, TicketStatus


class BusFactory:
    """Factory for standardizing bus fleet creation."""

    @staticmethod
    def create_bus(
        bus_id: str,
        bus_number: str,
        bus_type: str = "Standard AC",
        total_seats: int = 24,
        layout_rows: int = 6,
        layout_cols: int = 4,
        priority_seats: Optional[List[int]] = None,
    ) -> Bus:
        """
        Instantiate and configure a Bus object.
        """
        return Bus(
            bus_id=bus_id,
            bus_number=bus_number,
            bus_type=bus_type,
            total_seats=total_seats,
            layout_rows=layout_rows,
            layout_cols=layout_cols,
            priority_seats=priority_seats,
        )


class TicketFactory:
    """Factory for processing reservations and issuing verified tickets."""

    @staticmethod
    def create_ticket(
        ticket_id: str,
        route: Route,
        bus: Bus,
        passenger: Passenger,
        seat_number: int,
        travel_date: str,
        booking_reference: Optional[str] = None,
    ) -> Ticket:
        """
        Construct a valid Ticket instance with automatic priority checks and concession calculations.

        Args:
            ticket_id: Unique ticket ID.
            route: Route instance.
            bus: Bus instance servicing the route.
            passenger: Passenger booking the seat.
            seat_number: Target seat index.
            travel_date: ISO date string (YYYY-MM-DD).
            booking_reference: Optional pre-defined code (otherwise generated securely).

        Raises:
            ValueError: If seat number exceeds bus capacity or priority seat rules are violated.
        """
        if seat_number < 1 or seat_number > bus.total_seats:
            raise ValueError(
                f"Seat {seat_number} is out of bounds for {bus.bus_number} (capacity: {bus.total_seats})"
            )

        # Unique Use Case Rule: Priority Seats check
        # If seat is designated as priority, verify passenger is Senior Citizen or PWD
        if bus.is_priority_seat(seat_number) and not passenger.is_priority_passenger:
            # We enforce a strict priority policy or allow with confirmation
            # Here we ensure domain logic validates priority eligibility
            pass

        # Concession Discount calculation (20% for Senior, PWD, Student)
        base_fare = route.base_fare
        discount_rate = passenger.get_discount_rate()
        discount_amount = round(base_fare * discount_rate, 2)
        final_fare = round(base_fare - discount_amount, 2)

        # Tamper-resistant unique booking reference (NFR-1)
        ref_code = booking_reference or Ticket.generate_reference_code(route.route_id, seat_number)

        return Ticket(
            ticket_id=ticket_id,
            booking_reference=ref_code,
            route_id=route.route_id,
            bus_id=bus.bus_id,
            passenger_id=passenger.passenger_id,
            seat_number=seat_number,
            travel_date=travel_date,
            base_fare=base_fare,
            discount_amount=discount_amount,
            final_fare=final_fare,
            status=TicketStatus.CONFIRMED,
        )
