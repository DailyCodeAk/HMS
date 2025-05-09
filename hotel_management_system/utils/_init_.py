import os
from flask import Flask

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config: Configuration for testing
        
    Returns:
        Configured Flask application
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='walnutmercury_hotel_system',  # Change in production
        DATABASE=os.path.join(app.instance_path, 'hotel.db'),
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
    except OSError:
        pass

    # Register database functions
    from . import db
    app.teardown_appcontext(db.close_db)
    
    # Initialize database if it doesn't exist
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            db.init_db()
            create_default_data(app)

    # Register blueprints
    from . import auth, admin, user
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user.bp)
    
    # Make url_for('index') work
    app.add_url_rule('/', endpoint='index')
    
    return app

def create_default_data(app):
    """
    Create default data in the database.
    Creates admin user, sample rooms, inventory items, employees, and menu items.
    
    Args:
        app: Flask application
    """
    from . import db, auth
    
    # Create default admin user
    auth.register_user('admin', 'admin123', 'admin@hotel.com', 'admin')
    
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
        db.insert_db('rooms', room)
    
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
        db.insert_db('inventory', item)
    
    # Create sample employees
    employees = [
        {'name': 'John Smith', 'position': 'Manager', 'department': 'Management', 'contact': '555-1234'},
        {'name': 'Jane Doe', 'position': 'Receptionist', 'department': 'Front Desk', 'contact': '555-5678'},
        {'name': 'Robert Johnson', 'position': 'Housekeeper', 'department': 'Housekeeping', 'contact': '555-9012'},
        {'name': 'Mary Williams', 'position': 'Housekeeper', 'department': 'Housekeeping', 'contact': '555-3456'},
        {'name': 'James Brown', 'position': 'Chef', 'department': 'Food Service', 'contact': '555-7890'},
        {'name': 'Patricia Davis', 'position': 'Maintenance', 'department': 'Maintenance', 'contact': '555-2345'},
    ]
    
    for employee in employees:
        db.insert_db('employees', employee)

    # Create sample menu items
    menu_items = [
        # Breakfast Items
        {'name': 'Continental Breakfast', 'description': 'Fresh fruits, pastries, coffee, and juice', 'price': 15.99, 'category': 'Breakfast', 'availability': True},
        {'name': 'Full English Breakfast', 'description': 'Eggs, bacon, sausage, beans, mushrooms, and toast', 'price': 18.99, 'category': 'Breakfast', 'availability': True},
        {'name': 'Avocado Toast', 'description': 'Smashed avocado on sourdough with poached egg', 'price': 12.99, 'category': 'Breakfast', 'availability': True},
        
        # Main Courses
        {'name': 'Grilled Salmon', 'description': 'Fresh salmon with lemon butter sauce and seasonal vegetables', 'price': 24.99, 'category': 'Main Course', 'availability': True},
        {'name': 'Beef Tenderloin', 'description': '8oz beef tenderloin with red wine reduction and mashed potatoes', 'price': 29.99, 'category': 'Main Course', 'availability': True},
        {'name': 'Vegetable Risotto', 'description': 'Creamy arborio rice with seasonal vegetables and parmesan', 'price': 19.99, 'category': 'Main Course', 'availability': True},
        
        # Desserts
        {'name': 'Chocolate Lava Cake', 'description': 'Warm chocolate cake with vanilla ice cream', 'price': 8.99, 'category': 'Dessert', 'availability': True},
        {'name': 'New York Cheesecake', 'description': 'Classic cheesecake with berry compote', 'price': 7.99, 'category': 'Dessert', 'availability': True},
        {'name': 'Tiramisu', 'description': 'Italian coffee-flavored dessert with mascarpone cream', 'price': 8.99, 'category': 'Dessert', 'availability': True},
        
        # Beverages
        {'name': 'Fresh Orange Juice', 'description': 'Freshly squeezed orange juice', 'price': 4.99, 'category': 'Beverages', 'availability': True},
        {'name': 'House Red Wine', 'description': 'Glass of house red wine', 'price': 6.99, 'category': 'Beverages', 'availability': True},
        {'name': 'Craft Beer', 'description': 'Selection of local craft beers', 'price': 5.99, 'category': 'Beverages', 'availability': True},
        
        # Room Service
        {'name': 'Club Sandwich', 'description': 'Triple-decker sandwich with chicken, bacon, lettuce, and tomato', 'price': 14.99, 'category': 'Room Service', 'availability': True},
        {'name': 'Caesar Salad', 'description': 'Romaine lettuce, croutons, parmesan, and Caesar dressing', 'price': 12.99, 'category': 'Room Service', 'availability': True},
        {'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella, and basil', 'price': 16.99, 'category': 'Room Service', 'availability': True}
    ]
    
    for item in menu_items:
        db.insert_db('menu', item)