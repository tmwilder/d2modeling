import os
from d2modeling.schema import Base, engine, DB_NAME, DB_PATH


def main():
    if DB_NAME.split(':')[0] == 'sqlite':
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
