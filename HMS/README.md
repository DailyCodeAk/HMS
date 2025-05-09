# Hotel Management System

## Overview
The Hotel Management System (HMS) is a web application built using Flask that allows for the management of hotel operations, including user registration, booking management, and administrative functionalities.

## Features
- User registration and login
- Admin dashboard with statistics
- Management of guests, employees, and inventory
- Room booking and service requests
- Housekeeping task assignments

## Project Structure
```
HMS
├── app.py                     # Main application file
├── templates                  # HTML templates for the application
│   ├── admin                  # Admin-related templates
│   ├── user                   # User-related templates
│   └── index.html             # Homepage template
├── static                     # Static files (CSS, JS, assets)
│   ├── css                    # Stylesheets
│   ├── js                     # JavaScript files
│   └── assets                 # Additional static assets
├── schema.sql                 # Database schema
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd HMS
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   The database will be initialized automatically when you run the application for the first time.

4. **Run the application:**
   ```
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Usage
- Access the homepage to navigate to user or admin functionalities.
- Admins can log in to manage guests, employees, and inventory.
- Users can register, log in, and manage their bookings.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.