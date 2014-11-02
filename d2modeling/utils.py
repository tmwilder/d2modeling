import json


def get_match_row_dict(row):
    """ Given a tuple representing a row from the Match tables, return a dict. """

    if row[8] is not None:
        match_json = json.loads(row[8])
    else:
        match_json = None

    return {
        "match_id": row[0],
        "dire_score": row[1],
        "radiant_score": row[2],
        "time": row[3],
        "date": row[4],
        "winner": row[5],
        "dire_name": row[6],
        "radiant_name": row[7],
        "match_data": match_json,
        "dire_elo": row[9],
        "radiant_elo": row[10]
    }
