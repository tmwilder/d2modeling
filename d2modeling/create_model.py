import json
import sys
import traceback

import d2modeling.features as features
import d2modeling.schema as schema
from d2modeling import SessionFactory, get_dbapi2_conn, get_in_memory_dbapi2_conn


def load_matches():
    session = SessionFactory()

    matches = session.query(schema.Match).order_by(schema.Match.date)
    session.close()

    conn = get_in_memory_dbapi2_conn()

    match_features = []

    for count, match in enumerate(matches):
        try:
            print("Loading feature set for match #: {} with match id: {}".format(count, match.id))
            feature_set = get_one_match_features(conn, match)
            match_features.append({"match_id": match.id, "match_features": feature_set})
        except Exception as e:
            traceback.print_stack()
            sys.stderr.write("Error while processing match: {}".format(e))

    return match_features


def get_one_match_features(conn, match):
    feature_set = features.DefaultFeatureSet(
        last_date=match.date,
        team_1=match.dire_name,
        team_2=match.radiant_name,
        conn=conn,
        matches_back=40,
        increment=20
    )
    return feature_set.as_dict()
