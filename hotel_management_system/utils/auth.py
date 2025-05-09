from functools import wraps
from flask import request, redirect, url_for, flash, session, g
import sqlite3
import hashlib

def get_db():
    """Connect to the database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('hotel.db')
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    """Query the database."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def close_db(exception):
    """Close the database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def hash_password(password):
    """Hash a password for storing."""
    # In a production environment, use a more secure hashing method like bcrypt
    # This is a simple SHA-256 hash for demonstration purposes
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against a provided password."""
    return stored_password == hash_password(provided_password)

def login_user(username, password):
    """Attempt to log in a user."""
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    
    if user and verify_password(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return True, user
    return False, None

def register_user(username, password, email, role='user'):
    """Register a new user."""
    # Check if username already exists
    existing_user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if existing_user:
        return False, "Username already exists"
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Insert the new user
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (username, hashed_password, email, role)
        )
        db.commit()
        return True, "Registration successful"
    except sqlite3.Error as e:
        return False, str(e)

def logout_user():
    """Log out the current user."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)

def is_logged_in():
    """Check if a user is logged in."""
    return 'user_id' in session

def get_current_user():
    """Get the current logged-in user."""
    if not is_logged_in():
        return None
    
    user_id = session.get('user_id')
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    return user

def is_admin():
    """Check if the current user is an admin."""
    return is_logged_in() and session.get('role') == 'admin'

def admin_required(f):
    """Decorator to require admin access for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or session.get('role') != 'admin':
            flash('You need to be logged in as admin to access this page.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or session.get('role') != 'user':
            flash('You need to be logged in to access this page.')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

def has_guest_profile(user_id):
    """Check if a user has a guest profile."""
    guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)
    return guest is not None

def create_guest_profile(user_id, name, phone, address):
    """Create a guest profile for a user."""
    db = get_db()
    try:
        db.execute(
            'INSERT INTO guests (user_id, name, phone, address) VALUES (?, ?, ?, ?)',
            (user_id, name, phone, address)
        )
        db.commit()
        return True, "Profile created successfully"
    except sqlite3.Error as e:
        return False, str(e)

def get_guest_profile(user_id):
    """Get the guest profile for a user."""
    return query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)