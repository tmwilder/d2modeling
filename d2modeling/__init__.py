from sqlalchemy.orm import sessionmaker
from d2modeling.schema import engine

SessionFactory = sessionmaker(bind=engine)