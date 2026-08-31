import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="mindsense"
)

print("MySQL connected successfully!")

connection.close()