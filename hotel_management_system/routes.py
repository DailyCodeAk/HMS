from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .utils.auth import admin_required, user_required, login_user, register_user, logout_user
from .utils.db import query_db, insert_db, update_db, delete_db
from .utils.admin_utils import (
    get_dashboard_stats, get_all_guests, get_all_employees, add_employee,
    get_housekeeping_tasks, assign_housekeeping, update_housekeeping_status,
    get_inventory_items, add_inventory_item, place_order, get_orders, update_order_status
)
from .utils.user_utils import (
    get_guest_profile, create_guest_profile, get_user_bookings, get_booking,
    get_available_rooms, create_booking, cancel_booking, get_active_bookings,
    create_room_service_request, get_room_service_requests
)
from .utils.food import (
    get_all_menu_items, get_menu_item, add_menu_item, update_menu_item, 
    create_food_order, get_food_order, get_guest_food_orders, get_active_food_orders,
    update_food_order_status, cancel_food_order, get_menu_categories, search_menu,
    get_daily_specials, get_food_sales_report
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')
food_bp = Blueprint('food', __name__, url_prefix='/food')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, user = login_user(username, password)
        if success and user['role'] == 'admin':
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('admin/login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, user = login_user(username, password)
        if success and user['role'] == 'user':
            session['role'] = 'user'
            
            # Check if user has a guest profile
            guest = get_guest_profile(user['id'])
            if not guest:
                return redirect(url_for('user.profile_setup'))
            
            return redirect(url_for('user.dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('user/login.html')

@auth_bp.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        success, message = register_user(username, password, email, 'user')
        
        if success:
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.user_login'))
        else:
            flash(message)
    
    return render_template('user/register.html')

@auth_bp.route('/user/logout')
def user_logout():
    logout_user()
    return redirect(url_for('auth.user_login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/guests')
@admin_required
def guests():
    all_guests = get_all_guests()
    return render_template('admin/guests.html', guests=all_guests)

@admin_bp.route('/employees')
@admin_required
def employees():
    all_employees = get_all_employees()
    return render_template('admin/employees.html', employees=all_employees)

@admin_bp.route('/add_employee', methods=['POST'])
@admin_required
def add_employee_route():
    name = request.form['name']
    position = request.form['position']
    department = request.form['department']
    contact = request.form['contact']
    
    employee_id = add_employee(name, position, department, contact)
    
    if employee_id:
        flash('Employee added successfully')
    else:
        flash('Failed to add employee')
    
    return redirect(url_for('admin.employees'))

@admin_bp.route('/housekeeping')
@admin_required
def housekeeping():
    tasks = get_housekeeping_tasks()
    housekeeping_employees = get_all_employees(filter_department='Housekeeping')
    rooms = query_db('SELECT * FROM rooms ORDER BY room_number')
    
    return render_template('admin/housekeeping.html', 
                          housekeeping=tasks,
                          employees=housekeeping_employees,
                          rooms=rooms)

@admin_bp.route('/assign_housekeeping', methods=['POST'])
@admin_required
def assign_housekeeping_route():
    room_id = request.form['room_id']
    employee_id = request.form['employee_id']
    date = request.form['date']
    notes = request.form.get('notes', '')
    
    task_id = assign_housekeeping(room_id, employee_id, date, notes)
    
    if task_id:
        flash('Housekeeping task assigned successfully')
    else:
        flash('Failed to assign housekeeping task')
    
    return redirect(url_for('admin.housekeeping'))

@admin_bp.route('/update_housekeeping_status', methods=['POST'])
@admin_required
def update_housekeeping_status_route():
    task_id = request.form['task_id']
    status = request.form['status']
    
    success = update_housekeeping_status(task_id, status)
    
    if success:
        flash('Housekeeping status updated successfully')
    else:
        flash('Failed to update housekeeping status')
    
    return redirect(url_for('admin.housekeeping'))

@admin_bp.route('/inventory')
@admin_required
def inventory():
    inventory_items = get_inventory_items()
    orders = get_orders()
    
    return render_template('admin/inventory.html', 
                          inventory=inventory_items,
                          orders=orders)
@admin_bp.route('/add_inventory', methods=['POST'])
@admin_required
def add_inventory():
    item_name = request.form['item_name']
    quantity = request.form['quantity']
    category = request.form['category']
    
    item_id = add_inventory_item(item_name, quantity, category)
    
    if item_id:
        flash('Inventory item added successfully')
    else:
        flash('Failed to add inventory item')
    
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/place_order', methods=['POST'])
@admin_required
def place_order_route():
    item_id = request.form['item_id']
    quantity = request.form['quantity']
    
    order_id = place_order(item_id, quantity)
    
    if order_id:
        flash('Order placed successfully')
    else:
        flash('Failed to place order')
    
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/update_order_status', methods=['POST'])
@admin_required
def update_order_status_route():
    order_id = request.form['order_id']
    status = request.form['status']
    
    success = update_order_status(order_id, status)
    
    if success:
        flash('Order status updated successfully')
    else:
        flash('Failed to update order status')
    
    return redirect(url_for('admin.inventory'))
@user_bp.route('/profile_setup', methods=['GET', 'POST'])
@user_required
def profile_setup():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        
        guest_id = create_guest_profile(session['user_id'], name, phone, address)
        
        if guest_id:
            flash('Profile setup successful')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Failed to create profile')
    
    return render_template('user/profile_setup.html')

@user_bp.route('/dashboard')
@user_required
def dashboard():
    guest = get_guest_profile(session['user_id'])
    if not guest:
        return redirect(url_for('user.profile_setup'))
    
    bookings = get_user_bookings(guest['id'])
    
    return render_template('user/dashboard.html', guest=guest, bookings=bookings)

@user_bp.route('/booking', methods=['GET', 'POST'])
@user_required
def booking():
    guest = get_guest_profile(session['user_id'])
    if not guest:
        flash('You need to complete your profile first')
        return redirect(url_for('user.profile_setup'))
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        
        booking_id, message = create_booking(guest['id'], room_id, check_in, check_out)
        
        if booking_id:
            flash('Booking successful')
            return redirect(url_for('user.dashboard'))
        else:
            flash(f'Booking failed: {message}')
    
    rooms = get_available_rooms(
        datetime.now().strftime('%Y-%m-%d'), 
        (datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    )
    
    return render_template('user/booking.html', rooms=rooms)

@user_bp.route('/cancel_booking/<int:booking_id>')
@user_required
def cancel_booking_route(booking_id):
    guest = get_guest_profile(session['user_id'])
    if not guest:
        flash('Invalid request')
        return redirect(url_for('user.dashboard'))
    
    success, message = cancel_booking(booking_id, guest['id'])
    
    if success:
        flash('Booking cancelled successfully')
    else:
        flash(f'Failed to cancel booking: {message}')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/room_service', methods=['GET', 'POST'])
@user_required
def room_service():
    guest = get_guest_profile(session['user_id'])
    if not guest:
        flash('You need to complete your profile first')
        return redirect(url_for('user.profile_setup'))
    
    bookings = get_active_bookings(guest['id'])
    
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        service_type = request.form['service_type']
        notes = request.form['notes']
        
        service_id, message = create_room_service_request(booking_id, service_type, notes)
        
        if service_id:
            flash('Room service request submitted')
            return redirect(url_for('user.dashboard'))
        else:
            flash(f'Failed to submit request: {message}')
    
    return render_template('user/room_service.html', bookings=bookings)
@food_bp.route('/admin/menu', methods=['GET'])
@admin_required
def admin_menu():
    menu_items = get_all_menu_items()
    return render_template('admin/menu.html', menu_items=menu_items)

@food_bp.route('/admin/add_menu_item', methods=['POST'])
@admin_required
def admin_add_menu_item():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    category = request.form['category']
    is_vegetarian = 'is_vegetarian' in request.form
    is_vegan = 'is_vegan' in request.form
    is_gluten_free = 'is_gluten_free' in request.form
    is_special = 'is_special' in request.form
    
    item_id = add_menu_item(
        name, description, price, category,
        is_vegetarian, is_vegan, is_gluten_free, is_special
    )
    
    if item_id:
        flash('Menu item added successfully')
    else:
        flash('Failed to add menu item')
    
    return redirect(url_for('food.admin_menu'))

@food_bp.route('/admin/update_menu_item', methods=['POST'])
@admin_required
def admin_update_menu_item():
    item_id = request.form['id']
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    category = request.form['category']
    is_vegetarian = 'is_vegetarian' in request.form
    is_vegan = 'is_vegan' in request.form
    is_gluten_free = 'is_gluten_free' in request.form
    is_special = 'is_special' in request.form
    
    data = {
        'name': name,
        'description': description,
        'price': price,
        'category': category,
        'is_vegetarian': 1 if is_vegetarian else 0,
        'is_vegan': 1 if is_vegan else 0,
        'is_gluten_free': 1 if is_gluten_free else 0,
        'is_special': 1 if is_special else 0
    }
    
    success = update_menu_item(item_id, data)
    
    if success:
        flash('Menu item updated successfully')
    else:
        flash('Failed to update menu item')
    
    return redirect(url_for('food.admin_menu'))

@food_bp.route('/admin/toggle_menu_item', methods=['POST'])
@admin_required
def admin_toggle_menu_item():
    item_id = request.form['id']
    available = int(request.form.get('available', 0))
    
    data = {'available': 1 if available == 0 else 0}
    
    success = update_menu_item(item_id, data)
    
    if success:
        flash('Menu item availability updated')
    else:
        flash('Failed to update menu item')
    
    return redirect(url_for('food.admin_menu'))

@food_bp.route('/admin/orders', methods=['GET'])
@admin_required
def admin_orders():
    status = request.args.get('status')
    
    if status and status != 'all':
        orders = get_active_food_orders(status)
    else:
        orders = get_active_food_orders()
    
    return render_template('admin/food_orders.html', orders=orders)

@food_bp.route('/admin/update_order_status', methods=['POST'])
@admin_required
def admin_update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']
    
    success = update_food_order_status(order_id, status)
    
    if success:
        flash(f'Order status updated to {status}')
    else:
        flash('Failed to update order status')
    
    return redirect(url_for('food.admin_orders'))

@food_bp.route('/admin/reports', methods=['GET'])
@admin_required
def admin_food_reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report = None
    
    if start_date and end_date:
        report = get_food_sales_report(start_date, end_date)
    
    return render_template('admin/food_reports.html', report=report)

@food_bp.route('/menu', methods=['GET'])
def user_food_menu():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    dietary_filters = request.args.getlist('dietary')
    
    categories = get_menu_categories()

    daily_specials = get_daily_specials()
    
    if query:
        menu_items = search_menu(query, category, dietary_filters)
    elif category:
        menu_items = get_all_menu_items(category)
    else:
        menu_items = get_all_menu_items()
    active_bookings = []
    is_logged_in = 'user_id' in session and session.get('role') == 'user'
    
    if is_logged_in:
        user_id = session['user_id']
        guest = get_guest_profile(user_id)
        
        if guest:
            active_bookings = get_active_bookings(guest['id'])
    
    return render_template(
        'user/food_menu.html',
        menu_items=menu_items,
        categories=categories,
        daily_specials=daily_specials,
        dietary_filters=dietary_filters,
        is_logged_in=is_logged_in,
        active_bookings=active_bookings
    )

@food_bp.route('/place_order', methods=['POST'])
@user_required
def user_place_order():
    user_id = session['user_id']
    guest = get_guest_profile(user_id)
    
    if not guest:
        flash('You need to complete your profile before placing an order')
        return redirect(url_for('user.profile_setup'))
    
    items = []
    for i in range(len(request.form.getlist('items[][menu_item_id]'))):
        menu_item_id = request.form.getlist('items[][menu_item_id]')[i]
        quantity = int(request.form.getlist('items[][quantity]')[i])
        
        items.append({
            'menu_item_id': menu_item_id,
            'quantity': quantity
        })
    
    order_type = request.form['order_type']
    is_room_service = order_type == 'room_service'
    special_requests = request.form.get('special_requests', '')
    
    booking_id = None
    table_number = None
    
    if is_room_service:
        booking_id = request.form['booking_id']
    else:
        table_number = request.form.get('table_number', '')
    
    order_id, message = create_food_order(
        guest['id'], booking_id, items, is_room_service, table_number, special_requests
    )
    
    if order_id:
        flash('Order placed successfully')
        return redirect(url_for('food.user_my_orders'))
    else:
        flash(f'Failed to place order: {message}')
        return redirect(url_for('food.user_food_menu'))

@food_bp.route('/my_orders', methods=['GET'])
@user_required
def user_my_orders():
    user_id = session['user_id']
    guest = get_guest_profile(user_id)
    
    if not guest:
        flash('You need to complete your profile to view orders')
        return redirect(url_for('user.profile_setup'))
    
    orders = get_guest_food_orders(guest['id'])
    
    return render_template('user/my_orders.html', orders=orders)

@food_bp.route('/cancel_order/<int:order_id>', methods=['GET'])
@user_required
def user_cancel_order(order_id):
    user_id = session['user_id']
    guest = get_guest_profile(user_id)
    
    if not guest:
        flash('Invalid request')
        return redirect(url_for('user.dashboard'))
    
    success, message = cancel_food_order(order_id, guest['id'])
    
    if success:
        flash('Order cancelled successfully')
    else:
        flash(f'Failed to cancel order: {message}')
    
    return redirect(url_for('food.user_my_orders'))