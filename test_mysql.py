from mysql_connection import get_mysql_connection


engine = get_mysql_connection()

try:
    with engine.connect() as conn:
        print("MySQL Connected Successfully ✅")

except Exception as e:
    print("Error:", e)