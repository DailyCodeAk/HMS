from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'walnutmercury_hotel_system'  # Change in production

# Database initialization
DATABASE = 'hotel.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Login decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('You need to be logged in as admin to view this page.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'user':
            flash('You need to be logged in to view this page.')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = query_db('SELECT * FROM users WHERE username = ? AND password = ? AND role = "admin"',
                       [username, password], one=True)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    guest_count = query_db('SELECT COUNT(*) as count FROM guests', one=True)['count']
    employee_count = query_db('SELECT COUNT(*) as count FROM employees', one=True)['count']
    room_count = query_db('SELECT COUNT(*) as count FROM rooms', one=True)['count']
    inventory_count = query_db('SELECT COUNT(*) as count FROM inventory', one=True)['count']
    
    return render_template('admin/dashboard.html', 
                          guest_count=guest_count,
                          employee_count=employee_count,
                          room_count=room_count,
                          inventory_count=inventory_count)

@app.route('/admin/guests')
@admin_required
def admin_guests():
    guests = query_db('SELECT * FROM guests')
    return render_template('admin/guests.html', guests=guests)

@app.route('/admin/employees')
@admin_required
def admin_employees():
    employees = query_db('SELECT * FROM employees')
    return render_template('admin/employees.html', employees=employees)

@app.route('/admin/housekeeping')
@admin_required
def admin_housekeeping():
    housekeeping = query_db('''
        SELECT h.id, h.room_id, h.employee_id, h.status, h.date,
               r.room_number, e.name as employee_name
        FROM housekeeping h
        JOIN rooms r ON h.room_id = r.id
        JOIN employees e ON h.employee_id = e.id
    ''')
    employees = query_db('SELECT * FROM employees WHERE department = "housekeeping"')
    rooms = query_db('SELECT * FROM rooms')
    return render_template('admin/housekeeping.html', 
                          housekeeping=housekeeping,
                          employees=employees,
                          rooms=rooms)

@app.route('/admin/inventory')
@admin_required
def admin_inventory():
    inventory = query_db('SELECT * FROM inventory')
    orders = query_db('SELECT * FROM orders')
    return render_template('admin/inventory.html', 
                          inventory=inventory,
                          orders=orders)

@app.route('/admin/add_employee', methods=['POST'])
@admin_required
def add_employee():
    name = request.form['name']
    position = request.form['position']
    department = request.form['department']
    contact = request.form['contact']
    
    db = get_db()
    db.execute(
        'INSERT INTO employees (name, position, department, contact) VALUES (?, ?, ?, ?)',
        (name, position, department, contact)
    )
    db.commit()
    flash('Employee added successfully')
    return redirect(url_for('admin_employees'))

@app.route('/admin/add_inventory', methods=['POST'])
@admin_required
def add_inventory():
    item_name = request.form['item_name']
    quantity = request.form['quantity']
    category = request.form['category']
    
    db = get_db()
    db.execute(
        'INSERT INTO inventory (item_name, quantity, category) VALUES (?, ?, ?)',
        (item_name, quantity, category)
    )
    db.commit()
    flash('Inventory item added successfully')
    return redirect(url_for('admin_inventory'))

@app.route('/admin/place_order', methods=['POST'])
@admin_required
def place_order():
    item_id = request.form['item_id']
    quantity = request.form['quantity']
    
    db = get_db()
    db.execute(
        'INSERT INTO orders (item_id, quantity, status) VALUES (?, ?, "pending")',
        (item_id, quantity)
    )
    db.commit()
    flash('Order placed successfully')
    return redirect(url_for('admin_inventory'))

@app.route('/admin/assign_housekeeping', methods=['POST'])
@admin_required
def assign_housekeeping():
    room_id = request.form['room_id']
    employee_id = request.form['employee_id']
    date = request.form['date']
    
    db = get_db()
    db.execute(
        'INSERT INTO housekeeping (room_id, employee_id, status, date) VALUES (?, ?, "pending", ?)',
        (room_id, employee_id, date)
    )
    db.commit()
    flash('Housekeeping task assigned successfully')
    return redirect(url_for('admin_housekeeping'))

# User routes
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user:
            flash('Username already exists')
            return redirect(url_for('user_register'))
        
        db = get_db()
        db.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, "user")',
            (username, password, email)
        )
        db.commit()
        
        flash('Registration successful, please login')
        return redirect(url_for('user_login'))
    
    return render_template('user/register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = query_db('SELECT * FROM users WHERE username = ? AND password = ? AND role = "user"',
                       [username, password], one=True)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'user'
            
            guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user['id']], one=True)
            if not guest:
                return redirect(url_for('user_profile_setup'))
            
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('user/login.html')

@app.route('/user/logout')
def user_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('user_login'))

@app.route('/user/profile_setup', methods=['GET', 'POST'])
@user_required
def user_profile_setup():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        
        db = get_db()
        db.execute(
            'INSERT INTO guests (user_id, name, phone, address) VALUES (?, ?, ?, ?)',
            (session['user_id'], name, phone, address)
        )
        db.commit()
        
        flash('Profile setup successful')
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/profile_setup.html')

@app.route('/user/dashboard')
@user_required
def user_dashboard():
    user_id = session['user_id']
    guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)
    bookings = query_db('''
        SELECT b.id, b.check_in, b.check_out, b.status, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ?
    ''', [guest['id']])
    
    return render_template('user/dashboard.html', guest=guest, bookings=bookings)

@app.route('/user/booking', methods=['GET', 'POST'])
@user_required
def user_booking():
    if request.method == 'POST':
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        
        user_id = session['user_id']
        guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)
        
        existing_booking = query_db('''
            SELECT * FROM bookings
            WHERE room_id = ? AND status != "cancelled"
            AND ((check_in BETWEEN ? AND ?) OR (check_out BETWEEN ? AND ?))
        ''', [room_id, check_in, check_out, check_in, check_out], one=True)
        
        if existing_booking:
            flash('Room is not available for the selected dates')
            return redirect(url_for('user_booking'))
        
        db = get_db()
        db.execute(
            'INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES (?, ?, ?, ?, "confirmed")',
            (guest['id'], room_id, check_in, check_out)
        )
        db.commit()
        
        flash('Booking successful')
        return redirect(url_for('user_dashboard'))
    
    rooms = query_db('SELECT * FROM rooms WHERE status = "available"')
    return render_template('user/booking.html', rooms=rooms)

@app.route('/user/room_service', methods=['GET', 'POST'])
@user_required
def user_room_service():
    user_id = session['user_id']
    guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)
    
    bookings = query_db('''
        SELECT b.id, b.check_in, b.check_out, b.status, r.room_number, r.type
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ? AND b.status = "confirmed" AND b.check_out >= date('now')
    ''', [guest['id']])
    
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        service_type = request.form['service_type']
        notes = request.form['notes']
        
        db = get_db()
        db.execute(
            'INSERT INTO room_service (booking_id, service_type, notes, status) VALUES (?, ?, ?, "pending")',
            (booking_id, service_type, notes)
        )
        db.commit()
        
        flash('Room service request submitted')
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/room_service.html', bookings=bookings)

@app.route('/user/cancel_booking/<int:booking_id>')
@user_required
def cancel_booking(booking_id):
    user_id = session['user_id']
    guest = query_db('SELECT * FROM guests WHERE user_id = ?', [user_id], one=True)
    
    booking = query_db('SELECT * FROM bookings WHERE id = ? AND guest_id = ?', 
                      [booking_id, guest['id']], one=True)
    
    if not booking:
        flash('Invalid booking')
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    db.execute('UPDATE bookings SET status = "cancelled" WHERE id = ?', [booking_id])
    db.commit()
    
    flash('Booking cancelled successfully')
    return redirect(url_for('user_dashboard'))

# Initialize database
if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()
        
        db = get_db()
        db.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            ('admin', 'admin123', 'admin@hotel.com', 'admin')
        )
        db.commit()

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True, port=5000)