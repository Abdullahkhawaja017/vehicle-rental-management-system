import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from PIL import Image, ImageTk
import os
import controllers.car_controller as cc
import controllers.rental_request_controller as rrc
from app import session

# --- Design Configuration ---
COLOR_BG_MAIN = "#f4f7f6"     # Soft Gray for Right Panel
COLOR_SIDEBAR = "#1c2e4a"     # Dark Navy for Left Panel
COLOR_ACCENT = "#3b82f6"      # Bright Blue (Highlights)
COLOR_WHITE = "#ffffff"
COLOR_TEXT_DARK = "#1e293b"   # Slate 800
COLOR_TEXT_LIGHT = "#64748b"  # Slate 500
COLOR_SUCCESS = "#10b981"     # Green

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

def show_rent_car_window(parent=None):
    
    # 1. Hide Dashboard
    if parent:
        parent.withdraw()

    window = tk.Toplevel()
    window.title("Rent a Vehicle - Car Rental System")
    
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
            # --- FIX: Restore Parent to Full Screen ---
            try:
                parent.state("zoomed")
            except tk.TclError:
                pass 
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    # =========================================================================
    # LAYOUT STRUCTURE
    # =========================================================================
    
    # Left Panel: Sidebar (Navigation & Filters)
    left_panel = tk.Frame(window, bg=COLOR_SIDEBAR, width=320)
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    # Right Panel: Content (List & Booking Form)
    right_panel = tk.Frame(window, bg=COLOR_BG_MAIN)
    right_panel.pack(side="right", fill="both", expand=True)

    # =========================================================================
    # LEFT PANEL: SIDEBAR & FILTERS
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

    # Header
    tk.Label(left_panel, text="Find Your Ride", font=("Segoe UI", 20, "bold"), 
             bg=COLOR_SIDEBAR, fg="white").pack(padx=20, anchor="w")
    tk.Label(left_panel, text="Use filters to narrow down\nyour search.", font=("Segoe UI", 10), 
             bg=COLOR_SIDEBAR, fg="#94a3b8", justify="left").pack(padx=20, anchor="w", pady=(5, 20))

    # --- FILTER SECTION ---
    filter_container = tk.LabelFrame(left_panel, text="Filter Options", font=("Segoe UI", 11, "bold"),
                                     bg=COLOR_SIDEBAR, fg="white", bd=1, relief="solid")
    filter_container.pack(fill="x", padx=20, pady=10)

    # Make Filter
    tk.Label(filter_container, text="Manufacturer:", font=("Segoe UI", 10), bg=COLOR_SIDEBAR, fg="#cbd5e1").pack(anchor="w", padx=15, pady=(15, 5))
    makes_list = ["All"] + cc.get_distinct_makes()
    combo_make = ttk.Combobox(filter_container, values=makes_list, state="readonly", font=("Segoe UI", 10))
    combo_make.current(0)
    combo_make.pack(fill="x", padx=15, pady=(0, 15))

    # Type Filter
    tk.Label(filter_container, text="Vehicle Type:", font=("Segoe UI", 10), bg=COLOR_SIDEBAR, fg="#cbd5e1").pack(anchor="w", padx=15, pady=(5, 5))
    types_list = ["All", "Sedan", "SUV", "Hatchback", "Truck", "Luxury"]
    combo_type = ttk.Combobox(filter_container, values=types_list, state="readonly", font=("Segoe UI", 10))
    combo_type.current(0)
    combo_type.pack(fill="x", padx=15, pady=(0, 20))

    # Search Button
    btn_search = tk.Button(filter_container, text="🔍 Apply Filters", font=FONT_BTN, 
                           bg=COLOR_ACCENT, fg="white", bd=0, cursor="hand2", pady=8,
                           activebackground="#2563eb", activeforeground="white",
                           command=lambda: load_data())
    btn_search.pack(fill="x", padx=15, pady=(0, 20))

    # =========================================================================
    # RIGHT PANEL: MAIN CONTENT
    # =========================================================================
    
    container = tk.Frame(right_panel, bg=COLOR_BG_MAIN)
    container.pack(fill="both", expand=True, padx=30, pady=30)

    tk.Label(container, text="Available Fleet", font=FONT_HEADER, 
             bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DARK).pack(anchor="w", pady=(0, 20))

    # Split Layout for Content: Left (List) - Right (Details Card)
    content_split = tk.Frame(container, bg=COLOR_BG_MAIN)
    content_split.pack(fill="both", expand=True)

    # --- LEFT: CAR LIST ---
    list_frame = tk.Frame(content_split, bg=COLOR_WHITE)
    list_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
    
    # Decorative Strip
    tk.Frame(list_frame, bg="#cbd5e1", height=2).pack(fill="x")

    # Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 
    style.configure("Treeview", background=COLOR_WHITE, fieldbackground=COLOR_WHITE, foreground=COLOR_TEXT_DARK, rowheight=40, font=("Segoe UI", 10), borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#f1f5f9", foreground=COLOR_TEXT_DARK, relief="flat")
    style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "white")])

    columns = ("ID", "Make", "Model", "Year", "Price", "Type", "Status")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("ID", text="ID")
    tree.heading("Make", text="Make")
    tree.heading("Model", text="Model")
    tree.heading("Year", text="Year")
    tree.heading("Price", text="Daily Rate")
    tree.heading("Type", text="Type")
    tree.heading("Status", text="Status")

    tree.column("ID", width=40, anchor="center")
    tree.column("Make", width=100)
    tree.column("Model", width=100)
    tree.column("Year", width=60, anchor="center")
    tree.column("Price", width=80, anchor="e")
    tree.column("Type", width=80, anchor="center")
    tree.column("Status", width=80, anchor="center")

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- RIGHT: BOOKING STATION CARD ---
    booking_card = tk.Frame(content_split, bg=COLOR_WHITE, width=350)
    booking_card.pack(side="right", fill="y")
    booking_card.pack_propagate(False) # Keep fixed width

    # Card Header
    tk.Frame(booking_card, bg=COLOR_ACCENT, height=5).pack(fill="x")
    tk.Label(booking_card, text="Booking Station", font=FONT_SUBHEADER, bg=COLOR_WHITE, fg=COLOR_TEXT_DARK).pack(pady=20)

    # Image Preview
    img_container = tk.Frame(booking_card, bg="#f8fafc", width=300, height=200, highlightbackground="#e2e8f0", highlightthickness=1)
    img_container.pack(pady=10)
    img_container.pack_propagate(False)
    
    lbl_image = tk.Label(img_container, text="Select a car\nto view details", bg="#f8fafc", fg="#94a3b8", font=("Segoe UI", 10))
    lbl_image.place(relx=0.5, rely=0.5, anchor="center")

    # Car Info Placeholder
    lbl_selected_car = tk.Label(booking_card, text="No Car Selected", font=("Segoe UI", 12, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT_DARK)
    lbl_selected_car.pack(pady=(10, 0))
    
    lbl_rate = tk.Label(booking_card, text="", font=("Segoe UI", 11), bg=COLOR_WHITE, fg=COLOR_ACCENT)
    lbl_rate.pack(pady=(0, 20))

    # Form
    form_frame = tk.Frame(booking_card, bg=COLOR_WHITE)
    form_frame.pack(fill="x", padx=30)

    tk.Label(form_frame, text="Start Date:", font=FONT_LABEL, bg=COLOR_WHITE).pack(anchor="w", pady=(5, 0))
    entry_start = DateEntry(form_frame, width=25, background=COLOR_ACCENT, foreground='white', borderwidth=0, date_pattern='y-mm-dd', font=("Segoe UI", 10))
    entry_start.pack(fill="x", pady=5, ipady=3)

    tk.Label(form_frame, text="End Date:", font=FONT_LABEL, bg=COLOR_WHITE).pack(anchor="w", pady=(10, 0))
    entry_end = DateEntry(form_frame, width=25, background=COLOR_ACCENT, foreground='white', borderwidth=0, date_pattern='y-mm-dd', font=("Segoe UI", 10))
    entry_end.pack(fill="x", pady=5, ipady=3)

    # Hidden ID storage
    selected_car_id = tk.IntVar(value=0)

    # Submit Button Logic
    def submit_request():
        car_id = selected_car_id.get()
        if not car_id:
            messagebox.showwarning("Selection Required", "Please select a vehicle from the list first.", parent=window)
            return
        
        start_date = entry_start.get_date()
        end_date = entry_end.get_date()
        today = date.today()

        if start_date < today:
            messagebox.showerror("Invalid Date", "Start Date cannot be in the past.", parent=window)
            return
        if end_date <= start_date:
            messagebox.showerror("Invalid Date", "End Date must be after Start Date.", parent=window)
            return

        user = session.get_current_user()
        success, msg = rrc.create_rental_request(user['user_id'], car_id, str(start_date), str(end_date))
        
        if success:
            messagebox.showinfo("Request Sent", msg, parent=window)
            window.destroy()
        else:
            messagebox.showerror("Error", msg, parent=window)

    # Submit Button
    tk.Label(booking_card, text="", bg=COLOR_WHITE).pack(fill="y", expand=True) # Spacer
    
    btn_submit = tk.Button(booking_card, text="Request Booking", font=FONT_BTN, 
                           bg=COLOR_SUCCESS, fg="white", bd=0, cursor="hand2", pady=12,
                           activebackground="#059669", activeforeground="white",
                           command=submit_request)
    btn_submit.pack(fill="x", side="bottom")

    # =========================================================================
    # LOGIC: DATA & IMAGE
    # =========================================================================

    car_image_map = {}

    def load_data():
        for item in tree.get_children():
            tree.delete(item)
        car_image_map.clear()
        
        cars = cc.search_cars(combo_make.get(), combo_type.get())
        for car in cars:
            # car schema assumption: id(0), make(1), model(2), year(3), reg(4), type(5), price(6), status(7)... image(9)?
            tree.insert("", tk.END, iid=car[0], values=(car[0], car[1], car[2], car[3], f"${car[6]}", car[5], car[7]))
            
            # --- CRITICAL FIX ---
            # Use Index 9 for Image Path (Index 8 is 'created_at' timestamp)
            if len(car) > 9: 
                car_image_map[car[0]] = car[9] 

    def on_select(event):
        selected_item = tree.selection()
        if not selected_item:
            return
        
        # Get Data
        car_id = int(selected_item[0]) # iid is car_id
        values = tree.item(selected_item, 'values')
        
        # Update Booking Card
        selected_car_id.set(car_id)
        lbl_selected_car.config(text=f"{values[1]} {values[2]}")
        lbl_rate.config(text=f"{values[4]} / day")

        # Load Image
        img_path = car_image_map.get(car_id)
        if img_path and os.path.exists(img_path):
            try:
                load = Image.open(img_path)
                load.thumbnail((280, 180)) # Resize maintaining aspect ratio
                render = ImageTk.PhotoImage(load)
                lbl_image.config(image=render, text="")
                lbl_image.image = render
            except Exception:
                lbl_image.config(image="", text="Image Error")
        else:
            lbl_image.config(image="", text="No Image Available")

    tree.bind("<<TreeviewSelect>>", on_select)
    
    # Initial Load
    load_data()