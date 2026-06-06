from app.db import get_connection

# For Admin: View every bill in the system
def get_all_bills():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bills")
    results = cursor.fetchall()
    conn.close()
    return results

# For Customers: View only their own bills with FULL details
def get_my_bills(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch bills linked to bookings for this specific customer
    # We join with Cars to show the Car Name (Make/Model) to the user
    query = """
    SELECT b.bill_id, bk.booking_id, c.make, c.model, b.total_amount, b.billing_date, b.paid_status
    FROM Bills b
    JOIN Bookings bk ON b.booking_id = bk.booking_id
    JOIN Cars c ON bk.car_id = c.car_id
    WHERE bk.customer_id = ?
    """
    cursor.execute(query, (customer_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_bill_details(bill_id):
    """
    Fetch complete bill details for popup display.
    Returns: (bill_id, booking_id, make, model, daily_rate, img_path, 
              cust_name, start_date, return_date, total_amount, bill_date, status)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        b.bill_id, 
        bk.booking_id, 
        c.make, 
        c.model, 
        c.price_per_day,
        c.image_path,
        cust.name,
        bk.rental_start_date, 
        bk.actual_return_date,
        b.total_amount, 
        b.billing_date, 
        b.paid_status
    FROM Bills b
    JOIN Bookings bk ON b.booking_id = bk.booking_id
    JOIN Cars c ON bk.car_id = c.car_id
    JOIN Customers cust ON bk.customer_id = cust.customer_id
    WHERE b.bill_id = ?
    """
    cursor.execute(query, (bill_id,))
    result = cursor.fetchone()
    conn.close()
    return result