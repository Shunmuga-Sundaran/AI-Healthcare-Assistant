"""MySQL storage for interactions using mysql-connector-python.

Credentials come from environment variables. All SQL uses parameterized
queries (%s placeholders), never string formatting. Passwords are never
printed or logged, and this module never tries other credentials.
"""

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class DatabaseError(Exception):
    """Raised when a database operation fails. Message is safe to show."""


def get_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306") or 3306),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "healthcare_assistant_db"),
        "connection_timeout": 5,
    }


def get_connection():
    """Open a new connection or raise DatabaseError with a friendly message."""
    config = get_config()
    if not config["user"] or config["user"] == "your_mysql_username":
        raise DatabaseError(
            "MySQL is not configured. Set DB_USER and DB_PASSWORD in your .env file."
        )
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as exc:
        errno = getattr(exc, "errno", None)
        if errno == 1045:
            msg = "MySQL rejected the username or password. Please update DB_USER / DB_PASSWORD in your .env file."
        elif errno == 1049:
            msg = "The database does not exist. Run database/schema.sql first (see README)."
        elif errno in (2003, 2002):
            msg = "Could not connect to the MySQL server. Make sure MySQL is running and DB_HOST / DB_PORT are correct."
        else:
            msg = "Could not connect to MySQL. Please check your database settings."
        raise DatabaseError(msg) from None  # 'from None' avoids leaking details


INSERT_SQL = "INSERT INTO interactions (user_input, ai_response) VALUES (%s, %s)"
SELECT_SQL = (
    "SELECT id, user_input, ai_response, created_at "
    "FROM interactions ORDER BY created_at DESC, id DESC LIMIT %s"
)


def save_interaction(user_input: str, ai_response: str, connection=None) -> int:
    """Insert one interaction and return its new id."""
    own_connection = connection is None
    conn = connection or get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(INSERT_SQL, (user_input, ai_response))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error:
        raise DatabaseError(
            "Could not save the interaction. Check that the 'interactions' table exists (see README)."
        ) from None
    finally:
        if cursor is not None:
            cursor.close()
        if own_connection:
            conn.close()


def get_history(limit: int = 20, connection=None) -> list:
    """Return the most recent interactions as a list of dictionaries."""
    own_connection = connection is None
    conn = connection or get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(SELECT_SQL, (int(limit),))
        return cursor.fetchall()
    except mysql.connector.Error:
        raise DatabaseError(
            "Could not read the history. Check that the 'interactions' table exists (see README)."
        ) from None
    finally:
        if cursor is not None:
            cursor.close()
        if own_connection:
            conn.close()


def is_available() -> bool:
    """True if a connection can be opened right now."""
    try:
        conn = get_connection()
    except DatabaseError:
        return False
    conn.close()
    return True
