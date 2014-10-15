def get_match_row_dict(row):
    """ Given a tuple representing a row from the Match tables, return a dict. """
    return {
        "dire_score": row[0],
        "radiant_score": row[1],
        "time": row[2],
        "date": row[3],
        "winner": row[4],
        "dire_name": row[5],
        "radiant_name": row[6]
    }