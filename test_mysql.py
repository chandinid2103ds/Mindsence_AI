import mysql.connector
from mysql.connector import Error

# CHANGE THIS to your actual MySQL root password.
MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=MYSQL_PASSWORD,
        database="mindsense"
    )

    if connection.is_connected():
        print("MySQL connected successfully!")

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        print("Database:", cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM users;")
        print("Users:", cursor.fetchone()[0])

        cursor.close()

except Error as e:
    print("MySQL connection failed:")
    print(e)

finally:
    if "connection" in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")
