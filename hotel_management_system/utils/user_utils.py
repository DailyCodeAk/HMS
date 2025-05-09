from flask import current_app
from datetime import datetime, timedelta
from . import db

def get_user_profile(user_id):
    """
    Get the user profile information.
    
    Args:
        user_id: ID of the user
        
    Returns:
        User profile data or None if not found
    """
    return db.query_db(
        'SELECT * FROM users WHERE id = ?',
        [user_id],
        one=True
    )

def get_guest_profile(user_id):
    """
    Get the guest profile for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Guest profile data or None if not found
    """
    return db.query_db(
        'SELECT * FROM guests WHERE user_id = ?',
        [user_id],
        one=True
    )

def create_guest_profile(user_id, name, phone, address):
    """
    Create a guest profile for a user.
    
    Args:
        user_id: ID of the user
        name: Full name of the guest
        phone: Phone number
        address: Address
        
    Returns:
        ID of the new guest profile if successful, None otherwise
    """
    # Check if profile already exists
    existing = db.query_db(
        'SELECT id FROM guests WHERE user_id = ?',
        [user_id],
        one=True
    )
    
    if existing:
        return existing['id']
    
    data = {
        'user_id': user_id,
        'name': name,
        'phone': phone,
        'address': address,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return db.insert_db('guests', data)

def update_guest_profile(guest_id, data):
    """
    Update a guest profile.
    
    Args:
        guest_id: ID of the guest profile
        data: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    rows_affected = db.update_db(
        'guests',
        data,
        'id = ?',
        [guest_id]
    )
    
    return rows_affected is not None and rows_affected > 0

def get_user_bookings(guest_id, include_cancelled=False):
    """
    Get all bookings for a guest.
    
    Args:
        guest_id: ID of the guest
        include_cancelled: Whether to include cancelled bookings
        
    Returns:
        List of bookings
    """
    query = '''
        SELECT b.*, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ?
    '''
    
    if not include_cancelled:
        query += ' AND b.status != "cancelled"'
    
    query += ' ORDER BY b.check_in DESC'
    
    return db.query_db(query, [guest_id])

def get_booking(booking_id, guest_id=None):
    """
    Get a specific booking.
    
    Args:
        booking_id: ID of the booking
        guest_id: ID of the guest (for security check)
        
    Returns:
        Booking data or None if not found
    """
    query = '''
        SELECT b.*, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.id = ?
    '''
    params = [booking_id]
    
    if guest_id:
        query += ' AND b.guest_id = ?'
        params.append(guest_id)
    
    return db.query_db(query, params, one=True)

def get_available_rooms(check_in, check_out, room_type=None):
    """
    Get available rooms for a date range.
    
    Args:
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        room_type: Optional room type filter
        
    Returns:
        List of available rooms
    """
    # Base query for all rooms
    query = '''
        SELECT r.*
        FROM rooms r
        WHERE r.id NOT IN (
            SELECT b.room_id
            FROM bookings b
            WHERE b.status IN ('confirmed', 'checked_in')
            AND (
                (b.check_in <= ? AND b.check_out > ?) OR
                (b.check_in < ? AND b.check_out >= ?) OR
                (b.check_in >= ? AND b.check_out <= ?)
            )
        )
    '''
    params = [check_out, check_in, check_out, check_in, check_in, check_out]
    
    # Add room type filter if specified
    if room_type:
        query += ' AND r.type = ?'
        params.append(room_type)
    
    query += ' ORDER BY r.price, r.room_number'
    
    return db.query_db(query, params)

def create_booking(guest_id, room_id, check_in, check_out):
    """
    Create a new booking.
    
    Args:
        guest_id: ID of the guest
        room_id: ID of the room
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        
    Returns:
        ID of the new booking if successful, None otherwise
    """
    # Check if room is available for the dates
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
    
    # Validate dates
    if check_in_date >= check_out_date:
        return None, "Check-out date must be after check-in date"
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if check_in_date < today:
        return None, "Check-in date cannot be in the past"
    
    # Get available rooms
    available_rooms = get_available_rooms(check_in, check_out)
    room_ids = [room['id'] for room in available_rooms]
    
    if int(room_id) not in room_ids:
        return None, "Room is not available for the selected dates"
    
    data = {
        'guest_id': guest_id,
        'room_id': room_id,
        'check_in': check_in,
        'check_out': check_out,
        'status': 'confirmed',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    booking_id = db.insert_db('bookings', data)
    
    if not booking_id:
        return None, "Failed to create booking"
    
    # Update room status if check-in is today
    if check_in_date == today:
        db.update_db(
            'rooms',
            {'status': 'occupied'},
            'id = ?',
            [room_id]
        )
    
    return booking_id, "Booking successful"

def cancel_booking(booking_id, guest_id):
    """
    Cancel a booking.
    
    Args:
        booking_id: ID of the booking
        guest_id: ID of the guest (for security check)
        
    Returns:
        True if successful, False otherwise
    """
    # Check if booking belongs to guest
    booking = get_booking(booking_id, guest_id)
    
    if not booking:
        return False, "Invalid booking"
    
    # Check if booking can be cancelled
    if booking['status'] in ['checked_out', 'cancelled']:
        return False, "Booking cannot be cancelled"
    
    # Check cancellation policy (e.g., 24 hours before check-in)
    check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
    now = datetime.now()
    
    if check_in - now < timedelta(hours=24) and booking['status'] != 'pending':
        return False, "Booking cannot be cancelled within 24 hours of check-in"
    
    success = db.update_db(
        'bookings',
        {'status': 'cancelled'},
        'id = ? AND guest_id = ?',
        [booking_id, guest_id]
    )
    
    if not success:
        return False, "Failed to cancel booking"
    
    # If room was occupied, update room status
    if booking['status'] == 'checked_in':
        db.update_db(
            'rooms',
            {'status': 'available'},
            'id = ?',
            [booking['room_id']]
        )
    
    return True, "Booking cancelled successfully"

def get_active_bookings(guest_id):
    """
    Get active bookings for a guest (confirmed or checked-in).
    
    Args:
        guest_id: ID of the guest
        
    Returns:
        List of active bookings
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    query = '''
        SELECT b.*, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ?
        AND b.status IN ('confirmed', 'checked_in')
        AND b.check_out >= ?
        ORDER BY b.check_in
    '''
    
    return db.query_db(query, [guest_id, today])

def create_room_service_request(booking_id, service_type, notes):
    """
    Create a room service request.
    
    Args:
        booking_id: ID of the booking
        service_type: Type of service
        notes: Additional notes or details
        
    Returns:
        ID of the new request if successful, None otherwise
    """
    # Check if booking is active
    booking = db.query_db(
        '''
        SELECT b.*, g.id as guest_id
        FROM bookings b
        JOIN guests g ON b.guest_id = g.id
        WHERE b.id = ? AND b.status IN ('confirmed', 'checked_in')
        ''',
        [booking_id],
        one=True
    )
    
    if not booking:
        return None, "Invalid or inactive booking"
    
    data = {
        'booking_id': booking_id,
        'service_type': service_type,
        'notes': notes,
        'status': 'pending',
        'request_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    request_id = db.insert_db('room_service', data)
    
    if not request_id:
        return None, "Failed to create room service request"
    
    return request_id, "Room service request submitted"

def get_room_service_requests(guest_id):
    """
    Get room service requests for a guest.
    
    Args:
        guest_id: ID of the guest
        
    Returns:
        List of room service requests
    """
    query = '''
        SELECT rs.*, b.check_in, b.check_out, r.room_number
        FROM room_service rs
        JOIN bookings b ON rs.booking_id = b.id
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ?
        ORDER BY rs.request_time DESC
    '''
    
    return db.query_db(query, [guest_id])

def cancel_room_service_request(request_id, guest_id):
    """
    Cancel a room service request.
    
    Args:
        request_id: ID of the request
        guest_id: ID of the guest (for security check)
        
    Returns:
        True if successful, False otherwise
    """
    # Check if request belongs to guest
    request = db.query_db(
        '''
        SELECT rs.*, b.guest_id
        FROM room_service rs
        JOIN bookings b ON rs.booking_id = b.id
        WHERE rs.id = ? AND b.guest_id = ?
        ''',
        [request_id, guest_id],
        one=True
    )
    
    if not request:
        return False, "Invalid request"
    
    # Check if request can be cancelled
    if request['status'] not in ['pending', 'in_progress']:
        return False, "Request cannot be cancelled"
    
    success = db.update_db(
        'room_service',
        {'status': 'cancelled'},
        'id = ?',
        [request_id]
    )
    
    if not success:
        return False, "Failed to cancel request"
    
    return True, "Request cancelled successfully"

def search_rooms(check_in, check_out, guests=1, room_type=None, max_price=None):
    """
    Search for available rooms with filters.
    
    Args:
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        room_type: Optional room type filter
        max_price: Maximum price per night
        
    Returns:
        List of available rooms matching criteria
    """
    # Get available rooms for date range
    available_rooms = get_available_rooms(check_in, check_out, room_type)
    
    # Apply additional filters
    filtered_rooms = []
    for room in available_rooms:
        if guests and room['capacity'] < guests:
            continue
        
        if max_price and room['price'] > max_price:
            continue
        
        filtered_rooms.append(room)
    
    # Calculate total price for each room
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
    nights = (check_out_date - check_in_date).days
    
    for room in filtered_rooms:
        room['total_price'] = room['price'] * nights
        room['nights'] = nights
    
    return filtered_rooms

def get_booking_history(guest_id):
    """
    Get booking history for a guest.
    
    Args:
        guest_id: ID of the guest
        
    Returns:
        List of past bookings
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    query = '''
        SELECT b.*, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.guest_id = ?
        AND (b.check_out < ? OR b.status = 'checked_out')
        ORDER BY b.check_out DESC
    '''
    
    return db.query_db(query, [guest_id, today])

def calculate_bill(booking_id):
    """
    Calculate the total bill for a booking.
    
    Args:
        booking_id: ID of the booking
        
    Returns:
        Dictionary with bill details
    """
    # Get booking details
    booking = db.query_db(
        '''
        SELECT b.*, r.room_number, r.type, r.price
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.id = ?
        ''',
        [booking_id],
        one=True
    )
    
    if not booking:
        return None
    
    # Calculate room charge
    check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
    check_out = datetime.strptime(booking['check_out'], '%Y-%m-%d')
    nights = (check_out - check_in).days
    room_charge = nights * booking['price']
    
    # Get room service charges
    room_services = db.query_db(
        '''
        SELECT *
        FROM room_service
        WHERE booking_id = ? AND status = 'completed'
        ''',
        [booking_id]
    )
    
    # In a real system, room service items would have prices
    # For this demo, we'll use a fixed charge
    service_charge = len(room_services) * 25.0
    
    # Calculate tax (e.g., 10%)
    tax_rate = 0.1
    tax = (room_charge + service_charge) * tax_rate
    
    # Calculate total
    total = room_charge + service_charge + tax
    
    return {
        'booking': booking,
        'nights': nights,
        'room_charge': room_charge,
        'service_charge': service_charge,
        'tax': tax,
        'total': total,
        'services': room_services
    }

def get_room_details(room_id):
    """
    Get detailed information about a room.
    
    Args:
        room_id: ID of the room
        
    Returns:
        Room details or None if not found
    """
    return db.query_db(
        'SELECT * FROM rooms WHERE id = ?',
        [room_id],
        one=True
    )