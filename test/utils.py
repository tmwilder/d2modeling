import random
import os
import datetime
import copy
import json
from datetime import timedelta
import sqlite3

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

import d2modeling.schema as schema


class DatabaseTest(object):
    """
        Creates and wipes a fresh test db for each test.
        We can afford the overhead until we have many more tests.

    """
    def setUp(self):
        self.db_path = 'd2modeling.db'
        self.engine = create_engine('sqlite:///{}'.format(self.db_path))
        schema.Base.metadata.bind = self.engine
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        schema.Base.metadata.create_all(self.connection)
        abspath = os.path.realpath(self.db_path)
        self.db_api_2_conn = sqlite3.connect(abspath)
        self.session = Session(self.connection)

    def tearDown(self):
        self.session.close()
        self.connection.close()
        self.engine.dispose()
        self.db_api_2_conn.close()
        os.remove(self.db_path)


def random_date(start=datetime.datetime(year=2014, month=1, day=1),
                end=datetime.datetime(year=2014, month=9, day=1)):
    """
    Credit: http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates

    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def populate(session,
             seed=0,
             team_names=("a", "b", "c", "d", "e"),
             winners=("DIRE", "RADIANT")):
    random.seed(seed)

    for team in team_names:
        team = schema.Team(name=team)
        session.add(team)

    id_count = 0
    for t1 in team_names:
        for t2 in team_names:
            if t1 != t2:
                match = schema.Match(
                    id=id_count,
                    dire_score=random.randint(0, 20),
                    radiant_score=random.randint(0, 20),
                    time=random.random()*1000,
                    date=random_date(),
                    winner=winners[random.randint(0, 1)],
                    dire_name=t1,
                    radiant_name=t2,
                    match_data=json.dumps({"players": _get_random_player_data()})
                )
                session.add(match)
                id_count += 1
    session.commit()


def _get_random_player_data():
    players = []
    for team in (0, 128):
        for x in range(5):
            traits = {
                "kills": random.randint(1, 20),
                "deaths": random.randint(1, 20),
                "assists": random.randint(1, 20),
                "leaver_status": random.randint(0, 5),
                "gold": random.randint(1, 5000),
                "last_hits": random.randint(1, 300),
                "denies": random.randint(1, 100),
                "gold_per_min": random.randint(1, 500),
                "xp_per_min": random.randint(1, 500),
                "gold_spent": random.randint(1, 15000),
                "hero_damage": random.randint(1, 20000),
                "tower_damage": random.randint(1, 5000),
                "hero_healing": random.randint(1, 2000),
                "level": random.randint(1, 18),
            }
            traits["player_slot"] = random.randint(0, 127) + team
            players.append(traits)
    return players