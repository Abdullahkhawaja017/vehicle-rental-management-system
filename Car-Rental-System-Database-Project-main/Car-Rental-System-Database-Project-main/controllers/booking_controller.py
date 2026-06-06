from app.db import get_connection
from datetime import datetime

def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bookings")
    results = cursor.fetchall()
    conn.close()
    return results

# Used for manual bookings (Admin/Employee side)
def add_booking(customer_id, car_id, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert the new booking
        query = """
        INSERT INTO Bookings (customer_id, car_id, rental_start_date, rental_end_date, status)
        VALUES (?, ?, ?, ?, 'Active')
        """
        cursor.execute(query, (customer_id, car_id, start_date, end_date))
        
        # 2. Update the car status to 'Rented'
        cursor.execute("UPDATE Cars SET status = 'Rented' WHERE car_id = ?", (car_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding booking: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Used for processing returns and generating bills
def process_return(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Get Booking Details (Dates, Car ID) and Car Price
        query = """
        SELECT b.rental_start_date, b.car_id, c.price_per_day 
        FROM Bookings b
        JOIN Cars c ON b.car_id = c.car_id
        WHERE b.booking_id = ?
        """
        cursor.execute(query, (booking_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Booking not found."
            
        start_str, car_id, price_per_day = result
        
        # 2. Calculate Bill
        # Note: We parse the string from SQL to a Python datetime object
        # The split('.')[0] removes milliseconds if they exist
        start_date = datetime.strptime(str(start_str).split('.')[0], '%Y-%m-%d %H:%M:%S') 
        end_date = datetime.now() 
        
        # Calculate difference in days
        days = (end_date - start_date).days
        if days < 1: days = 1 # Minimum charge is 1 day
        
        total_amount = days * float(price_per_day)
        
        # 3. Update Booking Status to 'Completed'
        cursor.execute("UPDATE Bookings SET status='Completed', actual_return_date=? WHERE booking_id=?", (end_date, booking_id))
        
        # 4. Make Car Available again
        cursor.execute("UPDATE Cars SET status='Available' WHERE car_id=?", (car_id,))
        
        # 5. Generate the Bill
        cursor.execute("INSERT INTO Bills (booking_id, total_amount, paid_status) VALUES (?, ?, 'Unpaid')", (booking_id, total_amount))
        
        conn.commit()
        return True, f"Car Returned! Total Bill: ${total_amount:.2f}"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_my_bookings(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Join with Cars to show the Car Name (Make/Model) instead of just ID
    query = """
    SELECT b.booking_id, c.make, c.model, b.rental_start_date, b.rental_end_date, b.status, b.actual_return_date
    FROM Bookings b
    JOIN Cars c ON b.car_id = c.car_id
    WHERE b.customer_id = ?
    ORDER BY b.rental_start_date DESC
    """
    cursor.execute(query, (customer_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def request_return_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Update status to signal that customer wants to return
        cursor.execute("UPDATE Bookings SET status = 'ReturnRequested' WHERE booking_id = ?", (booking_id,))
        conn.commit()
        return True, "Return request sent! Waiting for employee approval."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_return_requests():
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch bookings where the status is 'ReturnRequested'
    query = """
    SELECT b.booking_id, cust.name, c.make, c.model, b.rental_start_date, b.rental_end_date
    FROM Bookings b
    JOIN Customers cust ON b.customer_id = cust.customer_id
    JOIN Cars c ON b.car_id = c.car_id
    WHERE b.status = 'ReturnRequested'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results