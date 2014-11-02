from os.path import abspath as ap, dirname as dn

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float, Text
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
    name = Column("name", String(250), primary_key=True)
    elo = Column("elo", Float, default=1200)


class Match(Base):
    __tablename__ = 'match'

    id = Column("id", Integer, primary_key=True)
    dire_score = Column("dire_score", Integer)
    radiant_score = Column("radiant_score", Integer)
    time = Column("time", Float)
    date = Column("date", Date)
    winner = Column("winner", String(250))
    dire_name = Column("dire_name", String(250), ForeignKey('team.name'))
    radiant_name = Column("radiant_name", String(250), ForeignKey('team.name'))
    match_data = Column("match_data", Text)
    dire_elo = Column("dire_elo", Integer, default=1200)
    radiant_elo = Column("radiant_elo", Integer, default=1200)

    radiant = relationship("Team", foreign_keys=[radiant_name])
    dire = relationship("Team", foreign_keys=[dire_name])
