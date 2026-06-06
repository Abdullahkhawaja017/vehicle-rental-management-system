import tkinter as tk
from tkinter import ttk, messagebox
import controllers.booking_controller as bc
from app import session

# --- Design Configuration ---
COLOR_BG_MAIN = "#f4f7f6"     # Soft Gray for Right Panel
COLOR_SIDEBAR = "#1c2e4a"     # Dark Navy for Left Panel
COLOR_ACCENT = "#3b82f6"      # Bright Blue (Highlights)
COLOR_WHITE = "#ffffff"
COLOR_TEXT_DARK = "#1e293b"   # Slate 800
COLOR_TEXT_LIGHT = "#64748b"  # Slate 500
COLOR_SUCCESS = "#10b981"     # Green
COLOR_WARNING = "#f59e0b"     # Amber

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

def show_bookings_window(parent=None):
    
    # 1. Hide Dashboard
    if parent:
        parent.withdraw()

    window = tk.Toplevel()
    window.title("Booking Management - Car Rental System")
    
    # Attempt Full Screen
    try:
        window.state("zoomed")
    except tk.TclError:
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        window.geometry(f"{width}x{height}")

    window.configure(bg=COLOR_BG_MAIN)

    # 2. Handle Closing
    def on_close():
        if parent:
            parent.deiconify()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    # =========================================================================
    # LAYOUT STRUCTURE
    # =========================================================================
    
    # Left Panel: Sidebar
    left_panel = tk.Frame(window, bg=COLOR_SIDEBAR, width=350)
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    # Right Panel: Content
    right_panel = tk.Frame(window, bg=COLOR_BG_MAIN)
    right_panel.pack(side="right", fill="both", expand=True)

    # =========================================================================
    # LEFT PANEL
    # =========================================================================
    
    # Back Button
    back_btn_frame = tk.Frame(left_panel, bg=COLOR_SIDEBAR)
    back_btn_frame.pack(fill="x", padx=20, pady=20)
    
    def btn_back_hover(e):
        btn_back.config(bg="#334155") 
    def btn_back_leave(e):
        btn_back.config(bg=COLOR_SIDEBAR)

    btn_back = tk.Button(back_btn_frame, text="← Back to Dashboard", font=("Segoe UI", 11), 
                         bg=COLOR_SIDEBAR, fg="white", bd=0, cursor="hand2", anchor="w",
                         activebackground=COLOR_SIDEBAR, activeforeground="white",
                         command=on_close)
    btn_back.pack(fill="x")
    btn_back.bind("<Enter>", btn_back_hover)
    btn_back.bind("<Leave>", btn_back_leave)

    tk.Frame(left_panel, bg="#334155", height=1).pack(fill="x", padx=20, pady=(0, 20))

    # Sidebar Info
    tk.Label(left_panel, text="Active Rentals", font=("Segoe UI", 20, "bold"), 
             bg=COLOR_SIDEBAR, fg="white").pack(padx=20, anchor="w")
    
    tk.Label(left_panel, text="Manage all ongoing and\npast booking records here.", font=("Segoe UI", 10), 
             bg=COLOR_SIDEBAR, fg="#94a3b8", justify="left").pack(padx=20, anchor="w", pady=(5, 0))

    # =========================================================================
    # RIGHT PANEL: CONTENT
    # =========================================================================
    
    container = tk.Frame(right_panel, bg=COLOR_BG_MAIN)
    container.pack(fill="both", expand=True, padx=40, pady=40)

    # Header
    header_frame = tk.Frame(container, bg=COLOR_BG_MAIN)
    header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(header_frame, text="Booking Overview", font=FONT_HEADER, 
             bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DARK).pack(side="left")

    # --- MAIN CARD ---
    card = tk.Frame(container, bg=COLOR_WHITE)
    card.pack(fill="both", expand=True)
    
    # Decorative Top Strip
    tk.Frame(card, bg=COLOR_ACCENT, height=4).pack(fill="x")

    # Treeview Container
    tree_frame = tk.Frame(card, bg=COLOR_WHITE, padx=20, pady=20)
    tree_frame.pack(fill="both", expand=True)

    # Treeview Styles
    style = ttk.Style()
    style.theme_use("clam")
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 
    style.configure("Treeview", 
                    background=COLOR_WHITE, fieldbackground=COLOR_WHITE, foreground=COLOR_TEXT_DARK, 
                    rowheight=40, font=("Segoe UI", 10), borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                    background="#f1f5f9", foreground=COLOR_TEXT_DARK, relief="flat")
    style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "white")])

    # Columns
    columns = ("ID", "Cust ID", "Car ID", "Start", "End", "Status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("ID", text="ID")
    tree.heading("Cust ID", text="Cust ID")
    tree.heading("Car ID", text="Car ID")
    tree.heading("Start", text="Start Date")
    tree.heading("End", text="End Date")
    tree.heading("Status", text="Status")

    tree.column("ID", width=50, anchor="center")
    tree.column("Cust ID", width=80, anchor="center")
    tree.column("Car ID", width=80, anchor="center")
    tree.column("Start", width=150)
    tree.column("End", width=150)
    tree.column("Status", width=120, anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # =========================================================================
    # ACTIONS & LOGIC
    # =========================================================================

    def refresh_data():
        for item in tree.get_children():
            tree.delete(item)
        try:
            bookings = bc.get_all_bookings()
            for b in bookings:
                # b = (id, user_id, cust_id, car_id, start, end, total, status, ...)
                # Adjust indices based on your controller's query
                tree.insert("", tk.END, values=(b[0], b[2], b[3], b[4], b[5], b[7]))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load bookings: {e}")

    refresh_data()

    # --- Action Bar (Bottom) ---
    user = session.get_current_user()
    
    # Only Admin and Employees can see actions
    if user['role'] in ['Admin', 'Employee']:
        action_bar = tk.Frame(container, bg=COLOR_BG_MAIN, height=80)
        action_bar.pack(fill="x", pady=(20, 0))

        def return_car():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Booking", "Please select a booking to return.")
                return

            values = tree.item(selected, 'values')
            booking_id = values[0]
            status = values[5]

            if status != "Active":
                messagebox.showerror("Error", "This car is already returned or cancelled.")
                return

            confirm = messagebox.askyesno("Confirm Return", "Are you sure you want to return this car now?\nThis will generate the final bill.")
            if confirm:
                success, msg = bc.process_return(booking_id)
                if success:
                    messagebox.showinfo("Success", msg)
                    refresh_data()
                else:
                    messagebox.showerror("Error", msg)

        # Styled Button
        btn_return = tk.Button(action_bar, text="🔄 Process Return", font=FONT_BTN, 
                               bg=COLOR_WARNING, fg="black", padx=25, pady=10, bd=0, cursor="hand2",
                               activebackground="#d97706", activeforeground="black",
                               command=return_car)
        btn_return.pack(side="right")
        
        tk.Label(action_bar, text="Select an 'Active' booking to process return.", 
                 font=("Segoe UI", 10, "italic"), bg=COLOR_BG_MAIN, fg=COLOR_TEXT_LIGHT).pack(side="right", padx=20)