from os.path import abspath as ap, dirname as dn

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()
DB_PATH = '{0}/d2modeling.db'.format(dn(dn(ap(__file__))))
DB_NAME = 'sqlite:///{0}'.format(DB_PATH)
engine = create_engine(DB_NAME)
Base.metadata.bind = engine


class Team(Base):
    __tablename__ = 'team'
    name = Column(String(250), primary_key=True)
    elo = Column(Float, default=1200)


class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    dire_score = Column(Integer)
    radiant_score = Column(Integer)
    time = Column(Float)
    date = Column(Date)
    winner = Column(String(250))
    dire_name = Column(String(250), ForeignKey('team.name'))
    radiant_name = Column(String(250), ForeignKey('team.name'))

    radiant = relationship("Team", foreign_keys=[radiant_name])
    dire = relationship("Team", foreign_keys=[dire_name])
