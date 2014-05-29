import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

DB_NAME = 'sqlite:///d2modeling.db'

 
class Team(Base):
    __tablename__ = 'team'
    # Stolen from sqlalchemy tutorial @http://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
    # Here we define columns for the table team
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

 
class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    match_id = Column(String)
    number_games = Column(Integer)
    dire_score = Column(Integer)
    radiant_score = Column(Integer)
    round = Column(String(250))

    time = Column(String(250))
    tournament = Column(String(250))
    date = Column(Date)
    winner = Column(String(250))

    dire_id = Column(Integer, ForeignKey('team.id'))
    radiant_id = Column(Integer, ForeignKey('team.id'))

    radiant = relationship("Team", foreign_keys=[radiant_id])
    dire = relationship("Team", foreign_keys=[dire_id])


if __name__ == '__main__':
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine(DB_NAME)
     
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
