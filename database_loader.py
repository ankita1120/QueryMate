"""
database_loader.py

QueryMate AI
Database Loader

Supports:
- PostgreSQL
- MySQL
"""

import pandas as pd
from sqlalchemy import create_engine


class DatabaseLoader:

    def __init__(
        self,
        db_type,
        host,
        port,
        database,
        username,
        password
    ):

        if db_type == "PostgreSQL":

            self.connection_string = (
                f"postgresql+psycopg2://"
                f"{username}:{password}"
                f"@{host}:{port}/{database}"
            )

        elif db_type == "MySQL":

            self.connection_string = (
                f"mysql+pymysql://"
                f"{username}:{password}"
                f"@{host}:{port}/{database}"
            )

        else:

            raise ValueError(
                "Unsupported database type."
            )

    def load_table(self, query):

        try:

            engine = create_engine(
                self.connection_string
            )

            with engine.connect() as connection:

                df = pd.read_sql(
                    query,
                    connection
                )

            return df

        except Exception as e:

            raise Exception(
                f"Database connection failed:\n{e}"
            )