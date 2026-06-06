# Global variable to store the currently logged-in user
# Example structure: {"user_id": 1, "username": "Ali", "role": "Customer"}
current_user = None

def set_current_user(user_data):
    global current_user
    current_user = user_data

def get_current_user():
    return current_user

def logout():
    global current_user
    current_user = None