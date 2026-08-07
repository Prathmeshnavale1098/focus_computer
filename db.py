import os
import mysql.connector

print("HOST:", os.getenv("MYSQLHOST"))
print("PORT:", os.getenv("MYSQLPORT"))
print("USER:", os.getenv("MYSQLUSER"))
print("DB:", os.getenv("MYSQLDATABASE"))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),   # <-- changed
       port = int(os.getenv("MYSQLPORT", 3306))
    )
