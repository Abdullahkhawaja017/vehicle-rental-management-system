from app.db import get_connection

def get_live_tracking_data():
    """
    JOINS: Bookings + Cars + Customers
    PURPOSE: Returns a list of all currently active rentals for the Employee Dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # SQL Logic:
    # 1. Start with Bookings (b) to find active rentals.
    # 2. JOIN Cars (c) to get vehicle details (Make, Model, Reg No).
    # 3. JOIN Customers (cust) to get driver details (Name, Phone).
    query = """
    SELECT 
        b.booking_id,
        cust.name AS customer_name,
        cust.phone AS customer_phone,
        c.make,
        c.model,
        c.registration_number,
        b.rental_start_date,
        b.rental_end_date,
        DATEDIFF(day, GETDATE(), b.rental_end_date) AS days_remaining
    FROM Bookings b
    INNER JOIN Cars c ON b.car_id = c.car_id
    INNER JOIN Customers cust ON b.customer_id = cust.customer_id
    WHERE b.status = 'Active'
    ORDER BY b.rental_end_date ASC;
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert raw SQL rows into a clean list of dictionaries
        tracking_list = []
        for row in rows:
            tracking_list.append({
                "Booking ID": row[0],
                "Customer": row[1],
                "Phone": row[2],
                "Car Info": f"{row[3]} {row[4]}",  # e.g., Toyota Corolla
                "Reg No": row[5],
                "Start Date": row[6],
                "Return Due": row[7],
                "Days Left": row[8]  # Positive = safe, Negative = overdue
            })
            
        return tracking_list

    except Exception as e:
        print(f"Error fetching live tracking data: {e}")
        return []
    finally:
        conn.close()