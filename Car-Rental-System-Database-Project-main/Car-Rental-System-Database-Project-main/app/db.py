import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'Driver={SQL Server};'
        'Server=localhost\SQLEXPRESS;'
        'Database=CarRentalDB;'
        'Trusted_Connection=yes;'
    )
    return conn