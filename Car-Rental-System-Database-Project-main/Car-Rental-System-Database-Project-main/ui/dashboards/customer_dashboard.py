import tkinter as tk
from app import session
from ui.rent_car_ui import show_rent_car_window
from ui.my_bills_ui import show_my_bills_window
from ui.my_bookings_ui import show_my_bookings_window
from ui.notifications_ui import show_notifications_window
# removed top-level import to fix circular dependency

# --- Design Configuration ---
COLOR_BG = "#0f172a"          # Very Dark Slate (Background)
COLOR_CARD = "#ffffff"        # White (Main Surface)
COLOR_SHADOW = "#020617"      # Shadow Color
COLOR_ACCENT = "#10b981"      # Emerald Green (Specific for Customers)

# Tile Colors
COLOR_TILE_DEFAULT = "#f8fafc" 
COLOR_TILE_HOVER = "#ecfdf5"   # Light Green tint on hover
COLOR_TILE_BORDER = "#e2e8f0"  

COLOR_TEXT_DARK = "#1e293b"   
COLOR_TEXT_LIGHT = "#64748b"  

# Logout Button Colors (Soft Pill Style)
COLOR_LOGOUT_BG = "#fff1f2"    # Soft Rose Background
COLOR_LOGOUT_FG = "#e11d48"    # Rose Red Text
COLOR_LOGOUT_HOVER = "#ffe4e6" # Slightly Darker Rose on Hover

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_TILE_ICON = ("Segoe UI Emoji", 24) 
FONT_TILE_TITLE = ("Segoe UI", 12, "bold")
FONT_TILE_DESC = ("Segoe UI", 9)

def logout(root):
    session.logout()
    root.destroy()
    # Import locally to avoid circular import error
    from ui.login_ui import show_login_window
    show_login_window()

def show_customer_dashboard():
    root = tk.Tk()
    root.title("Customer Dashboard - Car Rental System")
    
    # --- Full Screen Setup ---
    try:
        root.state("zoomed")
    except tk.TclError:
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}")
        
    root.configure(bg=COLOR_BG)
    
    user = session.get_current_user()
    username = user['username'] if user else "Customer"

    # =========================================================================
    # VISUAL LAYOUT
    # =========================================================================
    
    # 1. DROP SHADOW 
    shadow_frame = tk.Frame(root, bg=COLOR_SHADOW)
    shadow_frame.place(relx=0.5, rely=0.5, anchor="center", width=860, height=640)

    # 2. MAIN CARD 
    hub_frame = tk.Frame(root, bg=COLOR_CARD)
    hub_frame.place(relx=0.5, rely=0.5, anchor="center", width=850, height=630)

    # Decorative Accent Line (Green for Customers)
    tk.Frame(hub_frame, bg=COLOR_ACCENT, height=6).pack(fill="x")

    # --- Header Section ---
    header_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    header_frame.pack(pady=(50, 30))

    tk.Label(header_frame, text="Customer Portal", font=FONT_TITLE, 
             bg=COLOR_CARD, fg=COLOR_TEXT_DARK).pack()
    
    tk.Label(header_frame, text=f"Welcome, {username}. Ready for your next journey?", 
             font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT).pack(pady=(5, 0))

    # --- TILE GRID CONTAINER ---
    grid_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    grid_frame.pack(expand=True)

    # --- CUSTOM TILE WIDGET BUILDER ---
    def create_tile(parent, icon, title, desc, command, r, c):
        tile = tk.Frame(parent, bg=COLOR_TILE_DEFAULT, 
                        highlightbackground=COLOR_TILE_BORDER, highlightthickness=1,
                        cursor="hand2", width=260, height=180)
        tile.grid(row=r, column=c, padx=15, pady=15)
        tile.pack_propagate(False) 
        
        content = tk.Frame(tile, bg=COLOR_TILE_DEFAULT)
        content.place(relx=0.5, rely=0.5, anchor="center")

        lbl_icon = tk.Label(content, text=icon, font=FONT_TILE_ICON, 
                            bg=COLOR_TILE_DEFAULT, fg=COLOR_ACCENT)
        lbl_icon.pack(pady=(0, 10))

        lbl_title = tk.Label(content, text=title, font=FONT_TILE_TITLE, 
                             bg=COLOR_TILE_DEFAULT, fg=COLOR_TEXT_DARK)
        lbl_title.pack(pady=(0, 5))

        lbl_desc = tk.Label(content, text=desc, font=FONT_TILE_DESC, 
                            bg=COLOR_TILE_DEFAULT, fg=COLOR_TEXT_LIGHT, justify="center")
        lbl_desc.pack()

        # Hover Effects
        def on_enter(e):
            tile.config(bg=COLOR_TILE_HOVER, highlightbackground=COLOR_ACCENT)
            content.config(bg=COLOR_TILE_HOVER)
            lbl_icon.config(bg=COLOR_TILE_HOVER)
            lbl_title.config(bg=COLOR_TILE_HOVER)
            lbl_desc.config(bg=COLOR_TILE_HOVER)

        def on_leave(e):
            tile.config(bg=COLOR_TILE_DEFAULT, highlightbackground=COLOR_TILE_BORDER)
            content.config(bg=COLOR_TILE_DEFAULT)
            lbl_icon.config(bg=COLOR_TILE_DEFAULT)
            lbl_title.config(bg=COLOR_TILE_DEFAULT)
            lbl_desc.config(bg=COLOR_TILE_DEFAULT)

        def on_click(e):
            command()

        for widget in [tile, lbl_icon, lbl_title, lbl_desc, content]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    # --- GENERATE TILES ---
    
    # 1. Rent a Car
    create_tile(grid_frame, "🚗", "RENT A CAR", "Browse our fleet and\nbook your ride.", 
                lambda: show_rent_car_window(), 0, 0)

    # 2. My Bookings
    create_tile(grid_frame, "📅", "MY BOOKINGS", "View active rentals\nand track status.", 
                lambda: show_my_bookings_window(), 0, 1)

    # 3. Billing
    create_tile(grid_frame, "💳", "BILLING HISTORY", "View invoices and\npayment records.", 
                lambda: show_my_bills_window(), 1, 0)

    # 4. Notifications
    create_tile(grid_frame, "🔔", "NOTIFICATIONS", "Check messages and\nupdates from admin.", 
                lambda: show_notifications_window(), 1, 1)

    # --- FOOTER & LOGOUT ---
    footer_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    footer_frame.pack(side="bottom", fill="x", pady=(0, 30))
    
    # Styled Logout Button (Matches Admin/Employee Dashboard)
    btn_logout = tk.Button(footer_frame, text="LOGOUT", font=("Segoe UI", 12, "bold"), 
                           bg=COLOR_LOGOUT_BG, fg=COLOR_LOGOUT_FG, 
                           activebackground=COLOR_LOGOUT_HOVER, activeforeground=COLOR_LOGOUT_FG,
                           bd=0, cursor="hand2", padx=40, pady=15,
                           command=lambda: logout(root))
    btn_logout.pack()

    # Logout Button Hover Animation
    def on_logout_enter(e):
        btn_logout.config(bg=COLOR_LOGOUT_HOVER)

    def on_logout_leave(e):
        btn_logout.config(bg=COLOR_LOGOUT_BG)

    btn_logout.bind("<Enter>", on_logout_enter)
    btn_logout.bind("<Leave>", on_logout_leave)

    root.mainloop()