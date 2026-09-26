"""
Generates standard, generic flowchart and wireframe diagrams with classic shapes:
- Terminators (Ovals/Rounded capsules): Start / End
- Processes (Rectangles): System operations and calculations
- Decisions (Diamonds/Rhombuses): Branching logic (Yes/No)
- Data I/O (Parallelograms): User inputs and screen displays
- Database (Cylinders): SQLite queries and persistence
- Connectors (Directed arrows with conditional labels)
- Wireframes: Clean UI component schematics with buttons, inputs, tabs, and tables.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path


def draw_capsule(ax, x, y, w, h, text, bg="#4A90E2", fg="#FFFFFF", fontsize=9, bold=True):
    """Draw a terminator oval/capsule."""
    box = patches.FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.08,rounding_size=0.35",
        ec="#1F4E79",
        fc=bg,
        lw=2,
        zorder=3,
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", color=fg, fontsize=fontsize, weight=weight, zorder=4)


def draw_process(ax, x, y, w, h, text, bg="#E8F4F8", fg="#1F4E79", fontsize=8.5, bold=False):
    """Draw a process rectangle."""
    box = patches.FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        ec="#2E75B6",
        fc=bg,
        lw=1.8,
        zorder=3,
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", color=fg, fontsize=fontsize, weight=weight, multialignment="center", zorder=4)


def draw_diamond(ax, x, y, w, h, text, bg="#FEF3C7", fg="#92400E", fontsize=8, bold=True):
    """Draw a decision diamond."""
    pts = [
        [x, y + h / 2],      # Top
        [x + w / 2, y],      # Right
        [x, y - h / 2],      # Bottom
        [x - w / 2, y],      # Left
    ]
    poly = patches.Polygon(pts, closed=True, ec="#D97706", fc=bg, lw=1.8, zorder=3)
    ax.add_patch(poly)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", color=fg, fontsize=fontsize, weight=weight, multialignment="center", zorder=4)


def draw_parallelogram(ax, x, y, w, h, text, bg="#E0F2FE", fg="#0369A1", fontsize=8.5, bold=False):
    """Draw an input/output parallelogram."""
    offset = w * 0.14
    pts = [
        [x - w / 2 + offset, y + h / 2],
        [x + w / 2, y + h / 2],
        [x + w / 2 - offset, y - h / 2],
        [x - w / 2, y - h / 2],
    ]
    poly = patches.Polygon(pts, closed=True, ec="#0284C7", fc=bg, lw=1.8, zorder=3)
    ax.add_patch(poly)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", color=fg, fontsize=fontsize, weight=weight, multialignment="center", zorder=4)


def draw_database(ax, x, y, w, h, text, bg="#ECFDF5", fg="#065F46", fontsize=8, bold=False):
    """Draw a database cylinder storage shape."""
    box = patches.FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        ec="#059669",
        fc=bg,
        lw=1.8,
        zorder=3,
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", color=fg, fontsize=fontsize, weight=weight, multialignment="center", zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, label=None, label_pos=(0.5, 0.5), color="#334155", lw=1.8):
    """Draw a connection arrow with optional text label."""
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->,head_width=0.35,head_length=0.45",
            color=color,
            lw=lw,
            shrinkA=2,
            shrinkB=2,
        ),
        zorder=2,
    )
    if label:
        lx = x1 + (x2 - x1) * label_pos[0]
        ly = y1 + (y2 - y1) * label_pos[1]
        ax.text(
            lx,
            ly,
            label,
            ha="center",
            va="center",
            fontsize=8,
            weight="bold",
            color=color,
            bbox=dict(boxstyle="square,pad=0.15", fc="#FFFFFF", ec="none", alpha=0.85),
            zorder=5,
        )


def draw_bent_arrow(ax, points, label=None, label_idx=0, color="#334155", lw=1.8):
    """Draw an arrow through multiple orthogonal points."""
    for i in range(len(points) - 2):
        p1 = points[i]
        p2 = points[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, zorder=2)

    p_penult = points[-2]
    p_last = points[-1]
    ax.annotate(
        "",
        xy=p_last,
        xytext=p_penult,
        arrowprops=dict(
            arrowstyle="->,head_width=0.35,head_length=0.45",
            color=color,
            lw=lw,
            shrinkA=0,
            shrinkB=2,
        ),
        zorder=2,
    )
    if label:
        p_a = points[label_idx]
        p_b = points[label_idx + 1]
        lx = (p_a[0] + p_b[0]) / 2
        ly = (p_a[1] + p_b[1]) / 2
        ax.text(
            lx,
            ly,
            label,
            ha="center",
            va="center",
            fontsize=8,
            weight="bold",
            color=color,
            bbox=dict(boxstyle="square,pad=0.15", fc="#FFFFFF", ec="none", alpha=0.85),
            zorder=5,
        )


# =============================================================================
# 1. BOOKING PROCESS FLOWCHART (GENERIC STANDARD SHAPES)
# =============================================================================
def generate_booking_flowchart(filepath):
    fig, ax = plt.subplots(figsize=(11, 16), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 16)
    ax.axis("off")

    # Title & Legend Box
    ax.text(5.5, 15.6, "FUNCTIONAL FLOWCHART: TICKET BOOKING & PRIORITY SEAT PROCESS", ha="center", va="center", fontsize=12, weight="bold", color="#1F4E79")
    ax.text(5.5, 15.3, "Standard Flowchart Representation • ISO / ANSI Shapes • FR-1, NFR-1, NFR-2 & Unique Use Case", ha="center", va="center", fontsize=8.5, style="italic", color="#64748B")

    # Legend banner
    legend_y = 14.8
    draw_capsule(ax, 1.2, legend_y, 1.4, 0.4, "Terminator", bg="#4A90E2", fg="#FFFFFF", fontsize=7.5)
    draw_process(ax, 3.2, legend_y, 1.4, 0.4, "Process", bg="#E8F4F8", fg="#1F4E79", fontsize=7.5)
    draw_diamond(ax, 5.2, legend_y, 1.4, 0.45, "Decision", bg="#FEF3C7", fg="#92400E", fontsize=7.5)
    draw_parallelogram(ax, 7.2, legend_y, 1.4, 0.4, "Data I/O", bg="#E0F2FE", fg="#0369A1", fontsize=7.5)
    draw_database(ax, 9.2, legend_y, 1.4, 0.4, "SQLite DB", bg="#ECFDF5", fg="#065F46", fontsize=7.5)

    # 1. Start
    draw_capsule(ax, 5.5, 14.0, 2.2, 0.55, "START", bg="#10B981", fg="#FFFFFF", fontsize=9.5)
    draw_arrow(ax, 5.5, 13.72, 5.5, 13.2)

    # 2. Input Route & Date
    draw_parallelogram(ax, 5.5, 12.9, 3.6, 0.6, "INPUT: Select Route (RT-101)\n& Travel Date (YYYY-MM-DD)", fontsize=8)
    draw_arrow(ax, 5.5, 12.6, 5.5, 12.0)

    # 3. Query DB
    draw_database(ax, 5.5, 11.7, 4.0, 0.6, "QUERY SQLite: Fetch Confirmed\nOccupied Seats for Trip", fontsize=8)
    draw_arrow(ax, 5.5, 11.4, 5.5, 10.8)

    # 4. Render Grid
    draw_process(ax, 5.5, 10.5, 4.2, 0.6, "PROCESS: Render 2x2 Cabin Seat Matrix\n(Green: Avail, Amber: Prio, Red: Taken)", fontsize=8)
    draw_arrow(ax, 5.5, 10.2, 5.5, 9.6)

    # 5. User Selects Seat
    draw_parallelogram(ax, 5.5, 9.3, 3.6, 0.6, "USER ACTION: Click Desired Seat\n(Seat #01 to #24)", fontsize=8)
    draw_arrow(ax, 5.5, 9.0, 5.5, 8.4)

    # 6. Decision: Seat Occupied?
    draw_diamond(ax, 5.5, 8.0, 2.8, 0.8, "Is Seat Already\nOccupied [Red]?", fontsize=7.5)
    # Yes -> loop back
    draw_bent_arrow(ax, [(6.9, 8.0), (9.2, 8.0), (9.2, 9.3), (7.3, 9.3)], label="YES (Occupied)", label_idx=0, color="#DC2626")
    draw_arrow(ax, 5.5, 7.6, 5.5, 6.9, label="NO (Available)", label_pos=(0.5, 0.5), color="#059669")

    # 7. Decision: Priority Seat?
    draw_diamond(ax, 5.5, 6.4, 3.0, 0.85, "Is Selected Seat in\nPriority Row 1 (#1-4)?", fontsize=7.5)
    # Yes -> Check eligibility prompt
    draw_bent_arrow(ax, [(4.0, 6.4), (2.0, 6.4), (2.0, 5.5)], label="YES (Priority)", label_idx=0, color="#D97706")
    draw_process(ax, 2.0, 5.1, 2.8, 0.7, "VERIFY: Prompt Priority Policy\n(Senior / PWD / Pregnant)", fontsize=7.5)
    draw_bent_arrow(ax, [(2.0, 4.75), (2.0, 4.2), (3.8, 4.2)], color="#334155")
    # No -> direct to passenger input
    draw_arrow(ax, 5.5, 5.97, 5.5, 4.6, label="NO (Regular)", label_pos=(0.5, 0.5), color="#334155")

    # 8. Input Passenger Details
    draw_parallelogram(ax, 5.5, 4.2, 3.6, 0.7, "INPUT: Passenger Name,\nMobile Phone, Category", fontsize=8)
    draw_arrow(ax, 5.5, 3.85, 5.5, 3.25)

    # 9. Decision: Concession Eligible?
    draw_diamond(ax, 5.5, 2.8, 3.0, 0.8, "Concession Eligible?\n(Senior/PWD/Student)", fontsize=7.5)
    # Yes -> Apply 20%
    draw_bent_arrow(ax, [(7.0, 2.8), (8.8, 2.8), (8.8, 1.9)], label="YES", label_idx=0, color="#059669")
    draw_process(ax, 8.8, 1.5, 3.0, 0.7, "PROCESS: Require Valid ID\n& Deduct 20% Concession Fare\n(Final = Base * 0.80)", fontsize=7.5)
    # No -> Regular fare
    draw_arrow(ax, 5.5, 2.4, 5.5, 1.85, label="NO", label_pos=(0.5, 0.5), color="#334155")
    draw_process(ax, 5.5, 1.5, 2.6, 0.6, "PROCESS: Apply 100%\nStandard Base Fare", fontsize=7.5)

    draw_bent_arrow(ax, [(8.8, 1.15), (8.8, 0.7), (6.8, 0.7)], color="#334155")
    draw_arrow(ax, 5.5, 1.2, 5.5, 0.7)

    # Connection node to page 2 / bottom
    draw_capsule(ax, 5.5, 0.45, 2.0, 0.45, "TO ATOMIC WRITE (A)", bg="#6366F1", fg="#FFFFFF", fontsize=8)

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


# =============================================================================
# 2. ATOMIC TRANSACTION & CANCELLATION FLOWCHART
# =============================================================================
def generate_cancellation_flowchart(filepath):
    fig, ax = plt.subplots(figsize=(11, 16), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 16)
    ax.axis("off")

    ax.text(5.5, 15.6, "FUNCTIONAL FLOWCHART: ATOMIC COMMIT & TICKET CANCELLATION", ha="center", va="center", fontsize=12, weight="bold", color="#1F4E79")
    ax.text(5.5, 15.3, "Double-Booking Prevention (NFR-2) & Ticket Lifecycle Seat Restoration (FR-2)", ha="center", va="center", fontsize=8.5, style="italic", color="#64748B")

    # Section 1: Atomic Booking Commit
    ax.text(1.0, 14.8, "[ SECTION A: ATOMIC SQLITE COMMIT & VERIFICATION ]", fontsize=9, weight="bold", color="#1E3A8A")

    draw_capsule(ax, 5.5, 14.2, 2.2, 0.5, "FROM STAGE A", bg="#6366F1", fg="#FFFFFF", fontsize=8.5)
    draw_arrow(ax, 5.5, 13.95, 5.5, 13.4)

    draw_process(ax, 5.5, 13.0, 4.4, 0.7, "PROCESS: Generate Cryptographic\nSalted SHA-256 Code ('BTK-XXXXXX')\n& Validate Phone Regex (NFR-1)", fontsize=8)
    draw_arrow(ax, 5.5, 12.65, 5.5, 12.0)

    draw_database(ax, 5.5, 11.6, 4.6, 0.7, "SQLITE TRANSACTION:\nINSERT INTO tickets & passengers\n(Partial Unique Index on active seat)", fontsize=8)
    draw_arrow(ax, 5.5, 11.25, 5.5, 10.6)

    draw_diamond(ax, 5.5, 10.1, 3.2, 0.9, "Constraint Violation /\nDouble-Booking Conflict?", fontsize=7.5)
    # Yes -> Rollback
    draw_bent_arrow(ax, [(7.1, 10.1), (9.0, 10.1), (9.0, 9.2)], label="YES (Conflict)", label_idx=0, color="#DC2626")
    draw_process(ax, 9.0, 8.8, 2.6, 0.65, "ROLLBACK & ALERT:\nSeat Collision Caught!\nZero Data Corruption", fontsize=7.5, bg="#FEE2E2", fg="#991B1B")
    # No -> Commit
    draw_arrow(ax, 5.5, 9.65, 5.5, 8.9, label="NO (Clean Write)", label_pos=(0.5, 0.5), color="#059669")
    draw_process(ax, 5.5, 8.5, 4.0, 0.65, "COMMIT TRANSACTION:\nMark Seat Occupied [X],\nUpdate Fleet Occupancy KPI", fontsize=8)
    draw_arrow(ax, 5.5, 8.17, 5.5, 7.55)

    draw_parallelogram(ax, 5.5, 7.2, 3.6, 0.6, "OUTPUT: Issue Verified Boarding Pass\n& Print Official Reference Code", fontsize=8)
    draw_arrow(ax, 5.5, 6.9, 5.5, 6.3)
    draw_capsule(ax, 5.5, 6.05, 2.0, 0.45, "BOOKING END", bg="#10B981", fg="#FFFFFF", fontsize=9)

    # Dividing separator
    ax.plot([0.8, 10.2], [5.5, 5.5], color="#CBD5E1", lw=1.5, ls="--")

    # Section 2: Cancellation & Seat Release
    ax.text(1.0, 5.2, "[ SECTION B: TICKET CANCELLATION & SEAT RESTORATION (FR-2) ]", fontsize=9, weight="bold", color="#1E3A8A")

    draw_capsule(ax, 5.5, 4.6, 2.2, 0.45, "START CANCELLATION", bg="#EF4444", fg="#FFFFFF", fontsize=8.5)
    draw_arrow(ax, 5.5, 4.37, 5.5, 3.8)

    draw_parallelogram(ax, 5.5, 3.5, 3.8, 0.55, "INPUT: Search Ticket ID (TKT-XXXX)\nor Booking Ref ('BTK-XXXXXX')", fontsize=8)
    draw_arrow(ax, 5.5, 3.22, 5.5, 2.65)

    draw_diamond(ax, 5.5, 2.2, 3.0, 0.8, "Record Exists &\nStatus = 'Confirmed'?", fontsize=7.5)
    draw_bent_arrow(ax, [(7.0, 2.2), (8.8, 2.2), (8.8, 1.4)], label="NO", label_idx=0, color="#DC2626")
    draw_process(ax, 8.8, 1.05, 2.4, 0.55, "DISPLAY ERROR:\nInvalid / Cancelled", fontsize=7.5, bg="#FEE2E2", fg="#991B1B")

    draw_arrow(ax, 5.5, 1.8, 5.5, 1.3, label="YES", label_pos=(0.5, 0.5), color="#059669")
    draw_database(ax, 5.5, 0.95, 4.2, 0.6, "UPDATE SQLite:\nSET status='Cancelled', cancel_time=NOW()\n(Seat Instantly Released to Fleet)", fontsize=7.5)
    draw_arrow(ax, 5.5, 0.65, 5.5, 0.25)
    draw_capsule(ax, 5.5, 0.15, 2.0, 0.35, "CANCELLATION END", bg="#10B981", fg="#FFFFFF", fontsize=8)

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


# =============================================================================
# 3. SYSTEM ARCHITECTURE & DATA FLOW DIAGRAM
# =============================================================================
def generate_architecture_diagram(filepath):
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    ax.text(5.5, 8.1, "SYSTEM ARCHITECTURE & RELATIONAL DATA FLOW", ha="center", va="center", fontsize=12, weight="bold", color="#1F4E79")
    ax.text(5.5, 7.8, "Layered MVC & Repository Pattern with SQLite Persistence", ha="center", va="center", fontsize=8.5, style="italic", color="#64748B")

    # Layer 1: Presentation Tier
    p1 = patches.Rectangle((0.8, 5.6), 9.4, 1.8, ec="#1F4E79", fc="#EFF6FF", lw=1.8)
    ax.add_patch(p1)
    ax.text(1.1, 7.15, "1. PRESENTATION LAYER (Tkinter Desktop GUI — app.py)", fontsize=9, weight="bold", color="#1F4E79")
    draw_process(ax, 2.5, 6.3, 2.8, 0.8, "Tab 1: Booking Engine\n- 2x2 Interactive Seat Grid\n- Route / Date Comboboxes", fontsize=7.5, bg="#FFFFFF")
    draw_process(ax, 5.5, 6.3, 2.8, 0.8, "Tab 2: Ticket Management\n- Ref Code Search Bar\n- Refund / Cancellation Action", fontsize=7.5, bg="#FFFFFF")
    draw_process(ax, 8.5, 6.3, 2.8, 0.8, "Tab 3: Fleet Analytics\n- Gross Revenue KPI Cards\n- Route Occupancy Table", fontsize=7.5, bg="#FFFFFF")

    draw_arrow(ax, 5.5, 5.6, 5.5, 4.8, label="GUI User Events & Form Data", label_pos=(0.5, 0.5), color="#1F4E79", lw=2)

    # Layer 2: Business Logic / Factory Tier
    p2 = patches.Rectangle((0.8, 3.1), 9.4, 1.7, ec="#2E75B6", fc="#F0FDF4", lw=1.8)
    ax.add_patch(p2)
    ax.text(1.1, 4.55, "2. BUSINESS LOGIC & FACTORY LAYER (models/)", fontsize=9, weight="bold", color="#166534")
    draw_process(ax, 2.4, 3.8, 2.6, 0.8, "Domain Models (OOP):\n- Route, Bus, Passenger\n- Encapsulated @property setters", fontsize=7.5, bg="#FFFFFF", fg="#166534")
    draw_process(ax, 5.5, 3.8, 3.0, 0.8, "TicketFactory & BusFactory:\n- 20% Concession Deduction\n- Priority Seating Policy Check", fontsize=7.5, bg="#FFFFFF", fg="#166534")
    draw_process(ax, 8.6, 3.8, 2.6, 0.8, "Security Validation:\n- Phone Number Regex\n- SHA-256 Tamper-Proof Ref", fontsize=7.5, bg="#FFFFFF", fg="#166534")

    draw_arrow(ax, 5.5, 3.1, 5.5, 2.3, label="Validated Domain Objects", label_pos=(0.5, 0.5), color="#166534", lw=2)

    # Layer 3: Persistence & Database Tier
    p3 = patches.Rectangle((0.8, 0.6), 9.4, 1.7, ec="#059669", fc="#F8FAFC", lw=1.8)
    ax.add_patch(p3)
    ax.text(1.1, 2.05, "3. DATA ACCESS LAYER & SQLITE PERSISTENCE ENGINE (models/database.py)", fontsize=9, weight="bold", color="#0F766E")
    draw_database(ax, 2.8, 1.3, 3.4, 0.8, "BusTicketingDatabase (Singleton):\n- @contextmanager connection handling\n- Thread-safe parameterized queries", fontsize=7.5, bg="#FFFFFF")
    draw_database(ax, 7.5, 1.3, 5.2, 0.8, "SQLite Relational Tables ('bus_ticketing.db'):\n- routes, buses, passengers, tickets\n- UNIQUE INDEX on active seats (Prevents Double-Booking)", fontsize=7.5, bg="#FFFFFF")

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


# =============================================================================
# 4. TAB 1 WIREFRAME: BOOK TICKETS & SEAT MAP
# =============================================================================
def generate_wireframe_tab1(filepath):
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Main Window Outline
    win = patches.FancyBboxPatch((0.5, 0.4), 10.0, 6.7, boxstyle="round,pad=0.08,rounding_size=0.15", ec="#1F4E79", fc="#F8FAFC", lw=2.5)
    ax.add_patch(win)

    # Title Bar
    title_bar = patches.Rectangle((0.5, 6.6), 10.0, 0.5, ec="#1F4E79", fc="#1F4E79")
    ax.add_patch(title_bar)
    ax.text(0.7, 6.85, "SmartBus Transit System — Desktop Booking Interface (Lab Practical)", color="#FFFFFF", weight="bold", fontsize=9.5)
    ax.text(9.8, 6.85, "[ - □ ✕ ]", color="#FFFFFF", weight="bold", fontsize=8.5, ha="right")

    # Tab Strip
    t1 = patches.Rectangle((0.7, 6.15), 3.2, 0.45, ec="#1F4E79", fc="#FFFFFF", lw=1.5)
    t2 = patches.Rectangle((3.9, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    t3 = patches.Rectangle((7.1, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    ax.add_patch(t1); ax.add_patch(t2); ax.add_patch(t3)
    ax.text(2.3, 6.38, "1. Book Tickets & Visual Seat Map", color="#1F4E79", weight="bold", fontsize=8.5, ha="center")
    ax.text(5.5, 6.38, "2. Manage Bookings", color="#64748B", fontsize=8, ha="center")
    ax.text(8.7, 6.38, "3. System Analytics", color="#64748B", fontsize=8, ha="center")

    # 3-Column Panels
    # Left Panel: Trip Selector
    p_left = patches.Rectangle((0.7, 0.9), 2.8, 5.1, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(p_left)
    ax.text(0.9, 5.75, "1. Select Route & Trip", weight="bold", color="#1F4E79", fontsize=8.5)
    ax.text(0.9, 5.4, "Route: [ RT-101: Manila -> Baguio  ▼ ]", fontsize=7.5, family="monospace")
    ax.text(0.9, 4.9, "Travel Date: [ 2026-09-28 ]", fontsize=7.5, family="monospace")
    btn_update = patches.Rectangle((0.9, 4.3), 2.4, 0.35, ec="#2E75B6", fc="#EBF8FF", lw=1)
    ax.add_patch(btn_update)
    ax.text(2.1, 4.47, "[ Update Seat Grid ]", ha="center", va="center", fontsize=7.5, weight="bold", color="#2E75B6")

    # Route Itinerary Box
    itinerary_box = patches.Rectangle((0.9, 1.2), 2.4, 2.9, ec="#E2E8F0", fc="#F8FAFC", lw=1)
    ax.add_patch(itinerary_box)
    itinerary_text = (
        "=== ROUTE ITINERARY ===\n"
        "Origin   : Manila (Cubao)\n"
        "Dest.    : Baguio City\n"
        "Distance : 245.0 km\n"
        "Departs  : 08:00 AM\n"
        "Base Fare: PHP 580.00\n\n"
        "=== FLEET BUS ===\n"
        "Plate    : DLTB-8012\n"
        "Class    : Standard AC\n"
        "Capacity : 24 Seats\n"
        "Priority : Row 1 (#1-4)"
    )
    ax.text(1.0, 3.9, itinerary_text, fontsize=7, family="monospace", va="top")

    # Center Panel: Visual 2x2 Cabin Seat Matrix
    p_mid = patches.Rectangle((3.7, 0.9), 3.6, 5.1, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(p_mid)
    ax.text(3.9, 5.75, "2. Interactive 2x2 Seat Matrix", weight="bold", color="#1F4E79", fontsize=8.5)

    # Legend
    ax.plot([3.9, 7.1], [5.55, 5.55], color="#E2E8F0", lw=1)
    for idx, (col, lbl) in enumerate([("#2E7D32", "Avail"), ("#E65100", "Priority"), ("#1565C0", "Selected"), ("#C62828", "Taken")]):
        bx = 3.9 + idx * 0.8
        ax.add_patch(patches.Rectangle((bx, 5.3), 0.15, 0.15, fc=col, ec="none"))
        ax.text(bx + 0.2, 5.38, lbl, fontsize=6.5, va="center")

    # Bus Cabin Frame
    cabin = patches.Rectangle((4.0, 1.2), 3.0, 3.9, ec="#94A3B8", fc="#F1F5F9", lw=1.5)
    ax.add_patch(cabin)
    # Driver Cab
    ax.add_patch(patches.Rectangle((4.1, 4.7), 2.8, 0.3, ec="#94A3B8", fc="#CBD5E1"))
    ax.text(5.5, 4.85, "[ DRIVER CAB / FRONT ]", ha="center", va="center", fontsize=7, weight="bold", color="#475569")

    # 6 Rows of 2x2 Seats
    seat_num = 1
    for r in range(6):
        sy = 4.3 - r * 0.52
        ax.text(4.2, sy + 0.15, f"R{r+1}", fontsize=6.5, weight="bold", color="#64748B")
        for c in range(4):
            sx = 4.5 + (c * 0.45) + (0.35 if c >= 2 else 0.0) # Aisle gap
            # Color code
            if seat_num in (1, 2, 4):
                s_col = "#E65100" # Priority
                s_txt = f"{seat_num:02d}\n[P]"
            elif seat_num == 3:
                s_col = "#1565C0" # Selected
                s_txt = f"{seat_num:02d}\n[✓]"
            elif seat_num in (7, 12, 19):
                s_col = "#C62828" # Taken
                s_txt = f"{seat_num:02d}\n[X]"
            else:
                s_col = "#2E7D32" # Available regular
                s_txt = f"{seat_num:02d}"

            ax.add_patch(patches.FancyBboxPatch((sx, sy), 0.38, 0.38, boxstyle="round,pad=0.02,rounding_size=0.06", fc=s_col, ec="#1E293B", lw=1))
            ax.text(sx + 0.19, sy + 0.19, s_txt, ha="center", va="center", color="#FFFFFF", fontsize=5.5, weight="bold")
            seat_num += 1

    # Right Panel: Passenger & Concession Booking
    p_right = patches.Rectangle((7.5, 0.9), 2.8, 5.1, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(p_right)
    ax.text(7.7, 5.75, "3. Passenger & Concession", weight="bold", color="#1F4E79", fontsize=8.5)

    ax.text(7.7, 5.35, "Full Name:\n[ Maria Santos                 ]", fontsize=7, family="monospace")
    ax.text(7.7, 4.75, "Contact Number:\n[ 09171234567                  ]", fontsize=7, family="monospace")
    ax.text(7.7, 4.15, "Category:\n[ Senior Citizen (20% Off)   ▼ ]", fontsize=7, family="monospace")
    ax.text(7.7, 3.55, "Concession / OSCA ID:\n[ OSCA-77491                   ]", fontsize=7, family="monospace")

    # Fare box
    fare_b = patches.Rectangle((7.7, 2.0), 2.4, 1.3, ec="#93C5FD", fc="#EFF6FF", lw=1)
    ax.add_patch(fare_b)
    ax.text(7.85, 3.05, "Base Fare : PHP 580.00", fontsize=7, family="monospace")
    ax.text(7.85, 2.75, "Discount  : -PHP 116.00 (20%)", fontsize=7, family="monospace", color="#16A34A", weight="bold")
    ax.text(7.85, 2.35, "Total Due : PHP 464.00", fontsize=8, family="monospace", color="#1F4E79", weight="bold")

    btn_book = patches.Rectangle((7.7, 1.2), 2.4, 0.55, ec="#1F4E79", fc="#1F4E79", lw=1.5)
    ax.add_patch(btn_book)
    ax.text(8.9, 1.47, "[ Confirm & Issue Ticket ]", color="#FFFFFF", weight="bold", fontsize=8, ha="center")

    # Status Bar
    ax.add_patch(patches.Rectangle((0.5, 0.4), 10.0, 0.35, ec="#CBD5E1", fc="#E2E8F0"))
    ax.text(0.7, 0.57, "System Ready • Connected to SQLite 'bus_ticketing.db' • ACID Transactions Enabled", fontsize=7, color="#334155")

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


# =============================================================================
# 5. TAB 2 WIREFRAME: MANAGE BOOKINGS & BOARDING PASS
# =============================================================================
def generate_wireframe_tab2(filepath):
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    win = patches.FancyBboxPatch((0.5, 0.4), 10.0, 6.7, boxstyle="round,pad=0.08,rounding_size=0.15", ec="#1F4E79", fc="#F8FAFC", lw=2.5)
    ax.add_patch(win)

    # Title Bar
    title_bar = patches.Rectangle((0.5, 6.6), 10.0, 0.5, ec="#1F4E79", fc="#1F4E79")
    ax.add_patch(title_bar)
    ax.text(0.7, 6.85, "SmartBus Transit System — Ticket Lifecycle Management & Verification", color="#FFFFFF", weight="bold", fontsize=9.5)
    ax.text(9.8, 6.85, "[ - □ ✕ ]", color="#FFFFFF", weight="bold", fontsize=8.5, ha="right")

    # Tab Strip
    t1 = patches.Rectangle((0.7, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    t2 = patches.Rectangle((3.9, 6.15), 3.2, 0.45, ec="#1F4E79", fc="#FFFFFF", lw=1.5)
    t3 = patches.Rectangle((7.1, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    ax.add_patch(t1); ax.add_patch(t2); ax.add_patch(t3)
    ax.text(2.3, 6.38, "1. Book Tickets & Seat Map", color="#64748B", fontsize=8, ha="center")
    ax.text(5.5, 6.38, "2. Manage Bookings & Cancellations", color="#1F4E79", weight="bold", fontsize=8.5, ha="center")
    ax.text(8.7, 6.38, "3. System Analytics", color="#64748B", fontsize=8, ha="center")

    # Search Bar
    ax.text(0.8, 5.75, "Search: [ TKT-1001 or BTK-XXXXXX   ]  [ Find Ticket ]  [ Reset View ]   Filter: [ All Statuses ▼ ]", fontsize=7.5, family="monospace")

    # Active Ticket Dossier Card
    dossier = patches.Rectangle((0.7, 3.8), 9.6, 1.7, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(dossier)
    ax.text(0.9, 5.25, "Active Ticket Dossier & SHA-256 Tamper-Proof Audit (NFR-1)", weight="bold", color="#1F4E79", fontsize=8.5)

    d_text = (
        "Ticket ID       : TKT-1001             Status      : [CONFIRMED]            Assigned Bus: DLTB-8012 (Standard AC)\n"
        "Security Ref    : BTK-8F3A29 (SHA-256) Route       : Manila -> Baguio       Assigned Seat: Seat #01 [PRIORITY ROW]\n"
        "Passenger Name  : Maria Santos         Travel Date : 2026-09-28 08:00 AM    Fare Paid    : PHP 464.00 (20% Off)\n"
        "Classification  : Senior Citizen       Concession ID: OSCA-77491             Contact No.  : 09171234567"
    )
    ax.text(0.9, 5.0, d_text, fontsize=7, family="monospace", va="top")

    btn_cancel = patches.Rectangle((8.1, 4.4), 2.0, 0.4, ec="#DC2626", fc="#FEE2E2", lw=1.2)
    ax.add_patch(btn_cancel)
    ax.text(9.1, 4.6, "[ Cancel & Refund ]", color="#B91C1C", weight="bold", fontsize=7.5, ha="center")

    btn_pass = patches.Rectangle((8.1, 3.9), 2.0, 0.4, ec="#2563EB", fc="#EFF6FF", lw=1.2)
    ax.add_patch(btn_pass)
    ax.text(9.1, 4.1, "[ View Boarding Pass ]", color="#1D4ED8", weight="bold", fontsize=7.5, ha="center")

    # Master Table Treeview
    table_box = patches.Rectangle((0.7, 0.9), 9.6, 2.7, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(table_box)
    ax.text(0.9, 3.35, "Master Ticket Ledger & Audit Records", weight="bold", color="#1F4E79", fontsize=8.5)

    # Headers
    headers = ["Ticket ID", "Reference (NFR-1)", "Passenger", "Category", "Route", "Date", "Seat", "Fare", "Status"]
    col_x = [0.8, 1.8, 3.2, 4.5, 5.6, 7.1, 8.0, 8.7, 9.6]
    ax.plot([0.8, 10.1], [3.15, 3.15], color="#1F4E79", lw=1.5)
    for i, h in enumerate(headers):
        ax.text(col_x[i], 3.22, h, weight="bold", fontsize=7, color="#1F4E79")

    # Sample rows
    rows = [
        ("TKT-1001", "BTK-8F3A29", "Maria Santos", "Senior", "Manila->Baguio", "2026-09-28", "#01 [P]", "PHP 464.00", "CONFIRMED"),
        ("TKT-1002", "BTK-4C91E2", "Juan Dela Cruz", "Regular", "Manila->Baguio", "2026-09-28", "#07", "PHP 580.00", "CONFIRMED"),
        ("TKT-1003", "BTK-1D77A0", "Grace Ramos", "PWD", "Manila->Batangas", "2026-09-28", "#02 [P]", "PHP 184.00", "CONFIRMED"),
        ("TKT-1004", "BTK-77BC11", "Mark Bautista", "Student", "Manila->La Union", "2026-09-28", "#05", "PHP 496.00", "CANCELLED"),
    ]
    for idx, r in enumerate(rows):
        ry = 2.9 - idx * 0.4
        for c_idx, val in enumerate(r):
            col = "#15803D" if val == "CONFIRMED" else ("#DC2626" if val == "CANCELLED" else "#334155")
            ax.text(col_x[c_idx], ry, val, fontsize=6.8, family="monospace", color=col)
        ax.plot([0.8, 10.1], [ry - 0.08, ry - 0.08], color="#F1F5F9", lw=0.8)

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


# =============================================================================
# 6. TAB 3 WIREFRAME: FLEET ANALYTICS & AUDIT
# =============================================================================
def generate_wireframe_tab3(filepath):
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    win = patches.FancyBboxPatch((0.5, 0.4), 10.0, 6.7, boxstyle="round,pad=0.08,rounding_size=0.15", ec="#1F4E79", fc="#F8FAFC", lw=2.5)
    ax.add_patch(win)

    # Title Bar
    title_bar = patches.Rectangle((0.5, 6.6), 10.0, 0.5, ec="#1F4E79", fc="#1F4E79")
    ax.add_patch(title_bar)
    ax.text(0.7, 6.85, "SmartBus Transit System — Operational Analytics & Fleet Performance", color="#FFFFFF", weight="bold", fontsize=9.5)
    ax.text(9.8, 6.85, "[ - □ ✕ ]", color="#FFFFFF", weight="bold", fontsize=8.5, ha="right")

    # Tab Strip
    t1 = patches.Rectangle((0.7, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    t2 = patches.Rectangle((3.9, 6.15), 3.2, 0.45, ec="#CBD5E1", fc="#E2E8F0", lw=1)
    t3 = patches.Rectangle((7.1, 6.15), 3.2, 0.45, ec="#1F4E79", fc="#FFFFFF", lw=1.5)
    ax.add_patch(t1); ax.add_patch(t2); ax.add_patch(t3)
    ax.text(2.3, 6.38, "1. Book Tickets & Seat Map", color="#64748B", fontsize=8, ha="center")
    ax.text(5.5, 6.38, "2. Manage Bookings", color="#64748B", fontsize=8, ha="center")
    ax.text(8.7, 6.38, "3. System Overview & Analytics", color="#1F4E79", weight="bold", fontsize=8.5, ha="center")

    # 5 KPI Metric Cards across the top
    kpi_data = [
        ("Total Bookings", "4", "#2563EB"),
        ("Active Confirmed", "3", "#16A34A"),
        ("Cancelled Tickets", "1", "#DC2626"),
        ("Gross Revenue (PHP)", "1,228.00", "#1F4E79"),
        ("Concession Subsidies", "272.00", "#D97706"),
    ]
    for i, (title, val, col) in enumerate(kpi_data):
        cx = 0.7 + i * 1.95
        card = patches.Rectangle((cx, 4.9), 1.8, 1.05, ec="#E2E8F0", fc="#FFFFFF", lw=1.2)
        ax.add_patch(card)
        ax.text(cx + 0.15, 5.7, title, fontsize=6.8, weight="bold", color="#64748B")
        ax.text(cx + 0.15, 5.25, val, fontsize=11, weight="bold", color=col)

    # Route Occupancy Table
    occ_box = patches.Rectangle((0.7, 2.5), 9.6, 2.2, ec="#CBD5E1", fc="#FFFFFF", lw=1.2)
    ax.add_patch(occ_box)
    ax.text(0.9, 4.45, "Fleet Route Popularity & Occupancy Rates", weight="bold", color="#1F4E79", fontsize=8.5)

    headers_occ = ["Route ID", "Origin -> Destination", "Capacity", "Confirmed Sold", "Occupancy Rate (%)"]
    col_x_occ = [0.9, 2.2, 5.6, 7.2, 8.8]
    ax.plot([0.9, 10.1], [4.25, 4.25], color="#1F4E79", lw=1.2)
    for i, h in enumerate(headers_occ):
        ax.text(col_x_occ[i], 4.32, h, weight="bold", fontsize=7.2, color="#1F4E79")

    occ_rows = [
        ("RT-101", "Manila (Cubao) -> Baguio City", "24 seats", "2 sold", "8.3%"),
        ("RT-102", "Manila (Buendia) -> Batangas Port", "24 seats", "1 sold", "4.2%"),
        ("RT-103", "Manila (Cubao) -> Naga City", "24 seats", "0 sold", "0.0%"),
        ("RT-104", "Manila (Pasay) -> La Union (San Juan)", "24 seats", "0 sold", "0.0%"),
    ]
    for idx, r in enumerate(occ_rows):
        ry = 3.95 - idx * 0.38
        for c_idx, val in enumerate(r):
            ax.text(col_x_occ[c_idx], ry, val, fontsize=7, family="monospace", color="#334155")
        ax.plot([0.9, 10.1], [ry - 0.08, ry - 0.08], color="#F1F5F9", lw=0.8)

    # SQLite Technical Verification Pane
    audit_pane = patches.Rectangle((0.7, 0.7), 9.6, 1.6, ec="#CBD5E1", fc="#F8FAFC", lw=1.2)
    ax.add_patch(audit_pane)
    ax.text(0.9, 2.05, "SQLite Persistence & ACID Concurrency Audit Verification", weight="bold", color="#0F766E", fontsize=8.5)

    audit_txt = (
        "• Persistence Status : ONLINE [SQLite Relational File: 'bus_ticketing.db']\n"
        "• ACID Mode          : Immediate Transactions Enabled with Foreign Key PRAGMA Validation\n"
        "• Double-Booking Net : Partial Unique Index: idx_unique_active_seat ON tickets(route_id, travel_date, seat_number) WHERE status='Confirmed'\n"
        "• NFR-1 Security     : Salted SHA-256 Reference Code Generation ('BTK-[HEX]') & Mobile Regex Verification\n"
        "• NFR-2 Quality      : PEP 8 Encapsulation with Private Fields & Property Setters Raising Explicit Exceptions"
    )
    ax.text(0.9, 1.85, audit_txt, fontsize=6.8, family="monospace", color="#1E293B", va="top")

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()
    print(f"Generated: {filepath}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    print("==================================================================")
    print("Generating Generic Standard Flowcharts & Wireframe Diagrams...")
    print("==================================================================")

    # 1. Flowchart 1: Booking & Priority Seat Process
    f1 = os.path.join(out_dir, "flowchart_booking_process.png")
    generate_booking_flowchart(f1)

    # 2. Flowchart 2: Atomic SQLite Commit & Cancellation Process
    f2 = os.path.join(out_dir, "flowchart_cancellation_process.png")
    generate_cancellation_flowchart(f2)

    # 3. Architecture & Data Flow Diagram
    f3 = os.path.join(out_dir, "flowchart_system_architecture.png")
    generate_architecture_diagram(f3)

    # 4. Wireframe Tab 1: Booking & Seat Matrix
    w1 = os.path.join(out_dir, "wireframe_tab1_booking.png")
    generate_wireframe_tab1(w1)

    # 5. Wireframe Tab 2: Manage Bookings
    w2 = os.path.join(out_dir, "wireframe_tab2_management.png")
    generate_wireframe_tab2(w2)

    # 6. Wireframe Tab 3: Fleet Analytics
    w3 = os.path.join(out_dir, "wireframe_tab3_analytics.png")
    generate_wireframe_tab3(w3)

    print("All generic flowchart and wireframe diagrams generated successfully!")
