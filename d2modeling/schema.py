from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
DB_NAME = 'sqlite:///d2modeling.db'

class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    dire_score = Column(Integer)
    radiant_score = Column(Integer)
    time = Column(String(250))
    date = Column(Date)
    winner = Column(String(250))
    dire_id = Column(Integer, ForeignKey('team.id'))
    radiant_id = Column(Integer, ForeignKey('team.id'))

    radiant = relationship("Team", foreign_keys=[radiant_id])
    dire = relationship("Team", foreign_keys=[dire_id])
