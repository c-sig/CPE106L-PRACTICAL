"""
Exports the SmartBus Markdown documentation and specifications into a
professional, publication-quality PDF report with embedded flowcharts,
wireframes, and verification matrices using ReportLab.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image as PILImage


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""

    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F4E79"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "SmartBus Transit System — System Specification, Wireframes & Flowcharts")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(576, 762, "CPE106L Practical Assessment")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(36, 756, 576, 756)

        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 24, "Confidential • Laboratory Submission • SQLite ACID Persistence Engine")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 24, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 34, 576, 34)
        self.restoreState()


def get_scaled_image(img_path, max_w=520, max_h=620):
    """Scale image proportionally to fit page boundaries."""
    if not os.path.exists(img_path):
        return None
    with PILImage.open(img_path) as im:
        orig_w, orig_h = im.size
    ratio = min(max_w / orig_w, max_h / orig_h)
    target_w = orig_w * ratio
    target_h = orig_h * ratio
    return Image(img_path, width=target_w, height=target_h)


def generate_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(base_dir, "SmartBus_System_Documentation.pdf")
    readme_pdf = os.path.join(base_dir, "README.pdf")
    screenshots_dir = os.path.join(base_dir, "screenshots")

    print(f"Building PDF at: {output_pdf}")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    NAVY = colors.HexColor("#1F4E79")
    STEEL = colors.HexColor("#2E75B6")
    DARK = colors.HexColor("#1E293B")
    MUTED = colors.HexColor("#475569")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=NAVY,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=STEEL,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=STEEL,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=DARK,
        spaceAfter=5,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=3,
        spaceAfter=5,
    )

    tbl_hdr_style = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0,
    )

    tbl_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=DARK,
        alignment=0,
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER / HEADER BANNER
    # -------------------------------------------------------------------------
    banner_data = [
        [
            Paragraph("<b>SMARTBUS TRANSIT SYSTEM</b>", ParagraphStyle("B1", fontName="Helvetica-Bold", fontSize=15, textColor=colors.white)),
            Paragraph("<b>CPE106L PRACTICAL ASSESSMENT</b><br/>Software Engineering Specification & Architecture", ParagraphStyle("B2", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#D0E1FD"), alignment=2))
        ]
    ]
    t_banner = Table(banner_data, colWidths=[330, 210])
    t_banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 10))

    story.append(Paragraph("System Requirements Specification, Architecture, Wireframes & Process Flowcharts", title_style))
    story.append(Paragraph("<b>Architectural Heritage:</b> Harmonized design patterns from Lab 2, Lab 3, Lab 4, and Lab 5 • <b>Persistence:</b> SQLite3 ACID Engine", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))

    # -------------------------------------------------------------------------
    # SECTION 1: REQUIREMENTS SPECIFICATION
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. System Requirements Specification Matrix", h1_style))
    story.append(Paragraph(
        "In accordance with software engineering principles, the system is designed around balanced "
        "<b>Functional Requirements (FR)</b> and <b>Non-Functional Requirements (NFR)</b>:",
        body_style,
    ))

    req_headers = [Paragraph("<b>Requirement Dimension</b>", tbl_hdr_style), Paragraph("<b>Functional Requirements (FR)</b>", tbl_hdr_style), Paragraph("<b>Non-Functional Requirements (NFR)</b>", tbl_hdr_style)]
    req_rows = [
        [
            Paragraph("<b>Core Definition</b>", tbl_cell_style),
            Paragraph("Define <b>what</b> the system should do (features & system functionality).", tbl_cell_style),
            Paragraph("Define <b>how</b> the system should perform (quality attributes & constraints).", tbl_cell_style),
        ],
        [
            Paragraph("<b>Operational Focus</b>", tbl_cell_style),
            Paragraph("Focus on system behavior, user interaction, and transactional operations.", tbl_cell_style),
            Paragraph("Focus on performance, security, data integrity, and code maintainability.", tbl_cell_style),
        ],
        [
            Paragraph("<b>Scope of Actions</b>", tbl_cell_style),
            Paragraph("Describes specific actions like route querying, seat booking, ticket issuance, and ticket cancellations.", tbl_cell_style),
            Paragraph("Describes constraints like response times (&lt;100ms), input sanitization, and OOP extensibility.", tbl_cell_style),
        ],
        [
            Paragraph("<b>Visibility</b>", tbl_cell_style),
            Paragraph("Directly visible to commuters, ticket agents, and dispatchers.", tbl_cell_style),
            Paragraph("Indirectly visible, governing underlying robustness, security, and architectural reliability.", tbl_cell_style),
        ],
        [
            Paragraph("<b>Validation Metric</b>", tbl_cell_style),
            Paragraph("Easier to measure (output-based validation e.g. ticket record generated, seat reserved).", tbl_cell_style),
            Paragraph("Harder to measure, verified via automated test benchmarks and strict database constraint tests.", tbl_cell_style),
        ],
        [
            Paragraph("<b>Design Driver</b>", tbl_cell_style),
            Paragraph("Drives the core user workflows and interactive GUI features.", tbl_cell_style),
            Paragraph("Influences database schema indexing (ACID SQLite), factory patterns, and class encapsulation.", tbl_cell_style),
        ],
        [
            Paragraph("<b>Documentation Format</b>", tbl_cell_style),
            Paragraph("Documented using use cases, user stories, and operational flowcharts.", tbl_cell_style),
            Paragraph("Documented using technical schemas, data dictionaries, and performance criteria.", tbl_cell_style),
        ],
    ]
    t_req = Table([req_headers] + req_rows, colWidths=[110, 215, 215])
    t_req.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.1 The 2 Functional Requirements (FR)", h2_style))
    story.append(Paragraph(
        "• <b>FR-1: Route Schedule Browsing & Interactive Seat Selection</b> — The system shall allow commuters and dispatchers "
        "to browse intercity bus schedules (origin, destination, departure time, and base fare) and dynamically select an available seat "
        "through an interactive 2×2 bus cabin layout with an aisle.",
        body_style,
    ))
    story.append(Paragraph(
        "• <b>FR-2: Booking Processing, Ticket Issuance & Lifecycle Cancellation</b> — The system shall process confirmed seat reservations "
        "into persistent SQLite records, generate tamper-resistant verification codes, and support ticket cancellation with immediate seat inventory "
        "release and audit logging.",
        body_style,
    ))

    story.append(Paragraph("1.2 The 2 Non-Functional Requirements (NFR)", h2_style))
    story.append(Paragraph(
        "• <b>NFR-1: Security, Validation & Tamper Resistance</b> — All passenger inputs undergo strict sanitization. Contact numbers must conform "
        "to standard mobile formats (<code>09XXXXXXXXX</code> or <code>+639XXXXXXXXX</code>). Concession fare discounts require mandatory verification "
        "of official institutional/government ID credentials (minimum 4 characters). Every ticket is issued with an 8-character cryptographically salted "
        "SHA-256 reference code (<code>BTK-[HEX]</code>) preventing counterfeiting.",
        body_style,
    ))
    story.append(Paragraph(
        "• <b>NFR-2: Maintainability, Clean Architecture & Double-Booking Prevention</b> — The codebase strictly enforces Object-Oriented encapsulation "
        "(private <code>_</code> attributes, <code>@property</code> getters, and <code>@setter</code> validation raising <code>TypeError</code> or <code>ValueError</code>) "
        "conforming to PEP 8 standards. At the database layer, an ACID-compliant SQLite schema with a partial unique index "
        "(<code>ON tickets (route_id, travel_date, seat_number) WHERE status = 'Confirmed'</code>) mathematically guarantees zero double-booking.",
        body_style,
    ))

    # -------------------------------------------------------------------------
    # SECTION 2: UNIQUE USE CASE
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Unique System Use Case", h1_style))
    story.append(Paragraph("<b>Interactive Visual Seat Layout Matrix with Senior/PWD Priority Allocation & Concession Discount Engine (UC-SMARTBUS-01)</b>", h2_style))
    story.append(Paragraph(
        "<b>Actor:</b> Commuter / Ticketing Counter Agent &nbsp;|&nbsp; <b>Precondition:</b> Routes & Fleet Buses initialized in SQLite.<br/>"
        "<b>Workflow Narrative:</b><br/>"
        "1. Dispatcher selects <i>RT-101: Manila (Cubao) &rarr; Baguio City</i> and travel date.<br/>"
        "2. System draws the <b>Visual Cabin Seat Map</b>: Row 1 (Seats 1-4) is color-coded in <b>Amber</b> as <b>Priority Seating</b> "
        "(Senior Citizens, PWDs, Pregnant), while Rows 2-6 are standard <b>Green</b>.<br/>"
        "3. Selecting an available seat highlights it in <b>Blue</b> (<code>[✓]</code>). Non-priority commuters choosing Row 1 trigger a confirmation alert.<br/>"
        "4. Selecting <b>Senior Citizen</b>, <b>PWD</b>, or <b>Student</b> dynamically unlocks the Concession ID input and applies a statutory <b>20% discount</b> "
        "(Base PHP 580.00 &rarr; Net PHP 464.00).<br/>"
        "5. Booking is committed to SQLite, seat status transitions to <b>Occupied [X]</b>, and an official printable boarding pass is issued.",
        body_style,
    ))

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # SECTION 3: STANDARD PROCESS FLOWCHARTS (GENERIC SHAPES)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Operational Process Flowcharts (Standard Flowchart Representation)", h1_style))
    story.append(Paragraph(
        "The following diagrams depict the operational workflows utilizing standard generic flowchart shapes: "
        "<b>Terminator capsules</b> (Start/End), <b>Input/Output parallelograms</b>, <b>Process rectangles</b>, "
        "<b>Decision diamonds</b> (Branching logic), and <b>Database cylinders</b> (SQLite queries):",
        body_style,
    ))

    story.append(Paragraph("3.1 Standard Flowchart: Ticket Booking & Concession Allocation (FR-1 & Unique UC)", h2_style))
    flowchart1_img = get_scaled_image(os.path.join(screenshots_dir, "flowchart_booking_process.png"), max_w=520, max_h=580)
    if flowchart1_img:
        story.append(flowchart1_img)

    story.append(PageBreak())

    story.append(Paragraph("3.2 Standard Flowchart: Atomic SQLite Commit & Ticket Cancellation (FR-2 & NFR-2)", h2_style))
    story.append(Paragraph(
        "Illustrates the atomic write transaction, double-booking rollback guard, and ticket cancellation lifecycle with instant seat restoration:",
        body_style,
    ))
    flowchart2_img = get_scaled_image(os.path.join(screenshots_dir, "flowchart_cancellation_process.png"), max_w=520, max_h=580)
    if flowchart2_img:
        story.append(flowchart2_img)

    story.append(PageBreak())

    story.append(Paragraph("3.3 High-Level Layered Architecture & Relational Data Flow", h2_style))
    story.append(Paragraph(
        "Depicts the structural separation across the Presentation Layer (Tkinter GUI), Business Logic / Factory Layer, Data Access Layer (BusTicketingDatabase Singleton), and SQLite Persistence Engine:",
        body_style,
    ))
    arch_img = get_scaled_image(os.path.join(screenshots_dir, "flowchart_system_architecture.png"), max_w=520, max_h=500)
    if arch_img:
        story.append(arch_img)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # SECTION 4: UI WIREFRAME BLUEPRINTS
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. UI Wireframe Schematics & Layout Blueprints", h1_style))
    story.append(Paragraph(
        "Clean component wireframe schematics illustrating interface layout, buttons, dropdowns, tables, and the 2×2 seat map across all three tabs:",
        body_style,
    ))

    story.append(Paragraph("4.1 Tab 1 Wireframe: Book Tickets & Visual Seat Map", h2_style))
    w1_img = get_scaled_image(os.path.join(screenshots_dir, "wireframe_tab1_booking.png"), max_w=520, max_h=340)
    if w1_img:
        story.append(w1_img)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.2 Tab 2 Wireframe: Manage Bookings & Audit Dossier", h2_style))
    w2_img = get_scaled_image(os.path.join(screenshots_dir, "wireframe_tab2_management.png"), max_w=520, max_h=340)
    if w2_img:
        story.append(w2_img)

    story.append(PageBreak())

    story.append(Paragraph("4.3 Tab 3 Wireframe: System Overview & Fleet Analytics", h2_style))
    w3_img = get_scaled_image(os.path.join(screenshots_dir, "wireframe_tab3_analytics.png"), max_w=520, max_h=340)
    if w3_img:
        story.append(w3_img)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.4 Official SmartBus Boarding Pass Modal Dialog", h2_style))
    pass_img = get_scaled_image(os.path.join(screenshots_dir, "06_boarding_pass_modal.png"), max_w=400, max_h=260)
    if pass_img:
        story.append(pass_img)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # SECTION 5: VERIFICATION TEST MATRIX
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Verification Test Suite Matrix (12/12 Passing)", h1_style))
    story.append(Paragraph(
        "The system was validated using an automated <code>unittest.TestCase</code> suite testing all functional and non-functional requirements:",
        body_style,
    ))

    test_headers = [Paragraph("<b>Test ID</b>", tbl_hdr_style), Paragraph("<b>Test Method Name</b>", tbl_hdr_style), Paragraph("<b>Category</b>", tbl_hdr_style), Paragraph("<b>Verification Criteria</b>", tbl_hdr_style), Paragraph("<b>Status</b>", tbl_hdr_style)]
    test_rows = [
        [Paragraph("TC-01", tbl_cell_style), Paragraph("test_01_singleton_database_instance", tbl_cell_style), Paragraph("Architecture", tbl_cell_style), Paragraph("Verifies BusTicketingDatabase enforces Singleton pattern across calls.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-02", tbl_cell_style), Paragraph("test_02_sqlite_persistence_roundtrip", tbl_cell_style), Paragraph("Persistence", tbl_cell_style), Paragraph("Verifies SQLite CRUD operations for Routes, Buses, and Passengers.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-03", tbl_cell_style), Paragraph("test_03_route_validation_boundaries", tbl_cell_style), Paragraph("NFR-2", tbl_cell_style), Paragraph("Verifies positive distance and non-negative base fare constraints.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-04", tbl_cell_style), Paragraph("test_04_bus_seating_and_priority_validation", tbl_cell_style), Paragraph("NFR-2", tbl_cell_style), Paragraph("Verifies seating bounds and priority seat designations.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-05", tbl_cell_style), Paragraph("test_05_passenger_contact_format_validation", tbl_cell_style), Paragraph("NFR-1", tbl_cell_style), Paragraph("Verifies mobile contact regex sanitization (09XXXXXXXXX).", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-06", tbl_cell_style), Paragraph("test_06_mandatory_concession_id_validation_nfr1", tbl_cell_style), Paragraph("NFR-1", tbl_cell_style), Paragraph("Verifies mandatory concession ID check for Senior, PWD, and Student.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-07", tbl_cell_style), Paragraph("test_07_senior_priority_seat_and_concession_discount", tbl_cell_style), Paragraph("Unique UC", tbl_cell_style), Paragraph("Verifies Row 1 priority seat booking with statutory 20% discount.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-08", tbl_cell_style), Paragraph("test_08_regular_passenger_full_fare", tbl_cell_style), Paragraph("FR-1", tbl_cell_style), Paragraph("Verifies regular passengers receive standard undiscounted fare.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-09", tbl_cell_style), Paragraph("test_09_tamper_resistant_reference_code_format_nfr1", tbl_cell_style), Paragraph("NFR-1", tbl_cell_style), Paragraph("Verifies cryptographically salted SHA-256 reference codes (BTK-XXXXXX).", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-10", tbl_cell_style), Paragraph("test_10_atomic_double_booking_prevention_nfr2", tbl_cell_style), Paragraph("NFR-2", tbl_cell_style), Paragraph("Verifies duplicate seat booking raises ValueError & rolls back transaction.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-11", tbl_cell_style), Paragraph("test_11_ticket_cancellation_releases_seat_fr2", tbl_cell_style), Paragraph("FR-2", tbl_cell_style), Paragraph("Verifies cancelled ticket releases seat for immediate re-booking.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
        [Paragraph("TC-12", tbl_cell_style), Paragraph("test_12_analytics_calculation", tbl_cell_style), Paragraph("Metrics", tbl_cell_style), Paragraph("Verifies gross revenue, ticket counters, and subsidy calculations.", tbl_cell_style), Paragraph("<b>PASS</b>", tbl_cell_style)],
    ]
    t_test = Table([test_headers] + test_rows, colWidths=[40, 160, 65, 230, 45])
    t_test.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TEXTCOLOR", (4, 1), (4, -1), colors.HexColor("#16A34A")),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Unit Test Execution Console Output:", h2_style))
    test_img = get_scaled_image(os.path.join(screenshots_dir, "09_unit_tests_pass.png"), max_w=520, max_h=300)
    if test_img:
        story.append(test_img)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF build complete: {output_pdf}")

    # Also save a copy as README.pdf
    import shutil
    shutil.copyfile(output_pdf, readme_pdf)
    print(f"Copied to: {readme_pdf}")


if __name__ == "__main__":
    generate_pdf()
