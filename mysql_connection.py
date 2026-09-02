from sqlalchemy import create_engine


MYSQL_USER = "root"
MYSQL_PASSWORD = "Ankita1120%40%23"
MYSQL_HOST = "localhost"


# Connect only to MySQL server (no database)
def get_mysql_server_connection():

    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}"
    )

    return engine



# Connect to selected database
def get_mysql_connection(database_name):

    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{database_name}"
    )

    return engine