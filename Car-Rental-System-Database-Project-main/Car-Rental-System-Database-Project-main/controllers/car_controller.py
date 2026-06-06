from app.db import get_connection
import shutil
import os
import re # <--- Import Regex to clean filenames

# Define where images are stored
IMAGE_DIR = "assets/cars/"

def clean_filename(filename):
    """Removes illegal characters from filenames (like : / \ *)"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_all_cars():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cars")
    results = cursor.fetchall()
    conn.close()
    return results

# --- FILTER FUNCTIONS ---
def get_distinct_makes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT make FROM Cars WHERE status = 'Available'")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def search_cars(make=None, car_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Cars WHERE status = 'Available'"
    params = []
    
    if make and make != "All":
        query += " AND make = ?"
        params.append(make)
    if car_type and car_type != "All":
        query += " AND type = ?"
        params.append(car_type)
        
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()
    return results

# --- ADMIN FUNCTIONS ---

def add_car(make, model, year, reg_num, car_type, price, image_source_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if Registration Number already exists
        cursor.execute("SELECT 1 FROM Cars WHERE registration_number = ?", (reg_num,))
        if cursor.fetchone():
            return False, "Registration Number already exists."

        # Handle Image
        final_image_path = None
        if image_source_path:
            if not os.path.exists(IMAGE_DIR):
                os.makedirs(IMAGE_DIR)
            
            # Create safe filename
            safe_reg_num = clean_filename(str(reg_num))
            extension = image_source_path.split('.')[-1]
            new_filename = f"{safe_reg_num}.{extension}"
            destination = os.path.join(IMAGE_DIR, new_filename)
            
            shutil.copy(image_source_path, destination)
            final_image_path = destination

        query = """
        INSERT INTO Cars (make, model, year, registration_number, type, price_per_day, status, image_path)
        VALUES (?, ?, ?, ?, ?, ?, 'Available', ?)
        """
        cursor.execute(query, (make, model, year, reg_num, car_type, price, final_image_path))
        conn.commit()
        return True, "Car Added Successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def update_car(car_id, make, model, year, reg_num, car_type, price, image_source_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Ensure ID is an integer
        car_id = int(car_id)

        # Check uniqueness of Reg Num (excluding current car)
        cursor.execute("SELECT 1 FROM Cars WHERE registration_number = ? AND car_id != ?", (reg_num, car_id))
        if cursor.fetchone():
            return False, "Registration Number exists for another car."

        # Handle Image Update
        final_image_path = None
        if image_source_path:
            if not os.path.exists(IMAGE_DIR):
                os.makedirs(IMAGE_DIR)
            
            # Create safe filename
            safe_reg_num = clean_filename(str(reg_num))
            extension = image_source_path.split('.')[-1]
            new_filename = f"{safe_reg_num}.{extension}"
            destination = os.path.join(IMAGE_DIR, new_filename)
            
            shutil.copy(image_source_path, destination)
            final_image_path = destination

        if final_image_path:
            # Update Everything + Image
            query = """
            UPDATE Cars 
            SET make=?, model=?, year=?, registration_number=?, type=?, price_per_day=?, image_path=?
            WHERE car_id=?
            """
            cursor.execute(query, (make, model, year, reg_num, car_type, price, final_image_path, car_id))
        else:
            # Update Everything EXCEPT Image
            query = """
            UPDATE Cars 
            SET make=?, model=?, year=?, registration_number=?, type=?, price_per_day=?
            WHERE car_id=?
            """
            cursor.execute(query, (make, model, year, reg_num, car_type, price, car_id))

        conn.commit()
        return True, "Car Updated Successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()

def delete_car(car_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Prevent delete if Rented
        cursor.execute("SELECT status FROM Cars WHERE car_id = ?", (car_id,))
        result = cursor.fetchone()
        if result and result[0] == 'Rented':
            return False, "Cannot delete a car that is currently Rented."

        # Unlink history (preservation)
        cursor.execute("UPDATE Bookings SET car_id = NULL WHERE car_id = ?", (car_id,))
        cursor.execute("UPDATE RentalRequests SET car_id = NULL WHERE car_id = ?", (car_id,))
        
        cursor.execute("DELETE FROM Cars WHERE car_id = ?", (car_id,))
        conn.commit()
        return True, "Car Deleted."
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        conn.close()