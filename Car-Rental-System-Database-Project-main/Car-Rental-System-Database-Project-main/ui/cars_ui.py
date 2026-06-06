import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk  # Requires: pip install pillow
import controllers.car_controller as cc
from app import session
import os

# --- Design Configuration ---
COLOR_BG_MAIN = "#f4f7f6"     # Soft Gray for Right Panel
COLOR_SIDEBAR = "#1c2e4a"     # Dark Navy for Left Panel
COLOR_ACCENT = "#3b82f6"      # Bright Blue (Highlights)
COLOR_WHITE = "#ffffff"
COLOR_TEXT_DARK = "#1e293b"   # Slate 800
COLOR_TEXT_LIGHT = "#64748b"  # Slate 500
COLOR_DANGER = "#ef4444"      # Red

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_VALUE = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 10, "bold")

def show_cars_window(parent=None):
    
    # 1. Hide Dashboard
    if parent:
        parent.withdraw()

    window = tk.Toplevel()
    window.title("Fleet Management - Car Rental System")
    
    # Attempt Full Screen / Zoomed
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
    
    # Left Panel: Sidebar (Navigation & List)
    left_panel = tk.Frame(window, bg=COLOR_SIDEBAR, width=400)
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    # Right Panel: Details & Content
    right_panel = tk.Frame(window, bg=COLOR_BG_MAIN)
    right_panel.pack(side="right", fill="both", expand=True)

    # =========================================================================
    # LEFT PANEL: BACK BUTTON & LIST
    # =========================================================================
    
    # Back Button Container
    back_btn_frame = tk.Frame(left_panel, bg=COLOR_SIDEBAR)
    back_btn_frame.pack(fill="x", padx=20, pady=20)
    
    def btn_back_hover(e):
        btn_back.config(bg="#334155") # Lighter slate
    def btn_back_leave(e):
        btn_back.config(bg=COLOR_SIDEBAR)

    # Back Button
    btn_back = tk.Button(back_btn_frame, text="← Back to Dashboard", font=("Segoe UI", 11), 
                         bg=COLOR_SIDEBAR, fg="white", bd=0, cursor="hand2", anchor="w",
                         activebackground=COLOR_SIDEBAR, activeforeground="white",
                         command=on_close)
    btn_back.pack(fill="x")
    btn_back.bind("<Enter>", btn_back_hover)
    btn_back.bind("<Leave>", btn_back_leave)

    # Separator
    tk.Frame(left_panel, bg="#334155", height=1).pack(fill="x", padx=20, pady=(0, 20))

    # Header
    tk.Label(left_panel, text="Vehicle Fleet", font=("Segoe UI", 20, "bold"), 
             bg=COLOR_SIDEBAR, fg="white").pack(padx=20, anchor="w")
    
    tk.Label(left_panel, text="Select a car to manage details", font=("Segoe UI", 10), 
             bg=COLOR_SIDEBAR, fg="#94a3b8").pack(padx=20, anchor="w", pady=(0, 10))

    # Treeview Styling
    style = ttk.Style()
    style.theme_use("clam")
    
    # Remove borders and make it look clean
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 
    style.configure("Treeview", 
                    background=COLOR_WHITE, fieldbackground=COLOR_WHITE, foreground=COLOR_TEXT_DARK, 
                    rowheight=40, font=("Segoe UI", 11), borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                    background="#f1f5f9", foreground=COLOR_TEXT_DARK, relief="flat")
    style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "white")])

    # Treeview
    columns = ("ID", "Make", "Model", "Reg")
    tree = ttk.Treeview(left_panel, columns=columns, show="headings", selectmode="browse")
    
    tree.heading("ID", text="ID")
    tree.heading("Make", text="Make")
    tree.heading("Model", text="Model")
    tree.heading("Reg", text="Reg #")
    
    tree.column("ID", width=50, anchor="center")
    tree.column("Make", width=100)
    tree.column("Model", width=110)
    tree.column("Reg", width=90)

    # Custom Scrollbar
    scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
    scrollbar.pack(side="right", fill="y", pady=(0, 20), padx=(0, 5))

    # =========================================================================
    # RIGHT PANEL: CONTENT CANVAS
    # =========================================================================
    
    canvas = tk.Canvas(right_panel, bg=COLOR_BG_MAIN, highlightthickness=0)
    v_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
    
    content_frame = tk.Frame(canvas, bg=COLOR_BG_MAIN)
    
    content_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Ensure full width
    def on_canvas_configure(e):
        canvas.itemconfig(canvas_window, width=e.width)
        
    canvas.bind("<Configure>", on_canvas_configure)
    canvas.configure(yscrollcommand=v_scroll.set)

    canvas.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")

    # --- MOUSE WHEEL SCROLLING FIX ---
    def _on_mousewheel(event):
        # Negative delta is standard for scrolling down on Windows
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _bind_mousewheel(event):
        # Bind only when mouse enters the right panel
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def _unbind_mousewheel(event):
        # Unbind when mouse leaves to avoid messing with other scrollables (like treeview)
        canvas.unbind_all("<MouseWheel>")

    # Apply bindings
    right_panel.bind("<Enter>", _bind_mousewheel)
    right_panel.bind("<Leave>", _unbind_mousewheel)


    # =========================================================================
    # DETAIL CARD
    # =========================================================================
    
    # Main Container with Padding
    # Reduced pady from 40 to 20 to prevent content from being pushed too far down
    main_container = tk.Frame(content_frame, bg=COLOR_BG_MAIN)
    main_container.pack(fill="x", padx=40, pady=20)

    # Title
    lbl_header_title = tk.Label(main_container, text="Vehicle Overview", font=FONT_HEADER, 
                                bg=COLOR_BG_MAIN, fg=COLOR_SIDEBAR)
    lbl_header_title.pack(anchor="w", pady=(0, 20))

    # --- CARD SURFACE ---
    card = tk.Frame(main_container, bg=COLOR_WHITE, bd=0)
    card.pack(fill="x", ipadx=0, ipady=0)

    # Top Color Strip
    tk.Frame(card, bg=COLOR_ACCENT, height=4).pack(fill="x")

    # Content Grid inside Card
    # Left: Image, Right: Details
    card_content = tk.Frame(card, bg=COLOR_WHITE, padx=30, pady=30)
    card_content.pack(fill="x")

    # Image Area
    img_container = tk.Frame(card_content, bg="#f8fafc", width=400, height=250, 
                             highlightbackground="#e2e8f0", highlightthickness=1)
    img_container.pack(side="left", anchor="n")
    img_container.pack_propagate(False)
    
    lbl_car_image = tk.Label(img_container, text="No Image", bg="#f8fafc", fg="#94a3b8", font=("Segoe UI", 12))
    lbl_car_image.place(relx=0.5, rely=0.5, anchor="center")

    # Info Area
    info_container = tk.Frame(card_content, bg=COLOR_WHITE)
    info_container.pack(side="left", fill="both", expand=True, padx=(40, 0))

    # Info Grid
    def add_detail_row(parent, label, var_name, row):
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"), bg=COLOR_WHITE, fg="#64748b").grid(row=row, column=0, sticky="w", pady=8)
        tk.Label(parent, textvariable=var_name, font=("Segoe UI", 12), bg=COLOR_WHITE, fg="#334155").grid(row=row, column=1, sticky="w", padx=20, pady=8)

    # Variables
    v_id = tk.StringVar(value="-")
    v_make = tk.StringVar(value="-")
    v_model = tk.StringVar(value="-")
    v_year = tk.StringVar(value="-")
    v_reg = tk.StringVar(value="-")
    v_type = tk.StringVar(value="-")
    v_price = tk.StringVar(value="-")
    v_status = tk.StringVar(value="-")

    info_grid = tk.Frame(info_container, bg=COLOR_WHITE)
    info_grid.pack(anchor="w")

    add_detail_row(info_grid, "MAKE", v_make, 0)
    add_detail_row(info_grid, "MODEL", v_model, 1)
    add_detail_row(info_grid, "YEAR", v_year, 2)
    add_detail_row(info_grid, "TYPE", v_type, 3)
    add_detail_row(info_grid, "REGISTRATION", v_reg, 4)
    
    # Price Tag Style
    tk.Label(info_grid, text="DAILY RATE", font=("Segoe UI", 10, "bold"), bg=COLOR_WHITE, fg="#64748b").grid(row=5, column=0, sticky="w", pady=20)
    lbl_price = tk.Label(info_grid, textvariable=v_price, font=("Segoe UI", 18, "bold"), bg=COLOR_WHITE, fg=COLOR_ACCENT)
    lbl_price.grid(row=5, column=1, sticky="w", padx=20, pady=20)

    # Status Badge
    frame_status = tk.Frame(info_container, bg=COLOR_WHITE)
    frame_status.pack(anchor="w", pady=(10, 0))
    
    lbl_status_badge = tk.Label(frame_status, textvariable=v_status, font=("Segoe UI", 10, "bold"), 
                                bg="#dcfce7", fg="#166534", padx=10, pady=4) # Default Green
    lbl_status_badge.pack(side="left")

    # =========================================================================
    # ADMIN FORM SECTION
    # =========================================================================
    user = session.get_current_user()
    
    if user['role'] == 'Admin':
        
        # Reduced vertical padding from 40 to 20
        form_wrapper = tk.Frame(main_container, bg=COLOR_BG_MAIN)
        form_wrapper.pack(fill="x", pady=20)

        # Header
        tk.Label(form_wrapper, text="Admin Operations", font=FONT_SUBHEADER, 
                 bg=COLOR_BG_MAIN, fg=COLOR_SIDEBAR).pack(anchor="w", pady=(0, 10))

        # Form Card
        form_card = tk.Frame(form_wrapper, bg=COLOR_WHITE, padx=30, pady=30)
        form_card.pack(fill="x")
        
        # Toolbar (Add / Delete)
        toolbar = tk.Frame(form_card, bg=COLOR_WHITE)
        toolbar.pack(fill="x", pady=(0, 20))

        def clear_form_for_add():
            tree.selection_remove(tree.selection())
            v_id.set("New")
            v_make.set("")
            v_model.set("")
            v_year.set("")
            v_reg.set("")
            v_type.set("")
            v_price.set("")
            v_status.set("Available")
            lbl_car_image.config(image="", text="No Image Selected")
            lbl_car_image.image = None
            lbl_status_badge.config(bg="#e2e8f0", fg="#475569") # Grey badge
            
            # Reset Entries
            entry_make.delete(0, tk.END)
            entry_model.delete(0, tk.END)
            entry_year.delete(0, tk.END)
            entry_reg.delete(0, tk.END)
            entry_price.delete(0, tk.END)
            combo_type.current(0)
            selected_image_path.set("")
            lbl_path_hint.config(text="")
            
            lbl_header_title.config(text="Add New Vehicle")
            btn_save.config(text="Save New Vehicle")

        btn_add_new = tk.Button(toolbar, text="+ Add New Car", font=FONT_BTN, 
                                bg=COLOR_ACCENT, fg="white", padx=20, pady=8, bd=0, cursor="hand2",
                                command=clear_form_for_add)
        btn_add_new.pack(side="left")

        def delete_current():
            car_id = v_id.get()
            if not car_id or car_id == "New" or car_id == "-":
                messagebox.showwarning("Warning", "Select a car to delete.")
                return
            if messagebox.askyesno("Confirm", f"Delete Car ID {car_id}?"):
                success, msg = cc.delete_car(car_id)
                if success:
                    refresh_data()
                    clear_form_for_add()
                else:
                    messagebox.showerror("Error", msg)

        btn_delete = tk.Button(toolbar, text="Delete Selected", font=FONT_BTN, 
                               bg="#fee2e2", fg=COLOR_DANGER, padx=20, pady=8, bd=0, cursor="hand2",
                               command=delete_current)
        btn_delete.pack(side="right")

        # Inputs Grid
        inputs_frame = tk.Frame(form_card, bg=COLOR_WHITE)
        inputs_frame.pack(fill="x")

        # Styling Helper
        def create_input(parent, label, row, col, width=25):
            tk.Label(parent, text=label, font=("Segoe UI", 9, "bold"), bg=COLOR_WHITE, fg="#64748b").grid(row=row, column=col, sticky="w", pady=(10, 5))
            entry = tk.Entry(parent, font=("Segoe UI", 10), bg="#f8fafc", bd=1, relief="solid", width=width)
            # Custom border trick usually involves a frame, but standard relief="solid" is okay for now
            entry.config(highlightbackground="#cbd5e1", highlightthickness=1, bd=0)
            entry.grid(row=row+1, column=col, sticky="w", padx=(0, 20), ipady=5)
            return entry

        entry_make = create_input(inputs_frame, "MAKE", 0, 0)
        entry_model = create_input(inputs_frame, "MODEL", 0, 1)
        entry_year = create_input(inputs_frame, "YEAR", 2, 0)
        entry_reg = create_input(inputs_frame, "REGISTRATION NO.", 2, 1)
        
        # Combo for Type
        tk.Label(inputs_frame, text="TYPE", font=("Segoe UI", 9, "bold"), bg=COLOR_WHITE, fg="#64748b").grid(row=4, column=0, sticky="w", pady=(10, 5))
        combo_type = ttk.Combobox(inputs_frame, values=["Sedan", "SUV", "Hatchback", "Truck", "Luxury"], state="readonly", width=23, font=("Segoe UI", 10))
        combo_type.grid(row=5, column=0, sticky="w", padx=(0, 20), ipady=5)
        
        entry_price = create_input(inputs_frame, "DAILY RATE ($)", 4, 1)

        # Image Upload Row
        tk.Label(inputs_frame, text="VEHICLE IMAGE", font=("Segoe UI", 9, "bold"), bg=COLOR_WHITE, fg="#64748b").grid(row=6, column=0, sticky="w", pady=(15, 5))
        
        img_upload_frame = tk.Frame(inputs_frame, bg=COLOR_WHITE)
        img_upload_frame.grid(row=7, column=0, columnspan=2, sticky="w")
        
        selected_image_path = tk.StringVar()
        def browse_image():
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if path:
                selected_image_path.set(path)
                load_image_preview(path)
                lbl_path_hint.config(text="New Image Selected")
        
        btn_upload = tk.Button(img_upload_frame, text="Choose File...", font=("Segoe UI", 9), command=browse_image)
        btn_upload.pack(side="left")
        
        lbl_path_hint = tk.Label(img_upload_frame, text="", font=("Segoe UI", 9, "italic"), bg=COLOR_WHITE, fg="#94a3b8")
        lbl_path_hint.pack(side="left", padx=10)

        # Save Button Area
        def save_data():
            mk = entry_make.get()
            md = entry_model.get()
            yr = entry_year.get()
            rg = entry_reg.get()
            pr = entry_price.get()
            tp = combo_type.get()
            img = selected_image_path.get()
            
            if not mk or not md or not rg or not pr:
                messagebox.showwarning("Missing Info", "Please fill required fields (Make, Model, Reg, Price).")
                return

            current_id = v_id.get()
            
            if current_id == "New" or current_id == "-":
                success, msg = cc.add_car(mk, md, yr, rg, tp, pr, img)
            else:
                success, msg = cc.update_car(current_id, mk, md, yr, rg, tp, pr, img)

            if success:
                messagebox.showinfo("Success", msg)
                refresh_data()
                if current_id == "New":
                    clear_form_for_add()
            else:
                messagebox.showerror("Error", msg)

        tk.Frame(inputs_frame, height=20, bg=COLOR_WHITE).grid(row=8, column=0) # Spacer
        
        btn_save = tk.Button(inputs_frame, text="Save Changes", font=FONT_BTN, 
                             bg=COLOR_SIDEBAR, fg="white", padx=30, pady=10, bd=0, cursor="hand2",
                             command=save_data)
        btn_save.grid(row=9, column=0, columnspan=2, sticky="w")

    # =========================================================================
    # LOGIC: DATA HANDLING
    # =========================================================================

    def load_image_preview(path):
        try:
            if not path or not os.path.exists(path):
                lbl_car_image.config(image="", text="No Image Available")
                lbl_car_image.image = None
                return

            pil_img = Image.open(path)
            # Smart Resize: Maintain aspect ratio to fit 400x250
            pil_img.thumbnail((400, 250)) 
            img = ImageTk.PhotoImage(pil_img)
            
            lbl_car_image.config(image=img, text="")
            lbl_car_image.image = img
        except Exception:
            lbl_car_image.config(image="", text="Error Loading Image")

    def on_tree_select(event):
        selected = tree.selection()
        if not selected:
            return
        
        values = tree.item(selected, 'values')
        car_id = values[0]
        
        # Find in cache
        selected_car = None
        for car in all_cars_cache:
            if str(car[0]) == str(car_id):
                selected_car = car
                break
        
        if selected_car:
            # Update Variables
            v_id.set(selected_car[0])
            v_make.set(selected_car[1])
            v_model.set(selected_car[2])
            v_year.set(selected_car[3])
            v_reg.set(selected_car[4])
            v_type.set(selected_car[5])
            v_price.set(f"${selected_car[6]}")
            
            status = selected_car[7]
            v_status.set(status)
            
            # Badge Color Logic
            if status == "Available":
                lbl_status_badge.config(bg="#dcfce7", fg="#166534") # Green
            elif status == "Rented":
                lbl_status_badge.config(bg="#dbeafe", fg="#1e40af") # Blue
            elif status == "Maintenance":
                lbl_status_badge.config(bg="#fef9c3", fg="#854d0e") # Yellow
            else:
                lbl_status_badge.config(bg="#f1f5f9", fg="#475569") # Grey

            # Image - UPDATED INDEX TO 9
            img_path = selected_car[9] if len(selected_car) > 9 else ""
            load_image_preview(img_path)

            # Update Edit Form
            if user['role'] == 'Admin':
                lbl_header_title.config(text=f"Details: {selected_car[1]} {selected_car[2]}")
                btn_save.config(text="Update Vehicle")
                
                # Pre-fill
                entry_make.delete(0, tk.END); entry_make.insert(0, selected_car[1])
                entry_model.delete(0, tk.END); entry_model.insert(0, selected_car[2])
                entry_year.delete(0, tk.END); entry_year.insert(0, selected_car[3])
                entry_reg.delete(0, tk.END); entry_reg.insert(0, selected_car[4])
                entry_price.delete(0, tk.END); entry_price.insert(0, selected_car[6])
                combo_type.set(selected_car[5])
                
                # CRITICAL FIX: Empty the new image selection so we don't overwrite existing
                selected_image_path.set("")
                lbl_path_hint.config(text="")

    tree.bind("<<TreeviewSelect>>", on_tree_select)
    
    all_cars_cache = []

    def refresh_data():
        nonlocal all_cars_cache
        for item in tree.get_children():
            tree.delete(item)
            
        all_cars_cache = cc.get_all_cars()
        
        for car in all_cars_cache:
            tree.insert("", tk.END, values=(car[0], car[1], car[2], car[4]))

    refresh_data()

    if user['role'] == 'Admin':
        clear_form_for_add()