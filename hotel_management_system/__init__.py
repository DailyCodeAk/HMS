import os
from flask import Flask, render_template, redirect, url_for, g
import sqlite3
from datetime import datetime

def get_db():
    """Connect to the database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database."""
    db = get_db()
    
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def create_app(test_config=None):
    """Create and configure the application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='walnutmercury_hotel_system',  # Change this in production!
        DATABASE=os.path.join(app.instance_path, 'hotel.db'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Register database functions
    app.teardown_appcontext(close_db)
    
    # Store the current app in the module for imports
    global current_app
    current_app = app

    # Register blueprints
    from .utils.auth import auth_bp
    from .utils.admin_utils import admin_bp
    from .utils.user_utils import user_bp
    from .utils.food import food_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(food_bp)

    # Add url rules for the root route
    @app.route('/')
    def index():
        """Render the home page."""
        return render_template('index.html')

    # Initialize database if it doesn't exist
    db_path = app.config['DATABASE']
    db_exists = os.path.exists(db_path)
    
    with app.app_context():
        if not db_exists:
            init_db()
            create_default_data()

    return app

def create_default_data():
    """Create default data in the database."""
    from .utils.auth import register_user
    from .utils.db import insert_db
    
    # Create default admin user
    register_user('admin', 'admin123', 'admin@hotel.com', 'admin')
    
    # Create sample rooms
    rooms = [
        {'room_number': '101', 'type': 'Standard', 'price': 99.99, 'capacity': 2, 'status': 'available'},
        {'room_number': '102', 'type': 'Standard', 'price': 99.99, 'capacity': 2, 'status': 'available'},
        {'room_number': '103', 'type': 'Standard', 'price': 99.99, 'capacity': 2, 'status': 'available'},
        {'room_number': '201', 'type': 'Deluxe', 'price': 149.99, 'capacity': 2, 'status': 'available'},
        {'room_number': '202', 'type': 'Deluxe', 'price': 149.99, 'capacity': 2, 'status': 'available'},
        {'room_number': '301', 'type': 'Suite', 'price': 249.99, 'capacity': 4, 'status': 'available'},
        {'room_number': '302', 'type': 'Suite', 'price': 249.99, 'capacity': 4, 'status': 'available'},
    ]
    
    for room in rooms:
        insert_db('rooms', room)
    
    # Create sample inventory items
    inventory_items = [
        {'item_name': 'Towels', 'quantity': 100, 'category': 'Housekeeping'},
        {'item_name': 'Shampoo', 'quantity': 80, 'category': 'Amenities'},
        {'item_name': 'Soap', 'quantity': 120, 'category': 'Amenities'},
        {'item_name': 'Toilet Paper', 'quantity': 150, 'category': 'Housekeeping'},
        {'item_name': 'Bed Sheets', 'quantity': 50, 'category': 'Housekeeping'},
        {'item_name': 'Coffee', 'quantity': 30, 'category': 'Food'},
        {'item_name': 'Tea', 'quantity': 25, 'category': 'Food'},
        {'item_name': 'Wine Bottles', 'quantity': 40, 'category': 'Beverages'},
        {'item_name': 'Beer', 'quantity': 60, 'category': 'Beverages'},
    ]
    
    for item in inventory_items:
        item['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_db('inventory', item)
    
    # Create sample employees
    employees = [
        {'name': 'John Smith', 'position': 'Manager', 'department': 'Management', 'contact': '555-1234'},
        {'name': 'Jane Doe', 'position': 'Receptionist', 'department': 'Front Desk', 'contact': '555-5678'},
        {'name': 'Robert Johnson', 'position': 'Housekeeper', 'department': 'Housekeeping', 'contact': '555-9012'},
        {'name': 'Mary Williams', 'position': 'Housekeeper', 'department': 'Housekeeping', 'contact': '555-3456'},
        {'name': 'James Brown', 'position': 'Chef', 'department': 'Food Service', 'contact': '555-7890'},
        {'name': 'Patricia Davis', 'position': 'Maintenance', 'department': 'Maintenance', 'contact': '555-2345'},
        {'name': 'Michael Wilson', 'position': 'Waiter', 'department': 'Food Service', 'contact': '555-6789'},
        {'name': 'Elizabeth Taylor', 'position': 'Room Service', 'department': 'Food Service', 'contact': '555-0123'},
    ]
    
    for employee in employees:
        employee['hire_date'] = datetime.now().strftime('%Y-%m-%d')
        insert_db('employees', employee)
    
    # Create sample food menu items
    # Note: Food menu items are defined in schema.sql

# Initialize a global variable to store the current app
current_app = None