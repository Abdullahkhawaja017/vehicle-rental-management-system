from app.db import get_connection

def process_payment(booking_id, amount):
    """
    Process payment for a booking.
    - Update bill status to Paid
    - Update car availability status
    Returns: (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get the bill_id and car_id from booking
        cursor.execute("""
            SELECT b.bill_id, bk.car_id 
            FROM Bills b 
            JOIN Bookings bk ON b.booking_id = bk.booking_id 
            WHERE bk.booking_id = ?
        """, (booking_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Booking not found."
        
        bill_id, car_id = result
        
        # Update bill status to Paid
        cursor.execute("""
            UPDATE Bills 
            SET paid_status = 'Paid' 
            WHERE bill_id = ?
        """, (bill_id,))
        
        # Make car available
        cursor.execute("""
            UPDATE Cars 
            SET status = 'Available' 
            WHERE car_id = ?
        """, (car_id,))
        
        conn.commit()
        return True, "Payment processed successfully!"
    
    except Exception as e:
        conn.rollback()
        print(f"Payment Error: {str(e)}")
        return False, f"Payment failed: {str(e)}"
    finally:
        conn.close()

def get_all_payments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Payments")
    results = cursor.fetchall()
    conn.close()
    return results