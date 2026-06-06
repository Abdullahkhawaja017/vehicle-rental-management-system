import tkinter as tk
from tkinter import messagebox
from app import session
from ui.bookings_ui import show_bookings_window
from ui.pending_requests_ui import show_pending_requests_window
from ui.employee_returns_ui import show_employee_returns_window
# --- NEW IMPORT HERE ---
from ui.employee_tracking_ui import show_employee_tracking_window

# --- Design Configuration ---
COLOR_BG = "#0f172a"          # Very Dark Slate (Background)
COLOR_CARD = "#ffffff"        # White (Main Surface)
COLOR_SHADOW = "#020617"      # Shadow Color
COLOR_ACCENT = "#f59e0b"      # Amber/Orange (Specific for Employees)

# Tile Colors
COLOR_TILE_DEFAULT = "#f8fafc" 
COLOR_TILE_HOVER = "#fffbeb"   # Light Amber tint on hover
COLOR_TILE_BORDER = "#e2e8f0"  
COLOR_TILE_DISABLED = "#f1f5f9" # Grey for disabled tiles

COLOR_TEXT_DARK = "#1e293b"   
COLOR_TEXT_LIGHT = "#64748b"  
COLOR_TEXT_DISABLED = "#94a3b8"

# Logout Button Colors
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
    from ui.login_ui import show_login_window
    show_login_window()

def show_employee_dashboard():
    root = tk.Tk()
    root.title("Employee Dashboard - Car Rental System")
    
    # --- Full Screen Setup ---
    try:
        root.state("zoomed")
    except tk.TclError:
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}")
        
    root.configure(bg=COLOR_BG)
    
    user = session.get_current_user()
    username = user['username'] if user else "Employee"

    # =========================================================================
    # VISUAL LAYOUT
    # =========================================================================
    
    # 1. DROP SHADOW 
    shadow_frame = tk.Frame(root, bg=COLOR_SHADOW)
    shadow_frame.place(relx=0.5, rely=0.5, anchor="center", width=860, height=640)

    # 2. MAIN CARD 
    hub_frame = tk.Frame(root, bg=COLOR_CARD)
    hub_frame.place(relx=0.5, rely=0.5, anchor="center", width=850, height=630)

    # Decorative Accent Line (Amber for Employees)
    tk.Frame(hub_frame, bg=COLOR_ACCENT, height=6).pack(fill="x")

    # --- Header Section ---
    header_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    header_frame.pack(pady=(50, 30))

    tk.Label(header_frame, text="Employee Workspace", font=FONT_TITLE, 
             bg=COLOR_CARD, fg=COLOR_TEXT_DARK).pack()
    
    tk.Label(header_frame, text=f"Logged in as {username}. Manage requests and returns.", 
             font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT).pack(pady=(5, 0))

    # --- TILE GRID CONTAINER ---
    grid_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    grid_frame.pack(expand=True)

    # --- CUSTOM TILE WIDGET BUILDER ---
    def create_tile(parent, icon, title, desc, command, r, c, state="normal"):
        is_disabled = state == "disabled"
        
        bg_color = COLOR_TILE_DISABLED if is_disabled else COLOR_TILE_DEFAULT
        fg_title = COLOR_TEXT_DISABLED if is_disabled else COLOR_TEXT_DARK
        fg_desc = COLOR_TEXT_DISABLED if is_disabled else COLOR_TEXT_LIGHT
        fg_icon = COLOR_TEXT_DISABLED if is_disabled else COLOR_ACCENT
        cursor = "arrow" if is_disabled else "hand2"

        tile = tk.Frame(parent, bg=bg_color, 
                        highlightbackground=COLOR_TILE_BORDER, highlightthickness=1,
                        cursor=cursor, width=260, height=180)
        tile.grid(row=r, column=c, padx=15, pady=15)
        tile.pack_propagate(False) 
        
        content = tk.Frame(tile, bg=bg_color)
        content.place(relx=0.5, rely=0.5, anchor="center")

        lbl_icon = tk.Label(content, text=icon, font=FONT_TILE_ICON, 
                            bg=bg_color, fg=fg_icon)
        lbl_icon.pack(pady=(0, 10))

        lbl_title = tk.Label(content, text=title, font=FONT_TILE_TITLE, 
                             bg=bg_color, fg=fg_title)
        lbl_title.pack(pady=(0, 5))

        lbl_desc = tk.Label(content, text=desc, font=FONT_TILE_DESC, 
                            bg=bg_color, fg=fg_desc, justify="center")
        lbl_desc.pack()

        # Hover Effects (Only if not disabled)
        if not is_disabled:
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
                if command:
                    command()

            for widget in [tile, lbl_icon, lbl_title, lbl_desc, content]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)

    # --- GENERATE TILES ---
    
    # 1. Pending Requests (Approvals)
    create_tile(grid_frame, "📝", "PENDING REQUESTS", "Review and approve/reject\nbooking requests.", 
                lambda: show_pending_requests_window(), 0, 0)

    # 2. Manage Return Requests
    create_tile(grid_frame, "↩️", "RETURN REQUESTS", "Process vehicle returns\nand finalize bills.", 
                lambda: show_employee_returns_window(), 0, 1)

    # 3. Active Rentals
    create_tile(grid_frame, "🚘", "ALL BOOKINGS", "View history of\nall system bookings.", 
                lambda: show_bookings_window(root), 1, 0)

    # 4. LIVE TRACKING (UPDATED)
    create_tile(grid_frame, "📡", "LIVE FLEET TRACKING", "Monitor active cars,\ndrivers, and deadlines.", 
                lambda: show_employee_tracking_window(), 1, 1, state="normal")

    # --- FOOTER & LOGOUT ---
    footer_frame = tk.Frame(hub_frame, bg=COLOR_CARD)
    footer_frame.pack(side="bottom", fill="x", pady=(0, 30))
    
    # Styled Logout Button
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