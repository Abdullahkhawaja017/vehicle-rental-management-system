import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk # Image handling
import os
import controllers.payment_controller as payc
from datetime import datetime

# --- Design Config ---
COLOR_BG = "#ffffff"
COLOR_HEADER_BG = "#1e293b" # Dark Slate
COLOR_HEADER_TEXT = "#ffffff"
COLOR_ACCENT = "#3b82f6"    # Blue
COLOR_TEXT_MAIN = "#0f172a"
COLOR_TEXT_SUB = "#64748b"
COLOR_SUCCESS = "#10b981"   # Green

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_VALUE = ("Segoe UI", 11)
FONT_TOTAL = ("Segoe UI", 22, "bold")

# Updated arguments to accept full details
def show_bill_popup(parent, bill_data, callback_refresh):
    
    # Unpack Data
    (bill_id, booking_id, make, model, daily_rate, img_path, 
     cust_name, start_date, return_date, total_amount, bill_date, status) = bill_data

    # Create Popup Window
    popup = tk.Toplevel(parent)
    popup.title(f"Invoice #{bill_id}")
    
    # Attempt Full Screen (same as parent)
    try:
        popup.state("zoomed")
    except tk.TclError:
        width = popup.winfo_screenwidth()
        height = popup.winfo_screenheight()
        popup.geometry(f"{width}x{height}")
    
    popup.configure(bg=COLOR_BG)
    popup.transient(parent)
    popup.grab_set()

    # --- Header ---
    header_frame = tk.Frame(popup, bg=COLOR_HEADER_BG, pady=20)
    header_frame.pack(fill="x")
    
    tk.Label(header_frame, text="INVOICE", font=("Segoe UI", 24, "bold"), 
             bg=COLOR_HEADER_BG, fg=COLOR_HEADER_TEXT).pack()
    tk.Label(header_frame, text=f"Ref: INV-{bill_id}-{booking_id} | Date: {bill_date}", 
             font=("Segoe UI", 9), bg=COLOR_HEADER_BG, fg="#94a3b8").pack()

    # --- Scrollable Content (for smaller screens) ---
    canvas = tk.Canvas(popup, bg=COLOR_BG, highlightthickness=0)
    v_scroll = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, bg=COLOR_BG, padx=40, pady=20)
    
    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=v_scroll.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")

    # --- 1. Customer & Booking Info ---
    tk.Label(content, text="Customer Details", font=("Segoe UI", 12, "bold", "underline"), 
             bg=COLOR_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(0, 10))

    info_grid = tk.Frame(content, bg=COLOR_BG)
    info_grid.pack(fill="x", pady=(0, 20))

    def add_row(parent_frame, label, value, r):
        tk.Label(parent_frame, text=label, font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT_SUB).grid(row=r, column=0, sticky="w", pady=5)
        tk.Label(parent_frame, text=value, font=FONT_VALUE, bg=COLOR_BG, fg=COLOR_TEXT_MAIN).grid(row=r, column=1, sticky="w", padx=20, pady=5)

    add_row(info_grid, "Customer Name:", cust_name, 0)
    add_row(info_grid, "Booking Date/Time:", str(start_date), 1)
    add_row(info_grid, "Return Date/Time:", str(return_date), 2)

    # --- 2. Car Image & Details ---
    tk.Label(content, text="Vehicle Information", font=("Segoe UI", 12, "bold", "underline"), 
             bg=COLOR_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(0, 10))

    # Image Handling
    img_frame = tk.Frame(content, bg="#f8fafc", width=300, height=180, highlightbackground="#e2e8f0", highlightthickness=1)
    img_frame.pack(pady=10)
    img_frame.pack_propagate(False)
    
    try:
        if img_path and os.path.exists(img_path):
            load = Image.open(img_path)
            load.thumbnail((280, 160))
            render = ImageTk.PhotoImage(load)
            lbl_img = tk.Label(img_frame, image=render, bg="#f8fafc")
            lbl_img.image = render # Keep reference
            lbl_img.pack(expand=True)
        else:
            tk.Label(img_frame, text="No Image Available", bg="#f8fafc", fg="gray").pack(expand=True)
    except Exception:
        tk.Label(img_frame, text="Image Error", bg="#f8fafc", fg="red").pack(expand=True)

    # Car Details Grid
    car_grid = tk.Frame(content, bg=COLOR_BG)
    car_grid.pack(fill="x", pady=10)
    
    add_row(car_grid, "Vehicle:", f"{make} {model}", 0)
    add_row(car_grid, "Daily Rate:", f"${daily_rate:,.2f}", 1)

    # --- 3. Payment Breakdown ---
    total_frame = tk.Frame(content, bg="#f0fdf4", highlightbackground=COLOR_SUCCESS, highlightthickness=1, padx=20, pady=20)
    total_frame.pack(fill="x", pady=30)

    tk.Label(total_frame, text="TOTAL AMOUNT DUE", font=("Segoe UI", 10, "bold"), bg="#f0fdf4", fg="#15803d").pack()
    tk.Label(total_frame, text=f"${total_amount:,.2f}", font=FONT_TOTAL, bg="#f0fdf4", fg="#166534").pack()

    # --- Actions (Fixed Bottom Bar - Outside Canvas) ---
    action_frame = tk.Frame(popup, bg=COLOR_BG, pady=20, padx=40)
    action_frame.pack(fill="x", side="bottom")

    def confirm_payment():
        success, msg = payc.process_payment(booking_id, total_amount)
        print(f"Payment Result: Success={success}, Message={msg}")  # DEBUG
        if success:
            messagebox.showinfo("Payment Successful", "Thank you! Your payment has been processed.", parent=popup)
            popup.destroy()
            if callback_refresh:
                callback_refresh()
        else:
            messagebox.showerror("Payment Failed", msg, parent=popup)

    btn_pay = tk.Button(action_frame, text="CONFIRM PAYMENT", font=("Segoe UI", 12, "bold"), 
                        bg=COLOR_SUCCESS, fg="white", bd=0, cursor="hand2", pady=15, padx=40,
                        activebackground="#059669", activeforeground="white",
                        command=confirm_payment)
    btn_pay.pack(side="right")