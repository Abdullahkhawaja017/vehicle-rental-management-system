from app.db import get_connection
import controllers.notification_controller as nc  # <--- NEW IMPORT

def create_rental_request(customer_id, car_id, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insert a new request with 'Pending' status
        query = """
        INSERT INTO RentalRequests (customer_id, car_id, rental_start_date, rental_end_date, status)
        VALUES (?, ?, ?, ?, 'Pending')
        """
        cursor.execute(query, (customer_id, car_id, start_date, end_date))
        conn.commit()
        return True, "Request submitted! Waiting for approval."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_my_requests(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch requests specific to this logged-in customer
    # We join with Cars to show the Car Name instead of just ID
    query = """
    SELECT r.request_id, c.make, c.model, r.rental_start_date, r.rental_end_date, r.status
    FROM RentalRequests r
    JOIN Cars c ON r.car_id = c.car_id
    WHERE r.customer_id = ?
    """
    cursor.execute(query, (customer_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_pending_requests():
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch details: Request ID, Customer Name, Car Name, Dates
    query = """
    SELECT r.request_id, cust.name, c.make, c.model, r.rental_start_date, r.rental_end_date, r.status, r.car_id, r.customer_id
    FROM RentalRequests r
    JOIN Customers cust ON r.customer_id = cust.customer_id
    JOIN Cars c ON r.car_id = c.car_id
    WHERE r.status = 'Pending'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def process_approval(request_id, customer_id, car_id, start_date, end_date, employee_id, action):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch authoritative request details (in case caller passed wrong values)
        cursor.execute("SELECT customer_id, car_id, rental_start_date, rental_end_date FROM RentalRequests WHERE request_id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, "Rental request not found."

        req_customer_id, req_car_id, req_start_date, req_end_date = req

        # Prefer using values from the request row
        cust_id = req_customer_id
        car_to_use = req_car_id
        start_dt = req_start_date
        end_dt = req_end_date

        if action == "Approve":
            # 1. Create Booking (use request values)
            query_booking = """
            INSERT INTO Bookings (request_id, customer_id, car_id, rental_start_date, rental_end_date, status, employee_id)
            VALUES (?, ?, ?, ?, ?, 'Active', ?)
            """
            cursor.execute(query_booking, (request_id, cust_id, car_to_use, start_dt, end_dt, employee_id))
            
            # 2. Update Request Status
            cursor.execute("UPDATE RentalRequests SET status = 'Approved' WHERE request_id = ?", (request_id,))
            
            # 3. Update Car Status - try common column names to mark unavailable
            updated = 0
            try:
                cursor.execute("UPDATE Cars SET status = 'Rented' WHERE car_id = ?", (car_to_use,))
                updated = cursor.rowcount
            except Exception:
                updated = 0

            if updated == 0:
                # try alternative column
                try:
                    cursor.execute("UPDATE Cars SET available_status = 'Unavailable' WHERE car_id = ?", (car_to_use,))
                    updated = cursor.rowcount
                except Exception:
                    updated = 0

            if updated == 0:
                # try numeric flag
                try:
                    cursor.execute("UPDATE Cars SET is_available = 0 WHERE car_id = ?", (car_to_use,))
                    updated = cursor.rowcount
                except Exception:
                    # If none of the attempts worked, raise for rollback
                    raise Exception("Failed to mark car as unavailable (no matching column).")

            # 4. SEND NOTIFICATION
            nc.send_notification(cust_id, f"Your rental request for Car ID {car_to_use} has been Approved!")
            msg = "Request Approved! Booking Created."
            
        elif action == "Reject":
            # Update Status
            cursor.execute("UPDATE RentalRequests SET status = 'Rejected' WHERE request_id = ?", (request_id,))
            
            # SEND NOTIFICATION
            nc.send_notification(customer_id, f"Your rental request for Car ID {car_id} was Rejected.")
            
            msg = "Request Rejected."
            
        conn.commit()
        return True, msg
        
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()