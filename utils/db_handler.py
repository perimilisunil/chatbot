import sqlite3
import os

DB_NAME = "database.db"

def get_db_connection():
    """Establishes a connection to the SQLite database with WAL mode enabled."""
    conn = sqlite3.connect(DB_NAME)
    # Enable Write-Ahead Logging (WAL) to prevent locking errors with multiple users
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates necessary tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Chat Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def log_message(session_id, role, content):
    """Saves a message (User or Bot) to the database."""
    conn = get_db_connection()
    conn.execute('INSERT INTO chat_logs (user_session_id, role, content) VALUES (?, ?, ?)',
                 (session_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(session_id, limit=30):
    """Retrieves the last N messages for a specific user session (for AI Context)."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT role, content FROM chat_logs 
        WHERE user_session_id = ? 
        ORDER BY id DESC LIMIT ?
    ''', (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1] # Reverse to get chronological order (Oldest -> Newest)

def get_analytics():
    """Returns statistics for the Admin Dashboard."""
    conn = get_db_connection()
    # Count total messages
    total = conn.execute('SELECT COUNT(*) FROM chat_logs').fetchone()[0]
    # Count unique users
    users = conn.execute('SELECT COUNT(DISTINCT user_session_id) FROM chat_logs').fetchone()[0]
    conn.close()
    return {"total_messages": total, "active_users": users}

def get_all_logs():
    """Fetches the 50 most recent logs for the Admin Dashboard table."""
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM chat_logs ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    return logs

def delete_chat_log(log_id):
    """Deletes a specific chat log by ID (Used by Admin Dashboard)."""
    conn = get_db_connection()
    conn.execute('DELETE FROM chat_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()