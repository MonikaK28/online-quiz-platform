import re
from database import add_user, login_user

def is_valid_email(email):
    """Validates email format."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def register_user(username, email, password, confirm_password):
    """Validates inputs and registers a new user."""
    if not username or not email or not password:
        return False, "All fields are required."
    
    if not is_valid_email(email):
        return False, "Invalid email format."
        
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    if password != confirm_password:
        return False, "Passwords do not match."
        
    return add_user(username, email, password)

def authenticate_user(username_or_email, password):
    """Authenticates a user logging in."""
    if not username_or_email or not password:
        return False, "Please enter both username/email and password."
        
    return login_user(username_or_email, password)