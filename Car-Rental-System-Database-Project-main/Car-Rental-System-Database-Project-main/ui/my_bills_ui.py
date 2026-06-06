import tkinter as tk
from tkinter import ttk, messagebox
import controllers.billing_controller as bic
import controllers.payment_controller as payc
from app import session
from ui.bill_popup_ui import show_bill_popup

# --- Design Configuration ---
COLOR_BG_MAIN = "#f4f7f6"     # Soft Gray for Right Panel
COLOR_SIDEBAR = "#1c2e4a"     # Dark Navy for Left Panel
COLOR_ACCENT = "#3b82f6"      # Bright Blue (Highlights)
COLOR_WHITE = "#ffffff"
COLOR_TEXT_DARK = "#1e293b"   # Slate 800
COLOR_TEXT_LIGHT = "#64748b"  # Slate 500
COLOR_SUCCESS = "#10b981"     # Green for Pay Action

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

def show_my_bills_window(parent=None):
    
    # 1. Hide Dashboard
    if parent:
        parent.withdraw()

    window = tk.Toplevel()
    window.title("Billing History - Car Rental System")
    
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
    tk.Label(left_panel, text="My Invoices", font=("Segoe UI", 20, "bold"), 
             bg=COLOR_SIDEBAR, fg="white").pack(padx=20, anchor="w")
    
    tk.Label(left_panel, text="View history and pay outstanding\nbills securely.", font=("Segoe UI", 10), 
             bg=COLOR_SIDEBAR, fg="#94a3b8", justify="left").pack(padx=20, anchor="w", pady=(5, 0))

    # =========================================================================
    # RIGHT PANEL: CONTENT
    # =========================================================================
    
    container = tk.Frame(right_panel, bg=COLOR_BG_MAIN)
    container.pack(fill="both", expand=True, padx=40, pady=40)

    # Header
    header_frame = tk.Frame(container, bg=COLOR_BG_MAIN)
    header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(header_frame, text="Billing History", font=FONT_HEADER, 
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
    columns = ("BillID", "BookingID", "Car", "Amount", "Date", "Status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("BillID", text="Bill ID")
    tree.heading("BookingID", text="Booking Ref")
    tree.heading("Car", text="Car")
    tree.heading("Amount", text="Amount")
    tree.heading("Date", text="Billing Date")
    tree.heading("Status", text="Status")

    tree.column("BillID", width=60, anchor="center")
    tree.column("BookingID", width=100, anchor="center")
    tree.column("Car", width=150)
    tree.column("Amount", width=100)
    tree.column("Date", width=120)
    tree.column("Status", width=100, anchor="center")

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
        
        user = session.get_current_user()
        bills = bic.get_my_bills(user['user_id'])
        
        for b in bills:
            # b: (bill_id, booking_id, make, model, amount, date, status)
            car_name = f"{b[2]} {b[3]}"
            tree.insert("", tk.END, values=(b[0], b[1], car_name, f"${b[4]}", b[5], b[6]))

    refresh_data()

    # --- Action Bar (Bottom) ---
    action_bar = tk.Frame(container, bg=COLOR_BG_MAIN, height=80)
    action_bar.pack(fill="x", pady=(20, 0))

    def pay_bill():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a bill to pay.")
            return

        values = tree.item(selected, 'values')
        bill_id = values[0]
        booking_id = values[1]
        status = values[5]

        if status == "Paid":
            messagebox.showinfo("Info", "This bill is already paid.")
            return

        # Fetch full bill details
        user = session.get_current_user()
        bill_data = bic.get_bill_details(bill_id)  # You may need to create this function
        
        if bill_data:
            show_bill_popup(window, bill_data, refresh_data)
        else:
            messagebox.showerror("Error", "Could not load bill details.")

    # Styled Pay Button
    btn_pay = tk.Button(action_bar, text="💳 Pay Selected Bill", font=FONT_BTN, 
                        bg=COLOR_SUCCESS, fg="white", padx=25, pady=10, bd=0, cursor="hand2",
                        activebackground="#059669", activeforeground="white",
                        command=pay_bill)
    btn_pay.pack(side="right")
    
    tk.Label(action_bar, text="Secure Payment Gateway (Mock)", 
             font=("Segoe UI", 10, "italic"), bg=COLOR_BG_MAIN, fg=COLOR_TEXT_LIGHT).pack(side="right", padx=20)