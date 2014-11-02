import json


def get_match_row_dict(row):
    """ Given a tuple representing a row from the Match tables, return a dict. """
    return {
        "match_id": row[0],
        "dire_score": row[1],
        "radiant_score": row[2],
        "time": row[3],
        "date": row[4],
        "winner": row[5],
        "dire_name": row[6],
        "radiant_name": row[7],
        "match_data": json.loads(row[8]),
        "dire_elo": row[9],
        "radiant_elo": row[10]
    }
