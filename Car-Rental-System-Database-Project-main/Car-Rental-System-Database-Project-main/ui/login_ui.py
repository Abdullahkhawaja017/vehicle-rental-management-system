import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Requires: pip install pillow
import os

# --- Import Controllers & Session ---
import controllers.auth_controller as auth
from app import session

# --- Mock Dashboard Imports ---
# Ensure these imports match your actual file structure
from ui.dashboards.admin_dashboard import show_admin_dashboard
from ui.dashboards.employee_dashboard import show_employee_dashboard
from ui.dashboards.customer_dashboard import show_customer_dashboard

# --- Colors & Fonts Configuration ---
COLOR_PRIMARY = "#1c2e4a"     # Dark Navy (Sidebar)
COLOR_ACCENT = "#00509d"      # Royal Blue (Buttons)
COLOR_BG = "#ffffff"          # White (Form Background)
COLOR_TEXT = "#333333"        # Dark Grey (Text)
COLOR_LIGHT_GRAY = "#f0f0f0"  # Input Background
COLOR_ERROR = "#e74c3c"       # Red (Error Messages)

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 11)

def open_dashboard():
    """Redirects to the correct dashboard based on the user's role."""
    user = session.get_current_user()
    if user:
        role = user.get("role")
        if role == "Admin":
            show_admin_dashboard()
        elif role == "Employee":
            show_employee_dashboard()
        elif role == "Customer":
            show_customer_dashboard()

def show_login_window():
    root = tk.Tk()
    root.title("Login - Car Rental System")
    
    # --- FULL SCREEN CONFIGURATION ---
    # Attempt to maximize window based on OS
    try:
        root.state("zoomed")  # Windows
    except tk.TclError:
        # Linux/macOS fallback
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}")

    root.configure(bg=COLOR_BG)

    # =========================================================================
    # LEFT SIDE: Branding Panel
    # =========================================================================
    left_frame = tk.Frame(root, bg=COLOR_PRIMARY, width=500) # Slightly wider for the image
    left_frame.pack(side="left", fill="y")
    left_frame.pack_propagate(False)

    # Container to vertically center everything in the sidebar
    branding_container = tk.Frame(left_frame, bg=COLOR_PRIMARY)
    branding_container.place(relx=0.5, rely=0.5, anchor="center")

    # 1. Title
    tk.Label(branding_container, text="Car Rental\nSystem", font=("Segoe UI", 36, "bold"), 
             bg=COLOR_PRIMARY, fg="white", justify="center").pack(pady=(0, 30))
    
    # 2. Image Integration
    # We load the image, resize it to fit the sidebar, and display it.
    image_path = "assets/cars/Cars.png"
    
    try:
        # Load the image using Pillow
        original_img = Image.open(image_path)
        
        # Calculate aspect ratio to fit width of 400px
        base_width = 400
        w_percent = (base_width / float(original_img.size[0]))
        h_size = int((float(original_img.size[1]) * float(w_percent)))
        
        # Resize nicely using LANCZOS (high quality downsampling)
        resized_img = original_img.resize((base_width, h_size), Image.Resampling.LANCZOS)
        photo_img = ImageTk.PhotoImage(resized_img)
        
        # Display Image
        img_label = tk.Label(branding_container, image=photo_img, bg=COLOR_PRIMARY)
        img_label.image = photo_img  # Keep a reference! Important for Tkinter
        img_label.pack(pady=20)
        
    except Exception as e:
        print(f"Error loading image: {e}")
        # Fallback if image not found: Just show text
        tk.Label(branding_container, text="[Image Not Found]", bg=COLOR_PRIMARY, fg="gray").pack(pady=20)

    # 3. Slogan
    tk.Label(branding_container, text="Drive your dreams.\nPremium service for premium people.", 
             font=("Segoe UI", 14), bg=COLOR_PRIMARY, fg="#d1d1d1", justify="center").pack(pady=(30, 0))

    # =========================================================================
    # RIGHT SIDE: Login Form
    # =========================================================================
    right_frame = tk.Frame(root, bg=COLOR_BG)
    right_frame.pack(side="right", fill="both", expand=True)

    # Center Container for Form
    form_container = tk.Frame(right_frame, bg=COLOR_BG)
    form_container.place(relx=0.5, rely=0.5, anchor="center")

    # Header
    tk.Label(form_container, text="Welcome Back", font=FONT_HEADER, bg=COLOR_BG, fg=COLOR_PRIMARY).pack(pady=(0, 5))
    tk.Label(form_container, text="Please login to your account", font=("Segoe UI", 11), bg=COLOR_BG, fg="gray").pack(pady=(0, 40))

    # --- Helper: Styled Entry Field ---
    def create_styled_entry(parent, label_text, is_password=False):
        tk.Label(parent, text=label_text, font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", pady=(10, 0))
        
        entry_frame = tk.Frame(parent, bg=COLOR_LIGHT_GRAY, bd=0, highlightbackground="#cccccc", highlightthickness=1)
        entry_frame.pack(fill="x", pady=5, ipady=8) 
        
        entry = tk.Entry(entry_frame, font=FONT_BODY, bg=COLOR_LIGHT_GRAY, bd=0, show="*" if is_password else "")
        entry.pack(fill="both", padx=10)
        return entry

    entry_user = create_styled_entry(form_container, "USERNAME")
    entry_pass = create_styled_entry(form_container, "PASSWORD", is_password=True)

    # Role Selection
    tk.Label(form_container, text="SELECT ROLE", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", pady=(15, 0))
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TCombobox", fieldbackground=COLOR_LIGHT_GRAY, background=COLOR_BG)
    
    combo_role = ttk.Combobox(form_container, values=["Customer", "Employee", "Admin"], state="readonly", font=FONT_BODY)
    combo_role.current(0)
    combo_role.pack(fill="x", pady=5, ipady=6)

    # --- ERROR LABEL (Hidden by default) ---
    lbl_error = tk.Label(form_container, text="", font=("Segoe UI", 10), fg=COLOR_ERROR, bg=COLOR_BG)
    lbl_error.pack(pady=(15, 0))

    # --- Login Logic ---
    def perform_login():
        # Clear previous error
        lbl_error.config(text="")
        
        user = entry_user.get()
        pwd = entry_pass.get()
        role = combo_role.get()
        
        if not user or not pwd:
            lbl_error.config(text="⚠ Please fill in all fields")
            return

        # Attempt Login
        success, message = auth.login_user(user, pwd, role)
        
        if success:
            root.destroy()
            open_dashboard()
        else:
            # Display error in red on the screen
            lbl_error.config(text=f"⚠ {message}")

    # Login Button
    btn_login = tk.Button(form_container, text="LOGIN", font=("Segoe UI", 12, "bold"), 
                          bg=COLOR_ACCENT, fg="white", activebackground="#003f7f", activeforeground="white",
                          bd=0, cursor="hand2", width=35, command=perform_login)
    btn_login.pack(pady=20, ipady=8)

    # --- Registration Section ---
    def open_register_popup():
        reg_win = tk.Toplevel(root)
        reg_win.title("Create Account")
        reg_win.geometry("450x700")
        reg_win.configure(bg=COLOR_BG)
        
        tk.Label(reg_win, text="Create Account", font=FONT_HEADER, bg=COLOR_BG, fg=COLOR_PRIMARY).pack(pady=20)
        
        reg_frame = tk.Frame(reg_win, bg=COLOR_BG)
        reg_frame.pack(padx=50, fill="both")

        def mk_entry(lbl):
            tk.Label(reg_frame, text=lbl, font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg="gray").pack(anchor="w", pady=(5,0))
            e = tk.Entry(reg_frame, font=("Segoe UI", 10), bg=COLOR_LIGHT_GRAY, bd=0, relief="flat")
            e.pack(fill="x", pady=2, ipady=5)
            return e

        e_name = mk_entry("Full Name")
        e_email = mk_entry("Email")
        e_phone = mk_entry("Phone")
        e_addr = mk_entry("Address")
        e_lic = mk_entry("Driver License")
        e_user = mk_entry("Username")
        
        tk.Label(reg_frame, text="Password", font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg="gray").pack(anchor="w", pady=(5,0))
        e_pass = tk.Entry(reg_frame, font=("Segoe UI", 10), bg=COLOR_LIGHT_GRAY, bd=0, relief="flat", show="*")
        e_pass.pack(fill="x", pady=2, ipady=5)

        def submit_register():
            success, msg = auth.register_customer(
                e_name.get(), e_email.get(), e_phone.get(), 
                e_addr.get(), e_lic.get(), e_user.get(), e_pass.get()
            )
            if success:
                messagebox.showinfo("Success", msg)
                reg_win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(reg_win, text="REGISTER", bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, cursor="hand2", command=submit_register).pack(pady=30, ipadx=20, ipady=8)

    footer_frame = tk.Frame(form_container, bg=COLOR_BG)
    footer_frame.pack(pady=10)
    
    tk.Label(footer_frame, text="New Customer?", font=("Segoe UI", 10), bg=COLOR_BG, fg="gray").pack(side="left")
    tk.Button(footer_frame, text="Create Account", font=("Segoe UI", 10, "bold"), 
              bg=COLOR_BG, fg=COLOR_ACCENT, bd=0, cursor="hand2", 
              activebackground=COLOR_BG, activeforeground=COLOR_PRIMARY,
              command=open_register_popup).pack(side="left", padx=5)

    root.mainloop()