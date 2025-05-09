# Walnut Mercury Hotel Management System

A comprehensive hotel management system built with Flask that helps manage hotel operations including guest bookings, room management, housekeeping, and inventory control.

## Features

- User Authentication (Admin and Guest)
- Room Booking Management
- Housekeeping Task Assignment
- Inventory Management
- Room Service Requests
- Employee Management
- Guest Management

## Prerequisites

- Python 3.x
- Flask
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/walnut-mercury-hotel.git
cd walnut-mercury-hotel
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

3. Default admin credentials:
   - Username: admin
   - Password: admin123

## Project Structure

```
hotel_management_system/
├── app.py              # Main application file
├── schema.sql          # Database schema
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS, images)
└── templates/         # HTML templates
    ├── admin/        # Admin interface templates
    └── user/         # User interface templates
```

## Security Note

This is a development version. For production:
1. Change the secret key in app.py
2. Use proper password hashing
3. Implement proper security measures
4. Use environment variables for sensitive data

## License

MIT License 