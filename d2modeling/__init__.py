from sqlalchemy.orm import sessionmaker
from d2modeling.schema import engine, DB_PATH

SessionFactory = sessionmaker(bind=engine)

import sqlite3


def get_dbapi2_conn(path=DB_PATH):
    """ Gets a connection to the current sqlite database.
        Used to extract data with raw SQL.
        We lose the ability to freely transition engines by using SQL directly.
        We save time.
    """
    conn = sqlite3.connect(path)
    return conn
