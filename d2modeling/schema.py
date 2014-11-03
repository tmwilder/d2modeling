from os.path import abspath as ap, dirname as dn

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float, Text, DateTime
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
    date = Column("date", Date, index=True)
    winner = Column("winner", String(250))
    dire_name = Column("dire_name", String(250), ForeignKey('team.name'), index=True)
    radiant_name = Column("radiant_name", String(250), ForeignKey('team.name'), index=True)
    match_data = Column("match_data", Text)
    dire_elo = Column("dire_elo", Integer, default=1200)
    radiant_elo = Column("radiant_elo", Integer, default=1200)

    radiant = relationship("Team", foreign_keys=[radiant_name])
    dire = relationship("Team", foreign_keys=[dire_name])


class BetMatch(Base):
    __tablename__ = 'bet_match'
    # TODO, make unique super key add add cron logic somewhere in app to get this data regularly.
    id = Column("id", Integer, primary_key=True)
    team_1_name = Column("team_2_name", String(250))
    team_2_name = Column("team_1_name", String(250))
    team_1_odds = Column("team_1_odds", Integer)
    team_2_odds = Column("team_2_odds", Integer)
    tournament = Column("tournament", String(250))
    date_time = Column("date_time", DateTime())
