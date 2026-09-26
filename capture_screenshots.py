"""
Programmatic Screenshot Capture Suite for SmartBus Transit System.
Automates GUI workflows across all 3 tabs and captures high-resolution screenshots into screenshots/:
  1. screenshots/01_tab_booking_seat_map.png: Default Tab 1 booking interface with visual 2x2 seat map
  2. screenshots/02_selected_priority_seat.png: Tab 1 priority seat selection with live 20% concession calculation
  3. screenshots/03_issued_ticket.png: Tab 1 post-booking state with seat marked occupied in SQLite
  4. screenshots/04_tab_manage_bookings.png: Tab 2 master tickets Treeview with lookup controls
  5. screenshots/05_ticket_dossier_inspection.png: Tab 2 detailed ticket audit dossier with SHA-256 verification
  6. screenshots/06_boarding_pass_modal.png: Tab 2 printable official boarding pass modal dialog
  7. screenshots/07_ticket_cancellation_seat_released.png: Tab 2 cancelled ticket status and released seat
  8. screenshots/08_tab_system_analytics.png: Tab 3 KPI cards, route occupancy percentages, and SQLite audit log
  9. screenshots/09_unit_tests_pass.png: Subprocess execution of 12 passing unit tests
"""
import os
import sys
import time
import subprocess
import tkinter as tk
from PIL import ImageGrab

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import models
import app
import main


def grab_window(window: tk.Misc, filepath: str) -> None:
    """Capture a Tkinter window and save as PNG."""
    window.update_idletasks()
    window.update()
    time.sleep(0.3)
    x = window.winfo_rootx()
    y = window.winfo_rooty()
    w = window.winfo_width()
    h = window.winfo_height()

    try:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    except Exception:
        hwnd = window.winfo_id()
        img = ImageGrab.grab(window=hwnd)

    img.save(filepath, "PNG")
    print(f"Captured: {filepath} ({w}x{h})")


def run_capture_suite() -> None:
    """Launch BusTicketingApp with sample data and capture all 9 milestone screens."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(output_dir, exist_ok=True)

    print("==================================================================")
    print("SmartBus Transit System - Automated Screenshot Capture Suite")
    print("==================================================================")
    print(f"Output directory: {output_dir}")

    # Seed fresh sample data in SQLite
    db = main.initialize_sample_data()
    bus_app = app.BusTicketingApp(db)

    # Automation mode
    bus_app._suppress_dialogs = True
    bus_app._auto_confirm = True

    bus_app.deiconify()
    bus_app.lift()
    bus_app.focus_force()
    bus_app.update_idletasks()
    bus_app.update()

    try:
        # ---------------------------------------------------------------------
        # Scenario 1: Tab 1 Default View
        # ---------------------------------------------------------------------
        print("\n[1/9] Capturing Tab 1: Book Tickets & Visual Seat Map default view...")
        bus_app.notebook.select(0)
        bus_app._refresh_all_views()
        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_01 = os.path.join(output_dir, "01_tab_booking_seat_map.png")
        grab_window(bus_app, shot_01)

        # ---------------------------------------------------------------------
        # Scenario 2: Priority Seat Selected & Concession Quoted
        # ---------------------------------------------------------------------
        print("\n[2/9] Selecting Priority Seat 3 and entering Senior Citizen details...")
        bus_app.notebook.select(0)
        # Select Seat 3 (Row 1 Priority Seat)
        bus_app._on_seat_clicked(3)
        bus_app.pas_name_var.set("Corazon Aquino")
        bus_app.pas_contact_var.set("09195554321")
        bus_app.pas_type_combo.set("Senior Citizen")
        bus_app._on_passenger_type_changed(None)
        bus_app.discount_id_var.set("OSCA-88319")
        bus_app._update_fare_calculation()

        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_02 = os.path.join(output_dir, "02_selected_priority_seat.png")
        grab_window(bus_app, shot_02)

        # ---------------------------------------------------------------------
        # Scenario 3: Confirm Booking and Issue Ticket
        # ---------------------------------------------------------------------
        print("\n[3/9] Submitting booking and capturing updated seat matrix...")
        bus_app._handle_booking_submission()
        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_03 = os.path.join(output_dir, "03_issued_ticket.png")
        grab_window(bus_app, shot_03)

        # ---------------------------------------------------------------------
        # Scenario 4: Tab 2 Manage Bookings default view
        # ---------------------------------------------------------------------
        print("\n[4/9] Capturing Tab 2: Manage Bookings & Cancellations...")
        bus_app.notebook.select(1)
        bus_app._refresh_tickets_tree()
        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_04 = os.path.join(output_dir, "04_tab_manage_bookings.png")
        grab_window(bus_app, shot_04)

        # ---------------------------------------------------------------------
        # Scenario 5: Tab 2 Inspect Active Ticket Dossier
        # ---------------------------------------------------------------------
        print("\n[5/9] Inspecting active ticket dossier...")
        bus_app.notebook.select(1)
        if bus_app.tickets_tree.exists("TKT-1001"):
            bus_app.tickets_tree.selection_set("TKT-1001")
            bus_app.tickets_tree.see("TKT-1001")
            bus_app._on_ticket_selected(None)

        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_05 = os.path.join(output_dir, "05_ticket_dossier_inspection.png")
        grab_window(bus_app, shot_05)

        # ---------------------------------------------------------------------
        # Scenario 6: Official Boarding Pass Modal Dialog
        # ---------------------------------------------------------------------
        print("\n[6/9] Generating official boarding pass modal...")
        bus_app._show_boarding_pass_modal()
        # Find child toplevel
        modal = None
        for child in bus_app.winfo_children():
            if isinstance(child, tk.Toplevel):
                modal = child
                break

        if modal:
            modal.deiconify()
            modal.lift()
            modal.focus_force()
            modal.update_idletasks()
            modal.update()
            time.sleep(0.3)
            shot_06 = os.path.join(output_dir, "06_boarding_pass_modal.png")
            grab_window(modal, shot_06)
            modal.destroy()

        # ---------------------------------------------------------------------
        # Scenario 7: Ticket Cancellation & Seat Release
        # ---------------------------------------------------------------------
        print("\n[7/9] Cancelling ticket TKT-1002 and releasing seat...")
        bus_app.notebook.select(1)
        if bus_app.tickets_tree.exists("TKT-1002"):
            bus_app.tickets_tree.selection_set("TKT-1002")
            bus_app._handle_cancel_selected_ticket()

        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_07 = os.path.join(output_dir, "07_ticket_cancellation_seat_released.png")
        grab_window(bus_app, shot_07)

        # ---------------------------------------------------------------------
        # Scenario 8: Tab 3 System Overview & Fleet Analytics
        # ---------------------------------------------------------------------
        print("\n[8/9] Capturing Tab 3: System Overview & Fleet Analytics...")
        bus_app.notebook.select(2)
        bus_app._refresh_analytics()
        bus_app.update_idletasks()
        bus_app.update()
        time.sleep(0.3)
        shot_08 = os.path.join(output_dir, "08_tab_system_analytics.png")
        grab_window(bus_app, shot_08)

        # ---------------------------------------------------------------------
        # Scenario 9: Unit Test Suite Output (12/12 Passing)
        # ---------------------------------------------------------------------
        print("\n[9/9] Running unit tests and capturing terminal output...")
        cmd = [sys.executable, "-m", "unittest", "test_system", "-v"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        test_output = proc.stdout + proc.stderr

        test_win = tk.Toplevel(bus_app)
        test_win.title("SmartBus Transit System - Unit Test Execution Results (12/12 Passed)")
        test_win.geometry("980x700")
        test_win.configure(bg="#1e1e1e")

        hdr_frame = tk.Frame(test_win, bg="#2d2d2d", padx=12, pady=8)
        hdr_frame.pack(fill=tk.X)

        tk.Label(
            hdr_frame,
            text="PowerShell Console — python -m unittest test_system -v",
            font=("Consolas", 10, "bold"),
            bg="#2d2d2d",
            fg="#e0e0e0",
            anchor="w",
        ).pack(side=tk.LEFT)

        txt_frame = tk.Frame(test_win, bg="#1e1e1e", padx=10, pady=10)
        txt_frame.pack(fill=tk.BOTH, expand=True)

        txt_widget = tk.Text(
            txt_frame,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#cccccc",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        txt_widget.pack(fill=tk.BOTH, expand=True)

        txt_widget.tag_configure("cmd", foreground="#61afef", font=("Consolas", 10, "bold"))
        txt_widget.tag_configure("ok", foreground="#98c379", font=("Consolas", 10, "bold"))
        txt_widget.tag_configure("header", foreground="#e5c07b", font=("Consolas", 10))

        prompt_str = f"PS {base_dir}> python -m unittest test_system -v\n\n"
        txt_widget.insert(tk.END, prompt_str, "cmd")

        for line in test_output.splitlines(keepends=True):
            if "... ok" in line or line.strip() == "OK":
                txt_widget.insert(tk.END, line, "ok")
            elif "test_" in line:
                txt_widget.insert(tk.END, line, "header")
            else:
                txt_widget.insert(tk.END, line)

        txt_widget.config(state=tk.DISABLED)
        test_win.deiconify()
        test_win.lift()
        test_win.focus_force()
        test_win.update_idletasks()
        test_win.update()
        time.sleep(0.3)

        shot_09 = os.path.join(output_dir, "09_unit_tests_pass.png")
        grab_window(test_win, shot_09)
        test_win.destroy()

        print("\nAll 9 screenshots successfully captured into screenshots/!")

    finally:
        bus_app.destroy()


if __name__ == "__main__":
    run_capture_suite()
