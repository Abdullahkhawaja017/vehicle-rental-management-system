import tkinter as tk
from tkinter import ttk
from controllers.employee_tracking_controller import get_live_tracking_data

def show_employee_tracking_window():
    window = tk.Toplevel()
    window.title("Live Fleet Tracking")
    
    # --- Full Screen Setup ---
    try:
        window.state("zoomed")
    except tk.TclError:
        # Fallback for systems where 'zoomed' isn't supported
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        window.geometry(f"{width}x{height}")

    window.configure(bg="#0f172a") # Dark background

    # --- Header ---
    lbl_title = tk.Label(window, text="Live Fleet Tracking", font=("Segoe UI", 20, "bold"), 
                         bg="#0f172a", fg="white")
    lbl_title.pack(pady=(40, 20)) # Increased top padding slightly for full screen balance

    # --- Table Frame ---
    frame_table = tk.Frame(window, bg="#0f172a")
    frame_table.pack(fill="both", expand=True, padx=40, pady=(0, 40)) # More padding for full screen

    # --- Treeview Styles ---
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                    background="white", 
                    foreground="#1e293b", 
                    fieldbackground="white", 
                    rowheight=35, # Slightly taller rows for readability on big screen
                    font=("Segoe UI", 11))
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#e2e8f0")
    style.map("Treeview", background=[('selected', '#f59e0b')]) # Amber selection

    # --- Columns ---
    columns = ("id", "customer", "phone", "car", "reg", "start", "end", "days")
    tree = ttk.Treeview(frame_table, columns=columns, show="headings")

    # Define Headings
    tree.heading("id", text="ID")
    tree.heading("customer", text="Customer Name")
    tree.heading("phone", text="Phone")
    tree.heading("car", text="Vehicle")
    tree.heading("reg", text="Reg No")
    tree.heading("start", text="Start Date")
    tree.heading("end", text="Return Due")
    tree.heading("days", text="Status")

    # Define Columns Width (Adjusted for full screen)
    tree.column("id", width=60, anchor="center")
    tree.column("customer", width=200)
    tree.column("phone", width=150)
    tree.column("car", width=200)
    tree.column("reg", width=120)
    tree.column("start", width=140)
    tree.column("end", width=140)
    tree.column("days", width=150, anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    # --- Load Data ---
    data = get_live_tracking_data()

    # Define tags for coloring
    tree.tag_configure("overdue", foreground="#e11d48", font=("Segoe UI", 11, "bold")) # Red & Bold for emphasis
    tree.tag_configure("safe", foreground="#1e293b")    # Normal text

    for item in data:
        # Calculate visual status
        days_left = item["Days Left"]
        status_text = f"{days_left} Days Left"
        
        tag = "safe"
        if days_left < 0:
            status_text = f"OVERDUE ({abs(days_left)} days)"
            tag = "overdue"
        elif days_left == 0:
            status_text = "Due Today"
            tag = "overdue" # Make today urgent too

        tree.insert("", "end", values=(
            item["Booking ID"],
            item["Customer"],
            item["Phone"],
            item["Car Info"],
            item["Reg No"],
            str(item["Start Date"])[:10], # Truncate time
            str(item["Return Due"])[:10],
            status_text
        ), tags=(tag,))

    # Close button
    btn_close = tk.Button(window, text="Close", command=window.destroy, 
                          bg="#f59e0b", fg="white", font=("Segoe UI", 12, "bold"), padx=30, pady=10, bd=0)
    btn_close.pack(pady=20)