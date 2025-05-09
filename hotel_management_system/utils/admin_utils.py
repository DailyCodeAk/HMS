from flask import current_app
from datetime import datetime, timedelta
from . import db

def get_dashboard_stats():
    """
    Get statistics for the admin dashboard.
    
    Returns:
        Dictionary containing count of guests, employees, rooms, bookings, 
        and inventory items.
    """
    stats = {
        'guest_count': len(db.query_db('SELECT id FROM guests')),
        'employee_count': len(db.query_db('SELECT id FROM employees')),
        'room_count': len(db.query_db('SELECT id FROM rooms')),
        'booking_count': len(db.query_db('SELECT id FROM bookings WHERE status != "cancelled"')),
        'inventory_count': len(db.query_db('SELECT id FROM inventory')),
        'pending_orders': len(db.query_db('SELECT id FROM orders WHERE status = "pending"'))
    }
    
    # Calculate occupancy rate
    total_rooms = stats['room_count']
    occupied_rooms = len(db.query_db('SELECT id FROM rooms WHERE status = "occupied"'))
    stats['occupancy_rate'] = round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0
    
    return stats

def get_all_guests(with_bookings=False):
    """
    Get all guests.
    
    Args:
        with_bookings: If True, includes bookings for each guest
        
    Returns:
        List of guest records
    """
    guests = db.query_db('SELECT * FROM guests ORDER BY name')
    
    if with_bookings:
        for guest in guests:
            bookings = db.query_db('''
                SELECT b.*, r.room_number, r.type 
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                WHERE b.guest_id = ?
                ORDER BY b.check_in DESC
            ''', [guest['id']])
            guest['bookings'] = bookings
    
    return guests

def get_guest(guest_id):
    """
    Get a specific guest by ID.
    
    Args:
        guest_id: ID of the guest
        
    Returns:
        Guest record or None if not found
    """
    guest = db.query_db('SELECT * FROM guests WHERE id = ?', [guest_id], one=True)
    
    if guest:
        bookings = db.query_db('''
            SELECT b.*, r.room_number, r.type 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.guest_id = ?
            ORDER BY b.check_in DESC
        ''', [guest_id])
        guest['bookings'] = bookings
    
    return guest

def get_all_employees(filter_department=None):
    """
    Get all employees, optionally filtered by department.
    
    Args:
        filter_department: Department to filter by
        
    Returns:
        List of employee records
    """
    if filter_department:
        return db.query_db(
            'SELECT * FROM employees WHERE department = ? ORDER BY name',
            [filter_department]
        )
    return db.query_db('SELECT * FROM employees ORDER BY name')

def add_employee(name, position, department, contact):
    """
    Add a new employee.
    
    Args:
        name: Employee name
        position: Job position
        department: Department
        contact: Contact information
        
    Returns:
        ID of the new employee if successful, None otherwise
    """
    data = {
        'name': name,
        'position': position,
        'department': department,
        'contact': contact,
        'hire_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    return db.insert_db('employees', data)

def update_employee(employee_id, data):
    """
    Update employee information.
    
    Args:
        employee_id: ID of the employee to update
        data: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    rows_affected = db.update_db(
        'employees',
        data,
        'id = ?',
        [employee_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def delete_employee(employee_id):
    """
    Delete an employee.
    
    Args:
        employee_id: ID of the employee to delete
        
    Returns:
        True if successful, False otherwise
    """
    # Check if employee has housekeeping assignments
    assignments = db.query_db(
        'SELECT id FROM housekeeping WHERE employee_id = ?',
        [employee_id]
    )
    
    if assignments:
        return False
    
    rows_affected = db.delete_db(
        'employees',
        'id = ?',
        [employee_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def get_all_rooms(filter_status=None, filter_type=None):
    """
    Get all rooms, optionally filtered by status or type.
    
    Args:
        filter_status: Status to filter by
        filter_type: Room type to filter by
        
    Returns:
        List of room records
    """
    query = 'SELECT * FROM rooms'
    params = []
    
    if filter_status and filter_type:
        query += ' WHERE status = ? AND type = ?'
        params = [filter_status, filter_type]
    elif filter_status:
        query += ' WHERE status = ?'
        params = [filter_status]
    elif filter_type:
        query += ' WHERE type = ?'
        params = [filter_type]
    
    query += ' ORDER BY room_number'
    
    return db.query_db(query, params)

def add_room(room_number, room_type, price, capacity):
    """
    Add a new room.
    
    Args:
        room_number: Room number
        room_type: Type of room (Standard, Deluxe, Suite, etc.)
        price: Price per night
        capacity: Maximum number of people
        
    Returns:
        ID of the new room if successful, None otherwise
    """
    # Check if room number already exists
    existing = db.query_db(
        'SELECT id FROM rooms WHERE room_number = ?',
        [room_number],
        one=True
    )
    
    if existing:
        return None
    
    data = {
        'room_number': room_number,
        'type': room_type,
        'price': price,
        'capacity': capacity,
        'status': 'available'
    }
    
    return db.insert_db('rooms', data)

def update_room(room_id, data):
    """
    Update room information.
    
    Args:
        room_id: ID of the room to update
        data: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    rows_affected = db.update_db(
        'rooms',
        data,
        'id = ?',
        [room_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def get_housekeeping_tasks(status=None, date=None):
    """
    Get housekeeping tasks, optionally filtered by status or date.
    
    Args:
        status: Task status to filter by
        date: Date to filter by
        
    Returns:
        List of housekeeping tasks
    """
    query = '''
        SELECT h.*, r.room_number, e.name as employee_name
        FROM housekeeping h
        JOIN rooms r ON h.room_id = r.id
        JOIN employees e ON h.employee_id = e.id
    '''
    params = []
    
    if status and date:
        query += ' WHERE h.status = ? AND h.date = ?'
        params = [status, date]
    elif status:
        query += ' WHERE h.status = ?'
        params = [status]
    elif date:
        query += ' WHERE h.date = ?'
        params = [date]
    
    query += ' ORDER BY h.date DESC, r.room_number'
    
    return db.query_db(query, params)

def assign_housekeeping(room_id, employee_id, date, notes=None):
    """
    Assign a housekeeping task.
    
    Args:
        room_id: ID of the room
        employee_id: ID of the employee
        date: Date for the task
        notes: Additional notes
        
    Returns:
        ID of the new task if successful, None otherwise
    """
    data = {
        'room_id': room_id,
        'employee_id': employee_id,
        'status': 'pending',
        'date': date,
        'notes': notes
    }
    
    return db.insert_db('housekeeping', data)

def update_housekeeping_status(task_id, status):
    """
    Update the status of a housekeeping task.
    
    Args:
        task_id: ID of the task
        status: New status
        
    Returns:
        True if successful, False otherwise
    """
    data = {'status': status}
    
    if status == 'completed':
        data['completion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    rows_affected = db.update_db(
        'housekeeping',
        data,
        'id = ?',
        [task_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def get_inventory_items(category=None, low_stock=False):
    """
    Get inventory items, optionally filtered by category or low stock.
    
    Args:
        category: Category to filter by
        low_stock: If True, only returns items with low stock
        
    Returns:
        List of inventory items
    """
    query = 'SELECT * FROM inventory'
    params = []
    
    if category and low_stock:
        query += ' WHERE category = ? AND quantity < 20'
        params = [category]
    elif category:
        query += ' WHERE category = ?'
        params = [category]
    elif low_stock:
        query += ' WHERE quantity < 20'
    
    query += ' ORDER BY item_name'
    
    return db.query_db(query, params)

def add_inventory_item(item_name, quantity, category):
    """
    Add a new inventory item.
    
    Args:
        item_name: Name of the item
        quantity: Quantity available
        category: Category of the item
        
    Returns:
        ID of the new item if successful, None otherwise
    """
    # Check if item already exists
    existing = db.query_db(
        'SELECT id FROM inventory WHERE item_name = ?',
        [item_name],
        one=True
    )
    
    if existing:
        # Update quantity instead
        current_quantity = db.query_db(
            'SELECT quantity FROM inventory WHERE id = ?',
            [existing['id']],
            one=True
        )['quantity']
        
        new_quantity = current_quantity + int(quantity)
        
        db.update_db(
            'inventory',
            {'quantity': new_quantity, 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            'id = ?',
            [existing['id']]
        )
        
        return existing['id']
    
    data = {
        'item_name': item_name,
        'quantity': quantity,
        'category': category,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return db.insert_db('inventory', data)

def update_inventory_quantity(item_id, quantity_change):
    """
    Update the quantity of an inventory item.
    
    Args:
        item_id: ID of the item
        quantity_change: Change in quantity (positive or negative)
        
    Returns:
        True if successful, False otherwise
    """
    # Get current quantity
    current = db.query_db(
        'SELECT quantity FROM inventory WHERE id = ?',
        [item_id],
        one=True
    )
    
    if not current:
        return False
    
    new_quantity = current['quantity'] + quantity_change
    
    # Ensure quantity doesn't go below zero
    if new_quantity < 0:
        new_quantity = 0
    
    data = {
        'quantity': new_quantity,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    rows_affected = db.update_db(
        'inventory',
        data,
        'id = ?',
        [item_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def place_order(item_id, quantity):
    """
    Place an order for an inventory item.
    
    Args:
        item_id: ID of the item
        quantity: Quantity to order
        
    Returns:
        ID of the new order if successful, None otherwise
    """
    data = {
        'item_id': item_id,
        'quantity': quantity,
        'status': 'pending',
        'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return db.insert_db('orders', data)

def get_orders(status=None):
    """
    Get orders, optionally filtered by status.
    
    Args:
        status: Status to filter by
        
    Returns:
        List of orders
    """
    query = '''
        SELECT o.*, i.item_name, i.category
        FROM orders o
        JOIN inventory i ON o.item_id = i.id
    '''
    params = []
    
    if status:
        query += ' WHERE o.status = ?'
        params = [status]
    
    query += ' ORDER BY o.order_date DESC'
    
    return db.query_db(query, params)

def update_order_status(order_id, status):
    """
    Update the status of an order.
    
    Args:
        order_id: ID of the order
        status: New status
        
    Returns:
        True if successful, False otherwise
    """
    data = {'status': status}
    
    if status == 'received':
        # Update inventory quantity
        order = db.query_db(
            'SELECT item_id, quantity FROM orders WHERE id = ?',
            [order_id],
            one=True
        )
        
        if order:
            update_inventory_quantity(order['item_id'], order['quantity'])
    
    rows_affected = db.update_db(
        'orders',
        data,
        'id = ?',
        [order_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def get_room_service_requests(status=None):
    """
    Get room service requests, optionally filtered by status.
    
    Args:
        status: Status to filter by
        
    Returns:
        List of room service requests
    """
    query = '''
        SELECT rs.*, b.guest_id, g.name as guest_name, r.room_number
        FROM room_service rs
        JOIN bookings b ON rs.booking_id = b.id
        JOIN guests g ON b.guest_id = g.id
        JOIN rooms r ON b.room_id = r.id
    '''
    params = []
    
    if status:
        query += ' WHERE rs.status = ?'
        params = [status]
    
    query += ' ORDER BY rs.request_time DESC'
    
    return db.query_db(query, params)

def update_room_service_status(request_id, status):
    """
    Update the status of a room service request.
    
    Args:
        request_id: ID of the request
        status: New status
        
    Returns:
        True if successful, False otherwise
    """
    data = {'status': status}
    
    if status == 'completed':
        data['completion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    rows_affected = db.update_db(
        'room_service',
        data,
        'id = ?',
        [request_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def generate_occupancy_report(start_date, end_date):
    """
    Generate a room occupancy report for a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with report data
    """
    # Get all bookings in the date range
    bookings = db.query_db('''
        SELECT b.*, r.room_number, r.type, g.name as guest_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN guests g ON b.guest_id = g.id
        WHERE (b.check_in BETWEEN ? AND ?) OR
              (b.check_out BETWEEN ? AND ?) OR
              (b.check_in <= ? AND b.check_out >= ?)
        AND b.status != "cancelled"
        ORDER BY b.check_in
    ''', [start_date, end_date, start_date, end_date, start_date, end_date])
    
    # Calculate occupancy rate for each day
    date_range = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    total_rooms = len(db.query_db('SELECT id FROM rooms'))
    
    daily_occupancy = {}
    
    while current_date <= end:
        date_str = current_date.strftime('%Y-%m-%d')
        date_range.append(date_str)
        
        # Count occupied rooms for this day
        occupied = 0
        for booking in bookings:
            check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
            check_out = datetime.strptime(booking['check_out'], '%Y-%m-%d')
            
            if check_in <= current_date < check_out:
                occupied += 1
        
        rate = round((occupied / total_rooms * 100), 2) if total_rooms > 0 else 0
        daily_occupancy[date_str] = {
            'occupied': occupied,
            'total': total_rooms,
            'rate': rate
        }
        
        current_date += timedelta(days=1)
    
    # Calculate average occupancy for the period
    total_rate = sum(day['rate'] for day in daily_occupancy.values())
    avg_occupancy = round(total_rate / len(daily_occupancy), 2) if daily_occupancy else 0
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'bookings': bookings,
        'dates': date_range,
        'daily_occupancy': daily_occupancy,
        'average_occupancy': avg_occupancy
    }

def generate_revenue_report(start_date, end_date):
    """
    Generate a revenue report for a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with report data
    """
    # Get all bookings in the date range
    bookings = db.query_db('''
        SELECT b.*, r.room_number, r.type, r.price, g.name as guest_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN guests g ON b.guest_id = g.id
        WHERE (b.check_in BETWEEN ? AND ?) OR
              (b.check_out BETWEEN ? AND ?) OR
              (b.check_in <= ? AND b.check_out >= ?)
        AND b.status != "cancelled"
        ORDER BY b.check_in
    ''', [start_date, end_date, start_date, end_date, start_date, end_date])
    
    # Calculate revenue for each booking
    total_revenue = 0
    revenue_by_room_type = {}
    
    for booking in bookings:
        check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        check_out = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        
        # Calculate days in the date range
        days = 0
        current = max(check_in, datetime.strptime(start_date, '%Y-%m-%d'))
        end = min(check_out, datetime.strptime(end_date, '%Y-%m-%d'))
        
        while current < end:
            days += 1
            current += timedelta(days=1)
        
        revenue = days * booking['price']
        booking['revenue'] = revenue
        total_revenue += revenue
        
        # Track revenue by room type
        room_type = booking['type']
        if room_type not in revenue_by_room_type:
            revenue_by_room_type[room_type] = 0
        revenue_by_room_type[room_type] += revenue
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'bookings': bookings,
        'total_revenue': total_revenue,
        'revenue_by_room_type': revenue_by_room_type
    }