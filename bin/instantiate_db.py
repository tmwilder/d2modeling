import os
from d2modeling.schema import Base, engine, DB_NAME

if DB_NAME.split(':')[0] == 'sqlite':
    try:
        os.remove(DB_NAME.split('/', 3)[-1])
    except OSError:
        pass

Base.metadata.create_all(engine)
