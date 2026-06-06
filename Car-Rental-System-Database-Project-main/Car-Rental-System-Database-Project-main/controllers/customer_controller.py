from app.db import get_connection

def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    results = cursor.fetchall()
    conn.close()
    return results