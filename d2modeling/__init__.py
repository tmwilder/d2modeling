from sqlalchemy.orm import sessionmaker
from d2modeling.schema import engine, DB_PATH

SessionFactory = sessionmaker(bind=engine)

import sqlite3
from StringIO import StringIO


def get_dbapi2_conn(path=DB_PATH):
    """ Gets a connection to the current sqlite database.
        Used to extract data with raw SQL.
        We lose the ability to freely transition engines by using SQL directly.
        We save time.
    """
    conn = sqlite3.connect(path)
    return conn


def get_in_memory_dbapi2_conn():
    """ Modified from Cenk Alti's answer in http://stackoverflow.com/questions/3850022/python-sqlite3-load-existing-db-file-to-memory """
    # Read database to tempfile
    conn = get_dbapi2_conn()
    tempfile = StringIO()
    for line in conn.iterdump():
        tempfile.write('%s\n' % line)
    conn.close()
    tempfile.seek(0)

    # Create a database in memory and import from tempfile
    mem_conn = sqlite3.connect(":memory:")
    mem_conn.cursor().executescript(tempfile.read())
    mem_conn.commit()
    return mem_conn
