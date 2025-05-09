from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from datetime import datetime, timedelta
from functools import wraps
from . import db, auth
from .food import (
    get_all_menu_items, get_menu_item, add_menu_item, update_menu_item, delete_menu_item,
    create_food_order, get_food_order, get_guest_food_orders, get_active_food_orders,
    update_food_order_status, cancel_food_order, get_menu_categories, search_menu,
    get_daily_specials, get_food_sales_report
)
from .user_utils import get_active_bookings, get_guest_profile

# Create a Blueprint for food-related routes
food_bp = Blueprint('food', __name__, url_prefix='/food')

# Middleware
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('role') != 'admin':
            flash('You need to be logged in as admin to access this page.')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('role') != 'user':
            flash('You need to be logged in to access this page.')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
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

@food_bp.route('/admin/order_items/<int:order_id>', methods=['GET'])
@admin_required
def admin_order_items(order_id):
    order = get_food_order(order_id)
    
    if not order:
        return {'error': 'Order not found'}, 404
    
    return {'items': order['items']}

@food_bp.route('/admin/reports', methods=['GET'])
@admin_required
def admin_food_reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report = None
    
    if start_date and end_date:
        report = get_food_sales_report(start_date, end_date)
    
    return render_template('admin/food_reports.html', report=report)

# User routes
@food_bp.route('/menu', methods=['GET'])
def user_food_menu():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    dietary_filters = request.args.getlist('dietary')
    
    # Get all categories for filter dropdown
    categories = get_menu_categories()
    
    # Get daily specials
    daily_specials = get_daily_specials()
    
    # Get menu items based on filters
    if query:
        menu_items = search_menu(query, category, dietary_filters)
    elif category:
        menu_items = get_all_menu_items(category)
    else:
        menu_items = get_all_menu_items()
    
    # For logged-in users, get active bookings for room service
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
    
    # Parse items from form
    items = []
    for i in range(len(request.form.getlist('items[][menu_item_id]'))):
        menu_item_id = request.form.getlist('items[][menu_item_id]')[i]
        quantity = int(request.form.getlist('items[][quantity]')[i])
        
        items.append({
            'menu_item_id': menu_item_id,
            'quantity': quantity
        })
    
    # Get order details
    order_type = request.form['order_type']
    is_room_service = order_type == 'room_service'
    special_requests = request.form.get('special_requests', '')
    
    # Get booking or table info
    booking_id = None
    table_number = None
    
    if is_room_service:
        booking_id = request.form['booking_id']
    else:
        table_number = request.form.get('table_number', '')
    
    # Create the order
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

# Register the blueprint in __init__.py
# app.register_blueprint(food_bp)