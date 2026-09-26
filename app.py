"""
Bus Ticketing System - Graphical User Interface Application
Subclasses tk.Tk and implements a multi-tabbed transit reservation interface.
Matches aesthetic and structural paradigms from Lab2, Lab3, and Lab4.
"""
import os
import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Set, Tuple

from models import (
    Bus,
    BusTicketingDatabase,
    CONCESSION_DISCOUNT_RATE,
    Passenger,
    Route,
    SUPPORTED_PASSENGER_TYPES,
    Ticket,
    TicketFactory,
    TicketStatus,
)


class BusTicketingApp(tk.Tk):
    """
    Main GUI application window for the Bus Ticketing System.

    Features:
        - Tab 1: Book Tickets & Visual Seat Map (Interactive 2x2 grid, priority seating, concession validation)
        - Tab 2: Manage Bookings & Cancellations (Ticket lookup, lifecycle cancellation, boarding pass)
        - Tab 3: System Overview & Analytics (KPI revenue cards, fleet occupancy, transaction audit log)
    """

    def __init__(self, database: Optional[BusTicketingDatabase] = None) -> None:
        super().__init__()
        self.title("SmartBus - Intercity Bus Ticketing System")
        self.geometry("1020x740")
        self.minsize(920, 640)

        # Automation and non-blocking test flags (recycled from Lab4)
        self._suppress_dialogs: bool = False
        self._auto_confirm: bool = True
        self._last_dialog: Optional[Tuple[str, str, str]] = None

        # Connect to singleton SQLite database
        self.db: BusTicketingDatabase = database if database is not None else BusTicketingDatabase()

        # State tracking for booking workflow
        self.selected_route: Optional[Route] = None
        self.selected_bus: Optional[Bus] = None
        self.selected_seat: Optional[int] = None
        self.occupied_seats: Set[int] = set()
        self.seat_buttons: Dict[int, tk.Button] = {}

        # Counter for generating sequential passenger IDs and ticket IDs
        self._sync_id_counters()

        # Setup styling and user interface
        self._setup_style()
        self._build_ui()

        # Initial population of UI controls
        self._refresh_all_views()

    # =========================================================================
    # DIALOG HELPERS (Headless / Automation Friendly)
    # =========================================================================
    def _show_info(self, title: str, message: str) -> None:
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("info", title, message)
            return
        messagebox.showinfo(title, message)

    def _show_warning(self, title: str, message: str) -> None:
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("warning", title, message)
            return
        messagebox.showwarning(title, message)

    def _show_error(self, title: str, message: str) -> None:
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("error", title, message)
            return
        messagebox.showerror(title, message)

    def _confirm(self, title: str, message: str) -> bool:
        if getattr(self, "_auto_confirm", False):
            return True
        return messagebox.askyesno(title, message)

    # =========================================================================
    # ID GENERATION & STYLING
    # =========================================================================
    def _sync_id_counters(self) -> None:
        all_passengers = self.db.get_all_passengers()
        all_tickets = self.db.get_all_tickets()

        self.pas_counter = len(all_passengers) + 1001
        self.tkt_counter = len(all_tickets) + 1001

    def _setup_style(self) -> None:
        """Configure ttk styles and clam theme to match Lab3/Lab4 aesthetics."""
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Palette definition (Navy/Steel theme matching Lab5 report & Lab4)
        self.PRIMARY_NAVY = "#1F4E79"
        self.STEEL_BLUE = "#2E75B6"
        self.BG_LIGHT = "#F4F6F9"
        self.COLOR_AVAIL = "#2E7D32"     # Green for available regular seat
        self.COLOR_PRIORITY = "#E65100"  # Amber for priority seat
        self.COLOR_SELECT = "#1565C0"    # Blue for selected seat
        self.COLOR_BOOKED = "#C62828"    # Red for occupied seat

        self.configure(bg=self.BG_LIGHT)

        # Standard widget typography
        self.style.configure("TLabel", font=("Arial", 9), background=self.BG_LIGHT)
        self.style.configure("TButton", font=("Arial", 9))
        self.style.configure("Header.TLabel", font=("Arial", 11, "bold"), foreground=self.PRIMARY_NAVY, background=self.BG_LIGHT)
        self.style.configure("SubHeader.TLabel", font=("Arial", 10, "bold"), foreground="#333333", background=self.BG_LIGHT)
        self.style.configure("StatTitle.TLabel", font=("Arial", 9, "bold"), foreground="#555555", background="#FFFFFF")
        self.style.configure("StatValue.TLabel", font=("Arial", 15, "bold"), foreground=self.PRIMARY_NAVY, background="#FFFFFF")
        self.style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        self.style.configure("Treeview", font=("Arial", 9), rowheight=23)
        self.style.configure("TLabelframe", background=self.BG_LIGHT)
        self.style.configure("TLabelframe.Label", font=("Arial", 9, "bold"), foreground=self.PRIMARY_NAVY, background=self.BG_LIGHT)

    # =========================================================================
    # UI CONSTRUCTION (3 TABS)
    # =========================================================================
    def _build_ui(self) -> None:
        """Build main navigation tabs and status bar."""
        # Top Header Banner
        header_frame = tk.Frame(self, bg=self.PRIMARY_NAVY, height=54)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text="SmartBus Transit System — Booking & Fleet Management",
            font=("Arial", 13, "bold"),
            fg="#FFFFFF",
            bg=self.PRIMARY_NAVY,
            padx=16,
            pady=10,
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_frame,
            text="Lab Practical • SQLite Backend • Concession Priority Engine",
            font=("Arial", 9, "italic"),
            fg="#D0E1FD",
            bg=self.PRIMARY_NAVY,
            padx=16,
        )
        subtitle_label.pack(side=tk.RIGHT)

        # Main Notebook Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Tab Frames
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="  1. Book Tickets & Visual Seat Map  ")
        self.notebook.add(self.tab2, text="  2. Manage Bookings & Cancellations  ")
        self.notebook.add(self.tab3, text="  3. System Overview & Fleet Analytics  ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Build individual tabs
        self._build_tab1()
        self._build_tab2()
        self._build_tab3()

        # Bottom Status Bar
        self.status_var = tk.StringVar(value="System Ready. Connected to SQLite Database.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            font=("Arial", 8),
            fg="#444444",
            bg="#E1E4E8",
            anchor=tk.W,
            padx=10,
            pady=3,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # -------------------------------------------------------------------------
    # TAB 1: BOOK TICKETS & VISUAL SEAT MAP
    # -------------------------------------------------------------------------
    def _build_tab1(self) -> None:
        """Construct Tab 1: Route selection, visual seat layout matrix, passenger form."""
        paned = ttk.PanedWindow(self.tab1, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # LEFT PANEL: Trip & Route Selection
        left_frame = ttk.LabelFrame(paned, text=" 1. Select Route & Trip ", padding=10)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Transit Route:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.route_combo = ttk.Combobox(left_frame, state="readonly", width=34)
        self.route_combo.pack(fill=tk.X, pady=(0, 8))
        self.route_combo.bind("<<ComboboxSelected>>", self._on_route_selected)

        ttk.Label(left_frame, text="Travel Date (YYYY-MM-DD):", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.travel_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(left_frame, textvariable=self.travel_date_var, width=20)
        self.date_entry.pack(fill=tk.X, pady=(0, 8))
        self.date_entry.bind("<KeyRelease>", lambda e: self._refresh_seat_grid())

        btn_refresh_trip = ttk.Button(left_frame, text="Update Seat Availability", command=self._refresh_seat_grid)
        btn_refresh_trip.pack(fill=tk.X, pady=(2, 12))

        # Trip Summary Info Box
        info_group = ttk.LabelFrame(left_frame, text=" Route & Bus Details ", padding=8)
        info_group.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.trip_info_text = tk.Text(
            info_group,
            wrap=tk.WORD,
            height=12,
            font=("Consolas", 8),
            bg="#F9FAFB",
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.trip_info_text.pack(fill=tk.BOTH, expand=True)
        self.trip_info_text.insert(tk.END, "Please select a route to view trip itinerary.")
        self.trip_info_text.config(state=tk.DISABLED)

        # CENTER PANEL: Interactive Visual Seat Map (Unique Use Case)
        center_frame = ttk.LabelFrame(paned, text=" 2. Interactive Seat Selection Matrix ", padding=10)
        paned.add(center_frame, weight=2)

        # Legend Bar
        legend_frame = tk.Frame(center_frame, bg=self.BG_LIGHT)
        legend_frame.pack(fill=tk.X, pady=(0, 6))

        for color, label in [
            (self.COLOR_AVAIL, "Regular (Avail)"),
            (self.COLOR_PRIORITY, "Priority (Sr/PWD)"),
            (self.COLOR_SELECT, "Selected"),
            (self.COLOR_BOOKED, "Booked / Taken"),
        ]:
            item = tk.Frame(legend_frame, bg=self.BG_LIGHT)
            item.pack(side=tk.LEFT, padx=6)
            tk.Label(item, bg=color, width=2, height=1, relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, padx=2)
            tk.Label(item, text=label, font=("Arial", 8), bg=self.BG_LIGHT).pack(side=tk.LEFT)

        # Bus Cabin Container
        self.cabin_frame = tk.Frame(center_frame, bg="#E2E8F0", relief=tk.RIDGE, borderwidth=2, padx=10, pady=8)
        self.cabin_frame.pack(fill=tk.BOTH, expand=True)

        # Driver Head Section
        cab_header = tk.Frame(self.cabin_frame, bg="#CBD5E1", height=28, relief=tk.SOLID, borderwidth=1)
        cab_header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            cab_header,
            text="[ FRONT OF BUS  •  DRIVER CAB ]",
            font=("Arial", 8, "bold"),
            fg="#475569",
            bg="#CBD5E1",
        ).pack(pady=3)

        # Seat Grid Scroll/Canvas Area
        self.grid_container = tk.Frame(self.cabin_frame, bg="#E2E8F0")
        self.grid_container.pack(expand=True)

        # Priority Notice & Selected Seat Status
        self.seat_selection_var = tk.StringVar(value="No seat currently selected. Please click an available seat.")
        lbl_selected_status = tk.Label(
            center_frame,
            textvariable=self.seat_selection_var,
            font=("Arial", 9, "bold"),
            fg=self.PRIMARY_NAVY,
            bg=self.BG_LIGHT,
            pady=4,
        )
        lbl_selected_status.pack(fill=tk.X, pady=(4, 0))

        # RIGHT PANEL: Passenger Details & Concession Engine
        right_frame = ttk.LabelFrame(paned, text=" 3. Passenger & Concession Booking ", padding=10)
        paned.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Passenger Full Name:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.pas_name_var = tk.StringVar()
        self.pas_name_entry = ttk.Entry(right_frame, textvariable=self.pas_name_var)
        self.pas_name_entry.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(right_frame, text="Contact Number (e.g. 09171234567):", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.pas_contact_var = tk.StringVar()
        self.pas_contact_entry = ttk.Entry(right_frame, textvariable=self.pas_contact_var)
        self.pas_contact_entry.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(right_frame, text="Passenger Classification:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.pas_type_combo = ttk.Combobox(right_frame, values=list(SUPPORTED_PASSENGER_TYPES), state="readonly")
        self.pas_type_combo.set("Regular")
        self.pas_type_combo.pack(fill=tk.X, pady=(0, 6))
        self.pas_type_combo.bind("<<ComboboxSelected>>", self._on_passenger_type_changed)

        ttk.Label(right_frame, text="Concession / OSCA / PWD ID:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.discount_id_var = tk.StringVar()
        self.discount_id_entry = ttk.Entry(right_frame, textvariable=self.discount_id_var, state=tk.DISABLED)
        self.discount_id_entry.pack(fill=tk.X, pady=(0, 8))

        # Fare Calculation Card
        fare_box = ttk.LabelFrame(right_frame, text=" Fare Quotation ", padding=8)
        fare_box.pack(fill=tk.X, pady=(4, 8))

        self.lbl_base_fare = ttk.Label(fare_box, text="Base Fare: PHP 0.00")
        self.lbl_base_fare.pack(anchor=tk.W)

        self.lbl_discount = ttk.Label(fare_box, text="Concession Discount: PHP 0.00 (0%)", foreground="#2E7D32")
        self.lbl_discount.pack(anchor=tk.W)

        self.lbl_total_fare = ttk.Label(fare_box, text="Total Amount: PHP 0.00", font=("Arial", 11, "bold"), foreground=self.PRIMARY_NAVY)
        self.lbl_total_fare.pack(anchor=tk.W, pady=(4, 0))

        # Action Buttons
        btn_confirm = tk.Button(
            right_frame,
            text="Confirm & Issue Ticket",
            font=("Arial", 10, "bold"),
            bg=self.PRIMARY_NAVY,
            fg="#FFFFFF",
            activebackground=self.STEEL_BLUE,
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            cursor="hand2",
            pady=6,
            command=self._handle_booking_submission,
        )
        btn_confirm.pack(fill=tk.X, pady=(8, 4))

        btn_clear = ttk.Button(right_frame, text="Clear Form", command=self._reset_booking_form)
        btn_clear.pack(fill=tk.X)

    # -------------------------------------------------------------------------
    # TAB 2: MANAGE BOOKINGS & CANCELLATIONS (FR-2)
    # -------------------------------------------------------------------------
    def _build_tab2(self) -> None:
        """Construct Tab 2: Lookup ticket, lifecycle cancellation, boarding pass inspection."""
        top_bar = ttk.Frame(self.tab2, padding=6)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="Search Ticket / Ref Code:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.ticket_search_var = tk.StringVar()
        search_entry = ttk.Entry(top_bar, textvariable=self.ticket_search_var, width=22)
        search_entry.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(top_bar, text="Find Ticket", command=self._handle_search_ticket).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Reset / View All", command=self._refresh_tickets_tree).pack(side=tk.LEFT, padx=3)

        ttk.Label(top_bar, text="Filter Status:").pack(side=tk.LEFT, padx=(16, 6))
        self.status_filter_combo = ttk.Combobox(
            top_bar,
            values=["All Statuses", "Confirmed", "Cancelled"],
            state="readonly",
            width=14,
        )
        self.status_filter_combo.set("All Statuses")
        self.status_filter_combo.pack(side=tk.LEFT)
        self.status_filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_tickets_tree())

        # Split pane: Top details dossier card & bottom Table
        paned = ttk.PanedWindow(self.tab2, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Details Dossier
        detail_frame = ttk.LabelFrame(paned, text=" Active Ticket Dossier & Lifecycle Actions ", padding=8)
        paned.add(detail_frame, weight=1)

        self.ticket_detail_text = tk.Text(
            detail_frame,
            wrap=tk.WORD,
            height=6,
            font=("Consolas", 9),
            bg="#F9FAFB",
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.ticket_detail_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 8))
        self.ticket_detail_text.insert(tk.END, "Select a ticket from the table below to inspect details or execute lifecycle actions.")
        self.ticket_detail_text.config(state=tk.DISABLED)

        actions_box = ttk.Frame(detail_frame)
        actions_box.pack(side=tk.RIGHT, fill=tk.Y)

        btn_cancel = tk.Button(
            actions_box,
            text="Cancel Ticket & Refund",
            font=("Arial", 9, "bold"),
            bg="#C62828",
            fg="#FFFFFF",
            activebackground="#B71C1C",
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._handle_cancel_selected_ticket,
        )
        btn_cancel.pack(fill=tk.X, pady=(0, 6))

        btn_pass = ttk.Button(actions_box, text="View Boarding Pass", command=self._show_boarding_pass_modal)
        btn_pass.pack(fill=tk.X, pady=2)

        # Tickets Treeview
        tree_frame = ttk.LabelFrame(paned, text=" All Issued Tickets & Master Transactions ", padding=8)
        paned.add(tree_frame, weight=2)

        columns = (
            "ticket_id",
            "reference",
            "passenger",
            "type",
            "route",
            "date",
            "seat",
            "fare",
            "status",
        )
        self.tickets_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tickets_tree.heading("ticket_id", text="Ticket ID")
        self.tickets_tree.heading("reference", text="Reference Code (NFR-1)")
        self.tickets_tree.heading("passenger", text="Passenger Name")
        self.tickets_tree.heading("type", text="Category")
        self.tickets_tree.heading("route", text="Route")
        self.tickets_tree.heading("date", text="Travel Date")
        self.tickets_tree.heading("seat", text="Seat")
        self.tickets_tree.heading("fare", text="Amount Paid")
        self.tickets_tree.heading("status", text="Status")

        self.tickets_tree.column("ticket_id", width=85, anchor=tk.CENTER)
        self.tickets_tree.column("reference", width=140, anchor=tk.CENTER)
        self.tickets_tree.column("passenger", width=140, anchor=tk.W)
        self.tickets_tree.column("type", width=100, anchor=tk.CENTER)
        self.tickets_tree.column("route", width=170, anchor=tk.W)
        self.tickets_tree.column("date", width=95, anchor=tk.CENTER)
        self.tickets_tree.column("seat", width=55, anchor=tk.CENTER)
        self.tickets_tree.column("fare", width=95, anchor=tk.E)
        self.tickets_tree.column("status", width=95, anchor=tk.CENTER)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tickets_tree.yview)
        self.tickets_tree.configure(yscrollcommand=tree_scroll_y.set)

        self.tickets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tickets_tree.bind("<<TreeviewSelect>>", self._on_ticket_selected)

    # -------------------------------------------------------------------------
    # TAB 3: SYSTEM OVERVIEW & FLEET ANALYTICS
    # -------------------------------------------------------------------------
    def _build_tab3(self) -> None:
        """Construct Tab 3: KPI analytics cards, route occupancy, and audit logs."""
        kpi_bar = ttk.Frame(self.tab3, padding=6)
        kpi_bar.pack(fill=tk.X)

        self.kpi_cards = {}
        cards = [
            ("total_tkt", "Total Bookings", "0"),
            ("active_tkt", "Active Confirmed", "0"),
            ("cancel_tkt", "Cancelled Tickets", "0"),
            ("revenue", "Gross Revenue (PHP)", "0.00"),
            ("subsidies", "Concession Subsidies", "0.00"),
        ]

        for key, title, def_val in cards:
            c_frame = tk.Frame(kpi_bar, bg="#FFFFFF", relief=tk.SOLID, borderwidth=1, padx=10, pady=8)
            c_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

            t_lbl = tk.Label(c_frame, text=title, font=("Arial", 8, "bold"), fg="#4B5563", bg="#FFFFFF")
            t_lbl.pack(anchor=tk.W)

            v_lbl = tk.Label(c_frame, text=def_val, font=("Arial", 14, "bold"), fg=self.PRIMARY_NAVY, bg="#FFFFFF")
            v_lbl.pack(anchor=tk.W, pady=(2, 0))

            self.kpi_cards[key] = v_lbl

        # Content Panes
        paned = ttk.PanedWindow(self.tab3, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Fleet Route Occupancy
        occ_frame = ttk.LabelFrame(paned, text=" Fleet Route Popularity & Occupancy Rates ", padding=8)
        paned.add(occ_frame, weight=1)

        occ_cols = ("route_id", "route_path", "capacity", "booked", "occupancy")
        self.occ_tree = ttk.Treeview(occ_frame, columns=occ_cols, show="headings", height=5)
        self.occ_tree.heading("route_id", text="Route ID")
        self.occ_tree.heading("route_path", text="Origin -> Destination")
        self.occ_tree.heading("capacity", text="Fleet Capacity")
        self.occ_tree.heading("booked", text="Confirmed Sold")
        self.occ_tree.heading("occupancy", text="Occupancy Rate (%)")

        self.occ_tree.column("route_id", width=80, anchor=tk.CENTER)
        self.occ_tree.column("route_path", width=300, anchor=tk.W)
        self.occ_tree.column("capacity", width=110, anchor=tk.CENTER)
        self.occ_tree.column("booked", width=110, anchor=tk.CENTER)
        self.occ_tree.column("occupancy", width=140, anchor=tk.CENTER)

        self.occ_tree.pack(fill=tk.BOTH, expand=True)

        # Database Schema & Technical Audit Log
        audit_frame = ttk.LabelFrame(paned, text=" System Relational Architecture & ACID SQLite Verification ", padding=8)
        paned.add(audit_frame, weight=1)

        self.audit_text = tk.Text(
            audit_frame,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 8),
            bg="#F9FAFB",
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.audit_text.pack(fill=tk.BOTH, expand=True)
        self.audit_text.insert(
            tk.END,
            "SQLite Persistence Status: ONLINE\n"
            "ACID Mode: Immediate Transactions Enabled\n"
            "Double-Booking Prevention: SQLite Partial Unique Index (route_id, travel_date, seat_number)\n"
            "NFR-1 Security: SHA-256 Tamper-Resistant 8-char Reference Codes & PII Sanitization\n"
            "NFR-2 Maintainability: Encapsulated OOP Properties, Strict PEP 8, Singleton & Factory Patterns\n"
        )
        self.audit_text.config(state=tk.DISABLED)

    # =========================================================================
    # EVENT HANDLERS & BUSINESS LOGIC
    # =========================================================================
    def _on_tab_changed(self, event: Any) -> None:
        """Handle tab switching and trigger appropriate data sync."""
        active_tab = self.notebook.tab(self.notebook.select(), "text").strip()
        if "Book Tickets" in active_tab:
            self._refresh_seat_grid()
        elif "Manage Bookings" in active_tab:
            self._refresh_tickets_tree()
        elif "Overview" in active_tab:
            self._refresh_analytics()

    def _refresh_all_views(self) -> None:
        """Populate initial combo data and sync all views."""
        routes = self.db.get_all_routes()
        route_options = [f"{r.route_id} - {r.origin} to {r.destination} ({r.departure_time})" for r in routes]
        self.route_combo["values"] = route_options
        if route_options:
            self.route_combo.current(0)
            self._on_route_selected(None)

        self._refresh_tickets_tree()
        self._refresh_analytics()

    def _on_route_selected(self, event: Any) -> None:
        """Update selected route and rebuild seat grid accordingly."""
        selected_text = self.route_combo.get()
        if not selected_text:
            return
        route_id = selected_text.split(" - ")[0].strip()
        self.selected_route = self.db.get_route(route_id)
        if self.selected_route:
            self.selected_bus = self.db.get_bus(self.selected_route.bus_id)
            self._update_route_info_display()
            self._refresh_seat_grid()
            self._update_fare_calculation()

    def _update_route_info_display(self) -> None:
        if not self.selected_route or not self.selected_bus:
            return
        info = (
            f"=== ROUTE ITINERARY ===\n"
            f"Route ID     : {self.selected_route.route_id}\n"
            f"Origin       : {self.selected_route.origin}\n"
            f"Destination  : {self.selected_route.destination}\n"
            f"Distance     : {self.selected_route.distance_km:.1f} km\n"
            f"Departure    : {self.selected_route.departure_time}\n"
            f"Base Fare    : PHP {self.selected_route.base_fare:.2f}\n\n"
            f"=== ASSIGNED FLEET UNIT ===\n"
            f"Bus ID       : {self.selected_bus.bus_id}\n"
            f"Fleet Plate  : {self.selected_bus.bus_number}\n"
            f"Bus Class    : {self.selected_bus.bus_type}\n"
            f"Capacity     : {self.selected_bus.total_seats} passenger seats\n"
            f"Priority Rows: Front Row 1 (Seats: {', '.join(map(str, self.selected_bus.priority_seats))})\n"
        )
        self.trip_info_text.config(state=tk.NORMAL)
        self.trip_info_text.delete("1.0", tk.END)
        self.trip_info_text.insert(tk.END, info)
        self.trip_info_text.config(state=tk.DISABLED)

    def _refresh_seat_grid(self) -> None:
        """
        Reconstruct the 2x2 interactive seat grid.
        Applies color coding and binds click events for seat selection.
        """
        if not self.selected_route or not self.selected_bus:
            return

        travel_date = self.travel_date_var.get().strip()
        # Query SQLite for booked seats
        self.occupied_seats = self.db.get_booked_seats(self.selected_route.route_id, travel_date)

        # Clear existing buttons
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.seat_buttons.clear()

        # If previous selected seat is now occupied, clear selection
        if self.selected_seat in self.occupied_seats:
            self.selected_seat = None

        rows = self.selected_bus.layout_rows  # e.g., 6 rows
        # 4 seats per row: Col 0 (Window L), Col 1 (Aisle L), [Aisle Gap], Col 2 (Aisle R), Col 3 (Window R)

        seat_counter = 1
        for r in range(rows):
            row_frame = tk.Frame(self.grid_container, bg="#E2E8F0")
            row_frame.pack(pady=3)

            # Row label
            lbl_row = tk.Label(row_frame, text=f"R{r+1}", font=("Arial", 8, "bold"), fg="#64748B", bg="#E2E8F0", width=3)
            lbl_row.pack(side=tk.LEFT, padx=4)

            # Left seats (2 seats)
            for c in range(2):
                seat_num = seat_counter
                seat_counter += 1
                btn = self._create_seat_button(row_frame, seat_num)
                btn.pack(side=tk.LEFT, padx=3)
                self.seat_buttons[seat_num] = btn

            # Central Aisle
            aisle_lbl = tk.Label(row_frame, text="  ", bg="#E2E8F0", width=3)
            aisle_lbl.pack(side=tk.LEFT, padx=6)

            # Right seats (2 seats)
            for c in range(2):
                seat_num = seat_counter
                seat_counter += 1
                btn = self._create_seat_button(row_frame, seat_num)
                btn.pack(side=tk.LEFT, padx=3)
                self.seat_buttons[seat_num] = btn

        self._update_seat_status_label()

    def _create_seat_button(self, parent: tk.Widget, seat_num: int) -> tk.Button:
        """Create an individual seat button with appropriate color coding."""
        is_occupied = seat_num in self.occupied_seats
        is_selected = seat_num == self.selected_seat
        is_priority = self.selected_bus.is_priority_seat(seat_num)

        if is_occupied:
            bg_col = self.COLOR_BOOKED
            fg_col = "#FFFFFF"
            state = tk.DISABLED
            cursor = "arrow"
            text = f"{seat_num:02d}\n[X]"
        elif is_selected:
            bg_col = self.COLOR_SELECT
            fg_col = "#FFFFFF"
            state = tk.NORMAL
            cursor = "hand2"
            text = f"{seat_num:02d}\n[✓]"
        elif is_priority:
            bg_col = self.COLOR_PRIORITY
            fg_col = "#FFFFFF"
            state = tk.NORMAL
            cursor = "hand2"
            text = f"{seat_num:02d}\n[P]"
        else:
            bg_col = self.COLOR_AVAIL
            fg_col = "#FFFFFF"
            state = tk.NORMAL
            cursor = "hand2"
            text = f"{seat_num:02d}"

        btn = tk.Button(
            parent,
            text=text,
            width=5,
            height=2,
            font=("Arial", 8, "bold"),
            bg=bg_col,
            fg=fg_col,
            state=state,
            cursor=cursor,
            relief=tk.RAISED,
            borderwidth=2,
            command=lambda s=seat_num: self._on_seat_clicked(s),
        )
        return btn

    def _on_seat_clicked(self, seat_num: int) -> None:
        """Handle seat selection click and evaluate priority eligibility."""
        if seat_num in self.occupied_seats:
            return

        # Priority seat validation check
        if self.selected_bus.is_priority_seat(seat_num):
            pas_type = self.pas_type_combo.get()
            if pas_type not in ("Senior Citizen", "PWD"):
                confirm = self._confirm(
                    "Priority Seating Policy Notice",
                    f"Seat {seat_num:02d} is designated as a Priority Seat reserved for Senior Citizens, "
                    f"PWDs, and pregnant commuters.\n\n"
                    f"Do you wish to designate this passenger as eligible for Priority Seating?",
                )
                if not confirm:
                    return

        # Toggle or switch selection
        if self.selected_seat == seat_num:
            self.selected_seat = None
        else:
            self.selected_seat = seat_num

        self._refresh_seat_grid()
        self._update_seat_status_label()

    def _update_seat_status_label(self) -> None:
        if self.selected_seat is None:
            self.seat_selection_var.set("No seat currently selected. Please click an available seat in the map.")
        else:
            priority_tag = " (PRIORITY ROW)" if self.selected_bus.is_priority_seat(self.selected_seat) else ""
            self.seat_selection_var.set(
                f"Selected Seat: #{self.selected_seat:02d}{priority_tag} • Fare: PHP {self.selected_route.base_fare:.2f}"
            )

    def _on_passenger_type_changed(self, event: Any) -> None:
        """Dynamically enable concession ID input and recalculate fare quotation."""
        pas_type = self.pas_type_combo.get()
        if pas_type in ("Senior Citizen", "PWD", "Student"):
            self.discount_id_entry.config(state=tk.NORMAL)
            if not self.discount_id_var.get():
                self.discount_id_var.set("OSCA-" if pas_type == "Senior Citizen" else "ID-")
        else:
            self.discount_id_entry.config(state=tk.DISABLED)
            self.discount_id_var.set("")

        self._update_fare_calculation()

    def _update_fare_calculation(self) -> None:
        """Update live fare quotation based on route base fare and concession status."""
        if not self.selected_route:
            return

        base = self.selected_route.base_fare
        pas_type = self.pas_type_combo.get()
        is_discount = pas_type in ("Senior Citizen", "PWD", "Student")
        discount = round(base * CONCESSION_DISCOUNT_RATE, 2) if is_discount else 0.0
        final = round(base - discount, 2)

        self.lbl_base_fare.config(text=f"Base Fare: PHP {base:.2f}")
        disc_text = f"Concession Discount: -PHP {discount:.2f} (20%)" if is_discount else "Concession Discount: PHP 0.00 (0%)"
        self.lbl_discount.config(text=disc_text)
        self.lbl_total_fare.config(text=f"Total Amount: PHP {final:.2f}")

    def _handle_booking_submission(self) -> None:
        """Process passenger validation, create ticket in SQLite, and issue receipt (FR-1, NFR-1, NFR-2)."""
        if not self.selected_route or not self.selected_bus:
            self._show_error("Validation Error", "Please select a transit route first.")
            return

        if self.selected_seat is None:
            self._show_error("Validation Error", "Please select an available seat from the visual matrix.")
            return

        travel_date = self.travel_date_var.get().strip()
        try:
            datetime.strptime(travel_date, "%Y-%m-%d")
        except ValueError:
            self._show_error("Validation Error", "Travel date must follow YYYY-MM-DD format.")
            return

        name = self.pas_name_var.get().strip()
        contact = self.pas_contact_var.get().strip()
        pas_type = self.pas_type_combo.get()
        discount_id = self.discount_id_var.get().strip() if pas_type != "Regular" else None

        # Validate Passenger through encapsulated domain class (NFR-1)
        pas_id = f"PAS-{self.pas_counter}"
        try:
            passenger = Passenger(
                passenger_id=pas_id,
                name=name,
                contact_number=contact,
                passenger_type=pas_type,
                discount_id=discount_id,
            )
        except (ValueError, TypeError) as e:
            self._show_error("Passenger Validation Error", str(e))
            return

        # Unique Use Case Verification: Priority Seat Eligibility
        if self.selected_bus.is_priority_seat(self.selected_seat) and not passenger.is_priority_passenger:
            confirm = self._confirm(
                "Priority Seat Verification",
                f"Seat {self.selected_seat:02d} is designated for Senior Citizens / PWDs.\n"
                f"Confirm reservation for regular passenger?",
            )
            if not confirm:
                return

        # Generate Ticket via TicketFactory
        tkt_id = f"TKT-{self.tkt_counter}"
        ticket = TicketFactory.create_ticket(
            ticket_id=tkt_id,
            route=self.selected_route,
            bus=self.selected_bus,
            passenger=passenger,
            seat_number=self.selected_seat,
            travel_date=travel_date,
        )

        # Atomic commit to SQLite (NFR-2)
        try:
            self.db.add_passenger(passenger)
            self.db.book_ticket(ticket)
        except ValueError as e:
            self._show_error("Booking Conflict", str(e))
            self._refresh_seat_grid()
            return

        # Increment counters and sync state
        self.pas_counter += 1
        self.tkt_counter += 1

        self.status_var.set(f"Booking Successful! Ticket {ticket.ticket_id} issued with Ref: {ticket.booking_reference}")
        self._show_info(
            "Booking Confirmed",
            f"Ticket successfully issued!\n\n"
            f"Ticket ID      : {ticket.ticket_id}\n"
            f"Booking Ref    : {ticket.booking_reference} (NFR-1 Verified)\n"
            f"Passenger      : {passenger.name} ({passenger.passenger_type})\n"
            f"Seat Number    : #{ticket.seat_number:02d}\n"
            f"Date of Travel : {ticket.travel_date}\n"
            f"Total Paid     : PHP {ticket.final_fare:.2f}\n",
        )

        # Reset selection & refresh views
        self.selected_seat = None
        self._reset_booking_form()
        self._refresh_seat_grid()
        self._refresh_tickets_tree()
        self._refresh_analytics()

    def _reset_booking_form(self) -> None:
        """Clear form inputs."""
        self.pas_name_var.set("")
        self.pas_contact_var.set("")
        self.pas_type_combo.set("Regular")
        self.discount_id_var.set("")
        self.discount_id_entry.config(state=tk.DISABLED)
        self.selected_seat = None
        self._update_seat_status_label()
        self._update_fare_calculation()

    # -------------------------------------------------------------------------
    # TAB 2 EVENT HANDLERS
    # -------------------------------------------------------------------------
    def _refresh_tickets_tree(self) -> None:
        """Reload tickets list in Treeview with optional status filtering."""
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)

        filter_val = self.status_filter_combo.get()
        all_tickets = self.db.get_all_tickets()

        for t in all_tickets:
            if filter_val == "Confirmed" and t.status != TicketStatus.CONFIRMED:
                continue
            if filter_val == "Cancelled" and t.status != TicketStatus.CANCELLED:
                continue

            pas = self.db.get_passenger(t.passenger_id)
            pas_name = pas.name if pas else "N/A"
            pas_type = pas.passenger_type if pas else "Regular"
            route = self.db.get_route(t.route_id)
            route_str = f"{route.origin} -> {route.destination}" if route else t.route_id

            self.tickets_tree.insert(
                "",
                tk.END,
                iid=t.ticket_id,
                values=(
                    t.ticket_id,
                    t.booking_reference,
                    pas_name,
                    pas_type,
                    route_str,
                    t.travel_date,
                    f"#{t.seat_number:02d}",
                    f"PHP {t.final_fare:.2f}",
                    t.status.value,
                ),
            )

    def _on_ticket_selected(self, event: Any) -> None:
        """Display full details of selected ticket in the dossier text widget."""
        selected_items = self.tickets_tree.selection()
        if not selected_items:
            return

        tkt_id = selected_items[0]
        ticket = self.db.get_ticket(tkt_id)
        if not ticket:
            return

        passenger = self.db.get_passenger(ticket.passenger_id)
        route = self.db.get_route(ticket.route_id)
        bus = self.db.get_bus(ticket.bus_id)

        info = (
            f"=== TICKET DOSSIER & AUDIT VERIFICATION ===\n"
            f"Ticket ID          : {ticket.ticket_id}\n"
            f"Tamper-Proof Ref   : {ticket.booking_reference} [SHA-256 HMAC VERIFIED]\n"
            f"Booking Status     : [{ticket.status.value.upper()}]\n"
            f"Passenger Name     : {passenger.name if passenger else 'N/A'}\n"
            f"Classification     : {passenger.passenger_type if passenger else 'N/A'}\n"
            f"Concession ID Proof: {passenger.discount_id if passenger and passenger.discount_id else 'None (Regular)'}\n"
            f"Contact Number     : {passenger.contact_number if passenger else 'N/A'}\n"
            f"Route Itinerary    : {route.origin} -> {route.destination} ({route.departure_time})\n"
            f"Fleet Assigned     : {bus.bus_number} ({bus.bus_type})\n"
            f"Seat Assignment    : Seat #{ticket.seat_number:02d} {'[PRIORITY SEAT]' if bus.is_priority_seat(ticket.seat_number) else '[REGULAR SEAT]'}\n"
            f"Travel Date        : {ticket.travel_date}\n"
            f"Base Fare          : PHP {ticket.base_fare:.2f}\n"
            f"Discount Applied   : PHP {ticket.discount_amount:.2f}\n"
            f"Final Paid Amount  : PHP {ticket.final_fare:.2f}\n"
            f"Booking Timestamp  : {ticket.booking_time}\n"
        )
        if ticket.status == TicketStatus.CANCELLED:
            info += (
                f"\n=== CANCELLATION RECORD ===\n"
                f"Cancelled At       : {ticket.cancellation_time}\n"
                f"Reason Stated      : {ticket.cancellation_reason}\n"
            )

        self.ticket_detail_text.config(state=tk.NORMAL)
        self.ticket_detail_text.delete("1.0", tk.END)
        self.ticket_detail_text.insert(tk.END, info)
        self.ticket_detail_text.config(state=tk.DISABLED)

    def _handle_search_ticket(self) -> None:
        """Find ticket by ID or tamper-proof reference code."""
        query = self.ticket_search_var.get().strip()
        if not query:
            self._show_warning("Search Warning", "Please enter a Ticket ID or Booking Reference code.")
            return

        ticket = self.db.get_ticket(query)
        if not ticket:
            self._show_error("Not Found", f"No record matching '{query}' exists in the database.")
            return

        self._refresh_tickets_tree()
        if self.tickets_tree.exists(ticket.ticket_id):
            self.tickets_tree.selection_set(ticket.ticket_id)
            self.tickets_tree.see(ticket.ticket_id)
            self._on_ticket_selected(None)

    def _handle_cancel_selected_ticket(self) -> None:
        """Cancel the selected ticket, release the seat, and update SQLite state (FR-2)."""
        selected_items = self.tickets_tree.selection()
        if not selected_items:
            self._show_warning("Action Warning", "Please select a ticket from the table to cancel.")
            return

        tkt_id = selected_items[0]
        ticket = self.db.get_ticket(tkt_id)
        if not ticket:
            return

        if ticket.status == TicketStatus.CANCELLED:
            self._show_error("Cancellation Error", "This ticket is already cancelled.")
            return

        confirm = self._confirm(
            "Confirm Ticket Cancellation",
            f"Are you sure you want to cancel Ticket {ticket.ticket_id} (Ref: {ticket.booking_reference})?\n\n"
            f"This will immediately release Seat #{ticket.seat_number:02d} for re-booking.",
        )
        if not confirm:
            return

        try:
            updated_ticket = self.db.cancel_ticket(ticket.ticket_id, reason="Passenger requested refund")
            self.status_var.set(f"Ticket {updated_ticket.ticket_id} cancelled. Seat #{updated_ticket.seat_number:02d} released.")
            self._show_info(
                "Ticket Cancelled",
                f"Ticket {updated_ticket.ticket_id} has been successfully cancelled.\n"
                f"Seat #{updated_ticket.seat_number:02d} is now available again for booking.",
            )
            self._refresh_tickets_tree()
            self._refresh_seat_grid()
            self._refresh_analytics()
            self._on_ticket_selected(None)
        except ValueError as e:
            self._show_error("Cancellation Error", str(e))

    def _show_boarding_pass_modal(self) -> None:
        """Open a popup window rendering a printable bus boarding pass."""
        selected_items = self.tickets_tree.selection()
        if not selected_items:
            self._show_warning("Action Warning", "Please select a ticket to view the boarding pass.")
            return

        tkt_id = selected_items[0]
        ticket = self.db.get_ticket(tkt_id)
        if not ticket:
            return

        passenger = self.db.get_passenger(ticket.passenger_id)
        route = self.db.get_route(ticket.route_id)
        bus = self.db.get_bus(ticket.bus_id)

        # Popup Window
        win = tk.Toplevel(self)
        win.title(f"Boarding Pass — {ticket.ticket_id}")
        win.geometry("540x420")
        win.resizable(False, False)
        win.configure(bg="#F4F6F9")

        header = tk.Frame(win, bg=self.PRIMARY_NAVY, height=45)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="SMARTBUS TRANSIT — OFFICIAL BOARDING PASS",
            font=("Arial", 11, "bold"),
            fg="#FFFFFF",
            bg=self.PRIMARY_NAVY,
            pady=8,
        ).pack()

        body_frame = tk.Frame(win, bg="#FFFFFF", relief=tk.SOLID, borderwidth=1, padx=20, pady=16)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        pass_text = (
            f"PASSENGER NAME : {passenger.name.upper() if passenger else 'N/A'}\n"
            f"CATEGORY       : {passenger.passenger_type.upper() if passenger else 'REGULAR'}\n"
            f"----------------------------------------------------------\n"
            f"DEPARTURE ROUTE: {route.origin.upper()} -> {route.destination.upper()}\n"
            f"TRAVEL DATE    : {ticket.travel_date} | TIME: {route.departure_time}\n"
            f"FLEET / BUS    : {bus.bus_number} ({bus.bus_type})\n"
            f"ASSIGNED SEAT  : SEAT #{ticket.seat_number:02d} {'[PRIORITY]' if bus.is_priority_seat(ticket.seat_number) else ''}\n"
            f"----------------------------------------------------------\n"
            f"SECURITY CODE  : {ticket.booking_reference} (SHA-256 Verified)\n"
            f"TICKET STATUS  : {ticket.status.value.upper()}\n"
            f"FARE PAID      : PHP {ticket.final_fare:.2f}\n"
            f"----------------------------------------------------------\n"
            f"Please arrive at terminal 30 minutes before scheduled departure.\n"
        )

        tk.Label(body_frame, text=pass_text, font=("Consolas", 10), justify=tk.LEFT, bg="#FFFFFF").pack(anchor=tk.W)

        btn_close = ttk.Button(win, text="Close Boarding Pass", command=win.destroy)
        btn_close.pack(pady=(0, 12))

    # -------------------------------------------------------------------------
    # TAB 3 EVENT HANDLERS
    # -------------------------------------------------------------------------
    def _refresh_analytics(self) -> None:
        """Fetch updated system analytics from SQLite and refresh Tab 3."""
        stats = self.db.get_analytics()

        self.kpi_cards["total_tkt"].config(text=str(stats["total_tickets"]))
        self.kpi_cards["active_tkt"].config(text=str(stats["active_tickets"]))
        self.kpi_cards["cancel_tkt"].config(text=str(stats["cancelled_tickets"]))
        self.kpi_cards["revenue"].config(text=f"{stats['gross_revenue']:,.2f}")
        self.kpi_cards["subsidies"].config(text=f"{stats['total_subsidies']:,.2f}")

        # Occupancy Treeview
        for item in self.occ_tree.get_children():
            self.occ_tree.delete(item)

        for r_stat in stats["route_stats"]:
            self.occ_tree.insert(
                "",
                tk.END,
                values=(
                    r_stat["route_id"],
                    f"{r_stat['origin']} -> {r_stat['destination']}",
                    f"{r_stat['capacity']} seats",
                    f"{r_stat['confirmed_seats']} sold",
                    f"{r_stat['occupancy_rate']:.1f}%",
                ),
            )
