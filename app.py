"""
MindSense AI - Flask Backend
--------------------------------
Provides:
1. POST /signup  -> create a unique user in MySQL
2. POST /login   -> verify username/password
3. POST /chat    -> connect the existing MindSense AI model
4. GET  /health  -> test Flask + MySQL

IMPORTANT:
- Keep your MySQL password in an environment variable when possible.
- Passwords are stored as secure hashes, NOT plain text.
- Your existing MySQL database/table names are preserved.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

# Your existing chatbot model file should be renamed to:
# mindsense_ai.py
#
# It already exposes:
#     chat(message, condition=None)
#
# See your existing model: it returns success, type, message,
# condition_context, solution, detected_topics and timestamp.
from mindsense_ai import chat as ai_chat


app = Flask(__name__)
CORS(app)


# ============================================================
# MYSQL CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "YOUR_MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "mindsense"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}


def get_connection():
    """Create a new MySQL connection for one request."""
    return mysql.connector.connect(**DB_CONFIG)


def valid_username(username):
    """Basic username validation."""
    if not username:
        return False

    if len(username) < 3 or len(username) > 50:
        return False

    allowed = username.replace("_", "").replace("-", "")
    return allowed.isalnum()


def valid_password(password):
    """Require a sensible minimum password length."""
    return isinstance(password, str) and len(password) >= 6


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    connection = None
    try:
        connection = get_connection()

        if not connection.is_connected():
            return jsonify({
                "success": False,
                "message": "MySQL connection is not active."
            }), 500

        return jsonify({
            "success": True,
            "message": "MindSense server and MySQL are working."
        })

    except Error as e:
        return jsonify({
            "success": False,
            "message": "MySQL connection failed.",
            "error": str(e)
        }), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# ============================================================
# SIGN UP
# ============================================================

@app.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = data.get("password", "")

    # ---------- Validation ----------

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400

    if not valid_username(username):
        return jsonify({
            "success": False,
            "message": "User ID must be 3-50 characters and contain only letters, numbers, _ or -."
        }), 400

    if not valid_password(password):
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check uniqueness before INSERT so the user gets a clear message.
        cursor.execute(
            "SELECT id FROM users WHERE username = %s LIMIT 1",
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "This User ID already exists. Please choose another User ID."
            }), 409

        # Never store a plain-text password.
        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            """,
            (username, password_hash)
        )

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "id": user_id,
                "username": username
            }
        }), 201

    except IntegrityError as e:
        # Database UNIQUE constraint is the final protection against
        # two simultaneous requests creating the same username.
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "This User ID already exists. Please choose another User ID."
        }), 409

    except Error as e:
        if connection:
            connection.rollback()

        print("SIGNUP MYSQL ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to create the account because the database could not be reached."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please enter your User ID and password."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,)
        )

        user = cursor.fetchone()

        if not user or not check_password_hash(user["password"], password):
            return jsonify({
                "success": False,
                "message": "Invalid User ID or password."
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "username": user["username"]
            }
        })

    except Error as e:
        print("LOGIN MYSQL ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to connect to the database."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# ============================================================
# AI CHAT
# ============================================================

@app.post("/chat")
def chat_endpoint():
    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()
    condition = data.get("condition")
    user_id = data.get("user_id")

    if not message:
        return jsonify({
            "success": False,
            "message": "Please tell me a little about how you're feeling."
        }), 400

    try:
        result = ai_chat(message, condition)

        # Optional: save the detected condition/topic as history.
        # This uses the mental_health_history table supplied by you.
        if result.get("success") and user_id:
            save_history(
                user_id=user_id,
                condition=result.get("type"),
                score=None
            )

        return jsonify(result)

    except Exception as e:
        print("CHAT ERROR:", e)

        return jsonify({
            "success": False,
            "message": "The AI assistant could not generate a response right now."
        }), 500


def save_history(user_id, condition, score=None):
    """Save a simple wellness-history record when a valid user_id is supplied."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO mental_health_history (user_id, score, `condition`)
            SELECT %s, %s, %s
            WHERE EXISTS (
                SELECT 1 FROM users WHERE id = %s
            )
            """,
            (user_id, score, condition, user_id)
        )

        connection.commit()

    except Error as e:
        # Chat should still work even if optional history storage fails.
        print("HISTORY MYSQL ERROR:", e)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MindSense AI Flask Server")
    print("=" * 60)
    print("Signup : http://127.0.0.1:5000/signup")
    print("Login  : http://127.0.0.1:5000/login")
    print("Chat   : http://127.0.0.1:5000/chat")
    print("Health : http://127.0.0.1:5000/health")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
