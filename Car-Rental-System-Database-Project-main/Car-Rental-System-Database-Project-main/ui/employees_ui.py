import tkinter as tk
from tkinter import ttk, messagebox
import controllers.employee_controller as ec
from app import session

# --- UPDATE: Accept 'parent' argument ---
def show_employees_window(parent=None):
    
    # 1. Hide Dashboard
    if parent:
        parent.withdraw()

    window = tk.Toplevel()
    window.title("Manage Employees")
    window.geometry("800x550")

    # 2. Handle Closing
    def on_close():
        if parent:
            parent.deiconify()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text="Staff Management", font=("Arial", 14, "bold")).pack(pady=10)

    # --- Table ---
    columns = ("ID", "Name", "Email", "Phone", "Username", "Role")
    tree = ttk.Treeview(window, columns=columns, show="headings", height=8)

    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Email", text="Email")
    tree.heading("Phone", text="Phone")
    tree.heading("Username", text="Username")
    tree.heading("Role", text="Role")

    tree.column("ID", width=30)
    tree.column("Name", width=150)
    tree.column("Email", width=150)
    tree.column("Phone", width=100)
    tree.column("Username", width=100)
    tree.column("Role", width=80)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    def refresh_data():
        for item in tree.get_children():
            tree.delete(item)
        emps = ec.get_all_employees()
        for e in emps:
            tree.insert("", tk.END, values=e)

    refresh_data()

    # --- DELETE LOGIC ---
    def delete_selected():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an employee to delete.")
            return

        values = tree.item(selected_item, 'values')
        
        # --- ROBUST ID CLEANING ---
        raw_id = str(values[0])
        clean_id_str = ''.join(filter(str.isdigit, raw_id))
        
        if not clean_id_str:
            messagebox.showerror("Error", f"Could not find a valid ID in: {raw_id}")
            return
            
        emp_id = int(clean_id_str)
        # --------------------------

        emp_name = values[1]
        
        # Prevent deleting yourself
        current_user = session.get_current_user()
        if current_user and str(emp_id) == str(current_user['user_id']):
            messagebox.showerror("Error", "You cannot delete your own account while logged in!")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {emp_name} (ID: {emp_id})?")
        if confirm:
            success, msg = ec.delete_employee(emp_id)
            if success:
                messagebox.showinfo("Success", msg)
                refresh_data()
            else:
                messagebox.showerror("Error", msg)

    # Delete Button
    tk.Button(window, text="❌ Delete Selected Employee", bg="#dc3545", fg="white", command=delete_selected).pack(pady=5)

    # --- Add Employee Form ---
    frame_form = tk.LabelFrame(window, text="Add New Employee")
    frame_form.pack(pady=10, padx=20, fill=tk.X)

    tk.Label(frame_form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    e_name = tk.Entry(frame_form)
    e_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Email:").grid(row=0, column=2, padx=5, pady=5)
    e_email = tk.Entry(frame_form)
    e_email.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_form, text="Phone:").grid(row=1, column=0, padx=5, pady=5)
    e_phone = tk.Entry(frame_form)
    e_phone.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Role:").grid(row=1, column=2, padx=5, pady=5)
    c_role = ttk.Combobox(frame_form, values=["Employee", "Admin"], state="readonly")
    c_role.current(0)
    c_role.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(frame_form, text="Username:").grid(row=2, column=0, padx=5, pady=5)
    e_user = tk.Entry(frame_form)
    e_user.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Password:").grid(row=2, column=2, padx=5, pady=5)
    e_pass = tk.Entry(frame_form, show="*")
    e_pass.grid(row=2, column=3, padx=5, pady=5)

    def submit_employee():
        name = e_name.get()
        user = e_user.get()
        pwd = e_pass.get()
        
        if not name or not user or not pwd:
            messagebox.showwarning("Warning", "Name, Username, and Password are required.")
            return

        success, msg = ec.add_employee(name, e_email.get(), e_phone.get(), user, pwd, c_role.get())
        if success:
            messagebox.showinfo("Success", msg)
            refresh_data()
            e_name.delete(0, tk.END)
            e_user.delete(0, tk.END)
            e_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    tk.Button(frame_form, text="Save Employee", bg="#28a745", fg="white", command=submit_employee).grid(row=3, column=0, columnspan=4, pady=10)

    # 3. Update Close Button
    tk.Button(window, text="Close", command=on_close).pack(pady=5)