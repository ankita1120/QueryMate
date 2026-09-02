from mysql_connection import get_mysql_connection
from sqlalchemy import text

engine = get_mysql_connection()

try:
    with engine.connect() as conn:

        print("Connected")

        result = conn.execute(text("SHOW TABLES"))

        print("Tables:")

        for table in result:
            print(table[0])

except Exception as e:
    print("Error:", e)