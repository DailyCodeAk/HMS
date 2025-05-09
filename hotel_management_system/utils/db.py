import sqlite3
import os
from flask import g, current_app

# Database file path
DATABASE = 'hotel.db'

def get_db():
    """
    Connect to the database.
    Returns a database connection with row factory set to sqlite3.Row.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(exception=None):
    """
    Close the database connection at the end of the request.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initialize the database with schema.
    Creates tables if they don't exist.
    """
    with current_app.app_context():
        db = get_db()
        try:
            with current_app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            return True, "Database initialized successfully"
        except sqlite3.Error as e:
            return False, f"Database initialization error: {str(e)}"

def query_db(query, args=(), one=False):
    """
    Execute a query and return the results.
    Args:
        query: SQL query to execute
        args: Parameters for the query
        one: If True, returns only the first result or None
    Returns:
        Results as sqlite3.Row objects
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=True):
    """
    Execute a query without returning results.
    Useful for INSERT, UPDATE, DELETE operations.
    Args:
        query: SQL query to execute
        args: Parameters for the query
        commit: Whether to commit the transaction
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_db()
        db.execute(query, args)
        if commit:
            db.commit()
        return True
    except sqlite3.Error as e:
        if commit:
            db.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        return False

def insert_db(table, data, commit=True):
    """
    Insert data into a table.
    Args:
        table: Table name
        data: Dictionary of column_name: value pairs
        commit: Whether to commit the transaction
    Returns:
        ID of the inserted row if successful, None otherwise
    """
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, list(data.values()))
        
        if commit:
            db.commit()
        
        return cursor.lastrowid
    except sqlite3.Error as e:
        if commit:
            db.rollback()
        current_app.logger.error(f"Insert error: {str(e)}")
        return None

def update_db(table, data, condition, condition_params=(), commit=True):
    """
    Update data in a table.
    Args:
        table: Table name
        data: Dictionary of column_name: value pairs to update
        condition: WHERE clause of the update statement
        condition_params: Parameters for the condition
        commit: Whether to commit the transaction
    Returns:
        Number of rows affected if successful, None otherwise
    """
    try:
        set_clause = ', '.join([f"{column} = ?" for column in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        params = list(data.values()) + list(condition_params)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        
        if commit:
            db.commit()
        
        return cursor.rowcount
    except sqlite3.Error as e:
        if commit:
            db.rollback()
        current_app.logger.error(f"Update error: {str(e)}")
        return None

def delete_db(table, condition, condition_params=(), commit=True):
    """
    Delete data from a table.
    Args:
        table: Table name
        condition: WHERE clause of the delete statement
        condition_params: Parameters for the condition
        commit: Whether to commit the transaction
    Returns:
        Number of rows affected if successful, None otherwise
    """
    try:
        query = f"DELETE FROM {table} WHERE {condition}"
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, condition_params)
        
        if commit:
            db.commit()
        
        return cursor.rowcount
    except sqlite3.Error as e:
        if commit:
            db.rollback()
        current_app.logger.error(f"Delete error: {str(e)}")
        return None

def check_db_exists():
    """
    Check if the database file exists.
    Returns:
        True if database exists, False otherwise
    """
    return os.path.exists(DATABASE)

def create_transaction():
    """
    Start a database transaction.
    Returns:
        Database connection object
    """
    db = get_db()
    return db

def commit_transaction(db):
    """
    Commit a database transaction.
    Args:
        db: Database connection object
    """
    db.commit()

def rollback_transaction(db):
    """
    Rollback a database transaction.
    Args:
        db: Database connection object
    """
    db.rollback()

def backup_database(backup_file):
    """
    Create a backup of the database.
    Args:
        backup_file: Path to save the backup
    Returns:
        True if successful, False otherwise
    """
    try:
        source = get_db()
        destination = sqlite3.connect(backup_file)
        
        source.backup(destination)
        destination.close()
        return True
    except sqlite3.Error as e:
        current_app.logger.error(f"Backup error: {str(e)}")
        return False

def table_exists(table_name):
    """
    Check if a table exists in the database.
    Args:
        table_name: Name of the table to check
    Returns:
        True if the table exists, False otherwise
    """
    result = query_db(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        [table_name],
        one=True
    )
    return result is not None

def get_column_names(table_name):
    """
    Get column names for a table.
    Args:
        table_name: Name of the table
    Returns:
        List of column names if successful, None otherwise
    """
    try:
        cursor = get_db().cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        cursor.close()
        return [column['name'] for column in columns]
    except sqlite3.Error as e:
        current_app.logger.error(f"Error getting columns: {str(e)}")
        return None