from app.db import get_connection
from app import session

# --- HARDCODED ADMIN CREDENTIALS ---
ADMIN_USER = "a"
ADMIN_PASS = "1"

def login_user(username, password, role):
    # 1. ADMIN LOGIN
    if role == "Admin":
        # First, check the Hardcoded Admin
        if username == ADMIN_USER and password == ADMIN_PASS:
            session.set_current_user({"user_id": 0, "username": "Administrator", "role": "Admin"})
            return True, "Welcome, System Admin!"
        
        # If not hardcoded, check the Database for Admin users
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT employee_id, name FROM Employees WHERE username=? AND password_hash=? AND role='Admin'"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            session.set_current_user({"user_id": result[0], "username": result[1], "role": "Admin"})
            return True, f"Welcome Admin, {result[1]}!"
        else:
            return False, "Invalid Admin Credentials"

    # 2. EMPLOYEE LOGIN
    elif role == "Employee":
        conn = get_connection()
        cursor = conn.cursor()
        # Query matching username, password, AND role='Employee'
        query = "SELECT employee_id, name FROM Employees WHERE username=? AND password_hash=? AND role='Employee'"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            session.set_current_user({"user_id": result[0], "username": result[1], "role": "Employee"})
            return True, f"Welcome, {result[1]}!"
        else:
            return False, "Invalid Employee Credentials"

    # 3. CUSTOMER LOGIN
    elif role == "Customer":
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT customer_id, name FROM Customers WHERE username=? AND password_hash=?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            session.set_current_user({"user_id": result[0], "username": result[1], "role": "Customer"})
            return True, f"Welcome, {result[1]}!"
        else:
            return False, "Invalid Customer Credentials"
            
    return False, "Please select a valid role."

def register_customer(name, email, phone, address, license_num, username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if username already exists
        cursor.execute("SELECT 1 FROM Customers WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already taken."

        # Insert new customer
        query = """
        INSERT INTO Customers (name, email, phone, address, driver_license, username, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, email, phone, address, license_num, username, password))
        conn.commit()
        return True, "Account Created! You can now login."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()