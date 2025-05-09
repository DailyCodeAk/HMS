
-- Drop tables if they exist
DROP TABLE IF EXISTS room_service;
DROP TABLE IF EXISTS food_order_items;
DROP TABLE IF EXISTS food_orders;
DROP TABLE IF EXISTS food_menu;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS housekeeping;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS users;

-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    department TEXT NOT NULL,
    contact TEXT NOT NULL,
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guests table
CREATE TABLE guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Rooms table
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    price REAL NOT NULL,
    capacity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'occupied', 'maintenance'))
);

-- Bookings table
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests (id),
    FOREIGN KEY (room_id) REFERENCES rooms (id)
);

-- Housekeeping table
CREATE TABLE housekeeping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed')),
    date DATE NOT NULL,
    notes TEXT,
    completion_time TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (id),
    FOREIGN KEY (employee_id) REFERENCES employees (id)
);

-- Inventory table
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    category TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table for inventory
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'shipped', 'received', 'cancelled')),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory (id)
);

-- Room service table
CREATE TABLE room_service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_time TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings (id)
);

-- Food menu table
CREATE TABLE food_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    is_vegetarian INTEGER NOT NULL DEFAULT 0,
    is_vegan INTEGER NOT NULL DEFAULT 0,
    is_gluten_free INTEGER NOT NULL DEFAULT 0,
    is_special INTEGER NOT NULL DEFAULT 0,
    available INTEGER NOT NULL DEFAULT 1,
    image_path TEXT
);

-- Food orders table
CREATE TABLE food_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    booking_id INTEGER,
    is_room_service INTEGER NOT NULL DEFAULT 0,
    table_number TEXT,
    special_requests TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'preparing', 'ready', 'delivered', 'cancelled')),
    total REAL NOT NULL,
    order_time TIMESTAMP NOT NULL,
    delivery_time TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests (id),
    FOREIGN KEY (booking_id) REFERENCES bookings (id)
);

-- Food order items table
CREATE TABLE food_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    item_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES food_orders (id),
    FOREIGN KEY (menu_item_id) REFERENCES food_menu (id)
);

-- Insert sample rooms
INSERT INTO rooms (room_number, type, price, capacity, status)
VALUES 
    ('101', 'Standard', 99.99, 2, 'available'),
    ('102', 'Standard', 99.99, 2, 'available'),
    ('103', 'Standard', 99.99, 2, 'available'),
    ('201', 'Deluxe', 149.99, 2, 'available'),
    ('202', 'Deluxe', 149.99, 2, 'available'),
    ('301', 'Suite', 249.99, 4, 'available'),
    ('302', 'Suite', 249.99, 4, 'available');

-- Insert sample food menu items
INSERT INTO food_menu (name, description, price, category, is_vegetarian, is_vegan, is_gluten_free, is_special, available) VALUES
-- Breakfast Items
('Continental Breakfast', 'Assortment of pastries, fruits, and coffee', 15.99, 'Breakfast', 1, 0, 0, 0, 1),
('American Breakfast', 'Eggs, bacon, toast, and hash browns', 18.99, 'Breakfast', 0, 0, 0, 0, 1),
('Vegetable Omelette', 'Three-egg omelette with seasonal vegetables', 14.99, 'Breakfast', 1, 0, 1, 0, 1),
('Pancake Stack', 'Stack of fluffy pancakes with maple syrup', 12.99, 'Breakfast', 1, 0, 0, 0, 1),
('Fresh Fruit Bowl', 'Assortment of seasonal fruits', 9.99, 'Breakfast', 1, 1, 1, 0, 1),

-- Lunch Items
('Caesar Salad', 'Romaine lettuce, croutons, parmesan, and Caesar dressing', 12.99, 'Lunch', 1, 0, 0, 0, 1),
('Club Sandwich', 'Triple-decker sandwich with turkey, bacon, lettuce, and tomato', 16.99, 'Lunch', 0, 0, 0, 0, 1),
('Vegetable Soup', 'Seasonal vegetables in a savory broth', 8.99, 'Lunch', 1, 1, 1, 0, 1),
('Cheeseburger', 'Beef patty with cheese, lettuce, tomato, and special sauce', 17.99, 'Lunch', 0, 0, 0, 0, 1),
('Grilled Chicken Wrap', 'Grilled chicken with vegetables in a tortilla wrap', 15.99, 'Lunch', 0, 0, 0, 0, 1),

-- Dinner Items
('Filet Mignon', '8oz filet with mashed potatoes and seasonal vegetables', 34.99, 'Dinner', 0, 0, 1, 1, 1),
('Grilled Salmon', 'Atlantic salmon with rice pilaf and asparagus', 29.99, 'Dinner', 0, 0, 1, 0, 1),
('Vegetable Pasta', 'Penne with roasted vegetables in a tomato sauce', 19.99, 'Dinner', 1, 1, 0, 0, 1),
('Roast Chicken', 'Half chicken with roasted potatoes and vegetables', 24.99, 'Dinner', 0, 0, 1, 0, 1),
('Mushroom Risotto', 'Creamy risotto with wild mushrooms', 22.99, 'Dinner', 1, 0, 1, 0, 1),

-- Dessert Items
('Chocolate Cake', 'Rich chocolate cake with ganache', 9.99, 'Dessert', 1, 0, 0, 0, 1),
('Cheesecake', 'New York style cheesecake with berry compote', 10.99, 'Dessert', 1, 0, 0, 0, 1),
('Fruit Sorbet', 'Assortment of fruit sorbets', 7.99, 'Dessert', 1, 1, 1, 0, 1),
('Ice Cream Sundae', 'Vanilla ice cream with chocolate sauce and nuts', 8.99, 'Dessert', 1, 0, 0, 0, 1),
('Tiramisu', 'Classic Italian dessert with coffee and mascarpone', 11.99, 'Dessert', 1, 0, 0, 1, 1),

-- Beverage Items
('Bottled Water', 'Still or sparkling water', 3.99, 'Beverages', 1, 1, 1, 0, 1),
('Soft Drinks', 'Assortment of sodas', 4.99, 'Beverages', 1, 1, 1, 0, 1),
('Coffee', 'Freshly brewed coffee', 4.99, 'Beverages', 1, 1, 1, 0, 1),
('Tea', 'Selection of teas', 4.99, 'Beverages', 1, 1, 1, 0, 1),
('Fresh Juice', 'Orange, apple, or grapefruit juice', 5.99, 'Beverages', 1, 1, 1, 0, 1),
('House Wine (Glass)', 'Red or white house wine', 8.99, 'Beverages', 1, 1, 1, 0, 1),
('House Wine (Bottle)', 'Red or white house wine', 34.99, 'Beverages', 1, 1, 1, 0, 1),
('Beer', 'Selection of domestic and imported beers', 6.99, 'Beverages', 1, 0, 0, 0, 1);

-- Insert sample inventory items
INSERT INTO inventory (item_name, quantity, category)
VALUES
    ('Towels', 100, 'Housekeeping'),
    ('Shampoo', 80, 'Amenities'),
    ('Soap', 120, 'Amenities'),
    ('Toilet Paper', 150, 'Housekeeping'),
    ('Bed Sheets', 50, 'Housekeeping'),
    ('Coffee', 30, 'Food'),
    ('Tea', 25, 'Food'),
    ('Wine Bottles', 40, 'Beverages'),
    ('Beer', 60, 'Beverages');

-- Insert sample employees
INSERT INTO employees (name, position, department, contact)
VALUES
    ('John Smith', 'Manager', 'Management', '555-1234'),
    ('Jane Doe', 'Receptionist', 'Front Desk', '555-5678'),
    ('Robert Johnson', 'Housekeeper', 'Housekeeping', '555-9012'),
    ('Mary Williams', 'Housekeeper', 'Housekeeping', '555-3456'),
    ('James Brown', 'Chef', 'Food Service', '555-7890'),
    ('Patricia Davis', 'Maintenance', 'Maintenance', '555-2345'),
    ('Michael Wilson', 'Waiter', 'Food Service', '555-6789'),
    ('Elizabeth Taylor', 'Room Service', 'Food Service', '555-0123');