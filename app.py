from flask import Flask, request, jsonify, session, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Used to keep the student logged in
app.secret_key = "mindsense-secret-key-change-this"


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="mindsense"
    )
    return connection


@app.route("/")
def home():
    return redirect(url_for("index"))


@app.route("/index.html")
def index():
    return app.send_static_file("index.html")


@app.route("/login.html")
def login_page():
    return app.send_static_file("login.html")


@app.route("/signup.html")
def signup_page():
    return app.send_static_file("signup.html")


# -------------------------
# SIGN UP
# -------------------------
@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please enter User ID and password."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether username already exists
    cursor.execute(
        "SELECT id FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()

        return jsonify({
            "success": False,
            "message": "User ID already exists. Please choose another."
        }), 409

    # Never store the actual password
    password_hash = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Account created successfully!"
    })


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please enter User ID and password."
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        return jsonify({
            "success": False,
            "message": "User ID or password is incorrect."
        }), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({
            "success": False,
            "message": "User ID or password is incorrect."
        }), 401

    # Save logged-in user in Flask session
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return jsonify({
        "success": True,
        "message": "Login successful!"
    })


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# -------------------------
# CHECK CURRENT USER
# -------------------------
@app.route("/current-user")
def current_user():

    if "user_id" not in session:
        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "username": session["username"]
    })


# -------------------------
# TEST MYSQL
# -------------------------
@app.route("/test-db")
def test_db():

    connection = get_db_connection()

    if connection.is_connected():
        connection.close()
        return "MySQL connected successfully!"

    return "MySQL connection failed!"


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "mindsense"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400

    password_hash = generate_password_hash(password)

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            """,
            (username, password_hash)
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "success": True,
            "message": "Account created successfully!"
        })

    except mysql.connector.IntegrityError:
        return jsonify({
            "success": False,
            "message": "User ID already exists."
        }), 409

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database error."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)