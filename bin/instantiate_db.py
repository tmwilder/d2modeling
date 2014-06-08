from sqlalchemy import create_engine
from d2modeling.schema import Base

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('dbpath', help='Path at which you want to instantiate the db', default='sqlite:///d2modeling.db')
args = parser.parse_args()

engine = create_engine(args.dbpath)
Base.metadata.create_all(engine)

