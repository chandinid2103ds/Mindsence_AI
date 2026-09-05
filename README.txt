# MindSense Account / MySQL Fix

## Why the old Create Account button did not work

The browser code was calling:

    POST http://127.0.0.1:5000/signup

but the supplied files did not include the Flask `/signup` route.

This package adds that backend route and connects it to MySQL.

## Project arrangement

Put the files into your project like this:

MindSense_AI/
    index.html
    login.html
    signup.html
    js/
        signup.js
        login.js
    backend/
        app.py
        mindsense_ai.py
        test_mysql.py
    sql/
        test-db.sql
    requirements.txt

Rename your existing MindSense chatbot Python file to:

    mindsense_ai.py

The existing model already provides:

    chat(message, condition=None)

## 1. Install packages

Open Command Prompt / PowerShell in the backend folder:

    pip install -r ../requirements.txt

Or:

    python -m pip install Flask flask-cors mysql-connector-python Werkzeug

## 2. Create the database

Open MySQL Workbench or MySQL Command Line and run:

    source sql/test-db.sql

Or copy the SQL from sql/test-db.sql into MySQL Workbench.

## 3. Configure MySQL password

Open backend/app.py.

Find:

    "password": os.getenv("MYSQL_PASSWORD", "YOUR_MYSQL_PASSWORD"),

Replace YOUR_MYSQL_PASSWORD with your actual MySQL root password.

For example:

    "password": os.getenv("MYSQL_PASSWORD", "mypassword"),

Do not use the literal text YOUR_MYSQL_PASSWORD unless that is actually your MySQL password.

## 4. Test MySQL first

In backend/test_mysql.py set:

    MYSQL_PASSWORD = "your_real_mysql_password"

Then run:

    python test_mysql.py

Expected:

    MySQL connected successfully!

## 5. Start Flask

From the backend folder:

    python app.py

Expected routes:

    http://127.0.0.1:5000/health
    http://127.0.0.1:5000/signup
    http://127.0.0.1:5000/login
    http://127.0.0.1:5000/chat

Open this in your browser:

    http://127.0.0.1:5000/health

You should see a success JSON response.

## 6. Open the website

Open signup.html using your normal local website setup.

Create a User ID, for example:

    chandini01

Create a password with at least 6 characters.

The account will be inserted into:

    mindsense.users

## Unique User ID

The database already has:

    username VARCHAR(50) UNIQUE NOT NULL

The backend also checks before INSERT.

Therefore:

    chandini01
    chandini01

cannot create two accounts.

## Password storage

The backend does NOT save the original password.

It stores a secure password hash in the existing password column.

When logging in, the hash is checked against the entered password.

This is the correct approach even though the database column is named `password`.

## Important

Do not run the old signup.js twice.

Your message contained the same JavaScript block twice. Keep only one copy in:

    js/signup.js
