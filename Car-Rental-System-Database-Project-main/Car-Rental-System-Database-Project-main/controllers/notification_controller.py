from app.db import get_connection

def send_notification(cust_id, message):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO Notifications (recipient_customer_id, message, date_sent, status)
        VALUES (?, ?, GETDATE(), 'Unseen')
        """
        cursor.execute(query, (cust_id, message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Notification Error: {e}")
        return False
    finally:
        conn.close()

def get_my_notifications(cust_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT notification_id, message, date_sent, status 
    FROM Notifications 
    WHERE recipient_customer_id = ? 
    ORDER BY date_sent DESC
    """
    cursor.execute(query, (cust_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def mark_as_read(notif_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Notifications SET status='Seen' WHERE notification_id=?", (notif_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()    