from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schema import Team, Base, Match, DB_NAME


def get_session():
    engine = create_engine(DB_NAME)
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()
    return session


def insert_match(session, match):
    if not session.query(Match).filter_by(match_id=match['match']).all():
        radiant_name = match['radiant']
        dire_name = match['dire']

        radiant = session.query(Team).filter_by(name=radiant_name).all()
        if not radiant:
            radiant = Team(name=radiant_name)
            session.add(radiant)
            session.commit()
            radiant = session.query(Team).filter_by(name=radiant_name).all()[0]
        else:
            radiant = radiant[0]

        dire = session.query(Team).filter_by(name=dire_name).all()
        if not dire:
            dire = Team(name=dire_name)
            session.add(dire)
            session.commit()
            dire = session.query(Team).filter_by(name=dire_name).all()[0]
        else:
            dire = dire[0]

        match_obj = Match(
            match_id=match['match'],
            number_games=match['game'],
            dire_id=dire.id,
            dire_score=match['dire_score'],
            radiant_id=radiant.id,
            radiant_score=match['radiant_score'],
            round=match['round'],
            time=match['time'],
            tournament=match['tournament'],
            date=match['date'],
            winner=match['winner']
        )
        session.add(match_obj)

        session.commit()
