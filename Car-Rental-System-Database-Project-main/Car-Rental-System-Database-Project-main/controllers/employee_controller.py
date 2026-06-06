from app.db import get_connection

def get_all_employees():
    # --- REMOVED TRY/EXCEPT BLOCK TO REVEAL ERRORS ---
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, name, email, phone, username, role FROM Employees")
    results = cursor.fetchall()
    conn.close()
    return results

def add_employee(name, email, phone, username, password, role="Employee"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if username exists
        cursor.execute("SELECT 1 FROM Employees WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already taken."

        query = """
        INSERT INTO Employees (name, email, phone, username, password_hash, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, email, phone, username, password, role))
        conn.commit()
        return True, "Employee Added Successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def update_employee(emp_id, name, email, phone, username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check unique username (excluding current employee)
        cursor.execute("SELECT 1 FROM Employees WHERE username = ? AND employee_id != ?", (username, emp_id))
        if cursor.fetchone():
            return False, "Username already taken."

        if password: # If password provided, update it
            query = """
            UPDATE Employees 
            SET name=?, email=?, phone=?, username=?, password_hash=?, role=? 
            WHERE employee_id=?
            """
            cursor.execute(query, (name, email, phone, username, password, role, emp_id))
        else: # Keep old password
            query = """
            UPDATE Employees 
            SET name=?, email=?, phone=?, username=?, role=? 
            WHERE employee_id=?
            """
            cursor.execute(query, (name, email, phone, username, role, emp_id))

        conn.commit()
        return True, "Employee Updated Successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def delete_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Unlink from Bookings
        cursor.execute("UPDATE Bookings SET employee_id = NULL WHERE employee_id = ?", (employee_id,))
        
        # 2. Unlink from Notifications (commented out as per your code)
        # cursor.execute("UPDATE Notifications SET recipient_employee_id = NULL WHERE recipient_employee_id = ?", (employee_id,))
        
        # 3. Attempt Delete
        cursor.execute("DELETE FROM Employees WHERE employee_id = ?", (employee_id,))
        
        # 4. Check if it actually deleted anything
        if cursor.rowcount > 0:
            conn.commit()
            return True, "Employee deleted successfully."
        else:
            conn.rollback()
            return False, "Delete failed: ID not found in database."
            
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()