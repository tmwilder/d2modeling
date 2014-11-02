import math

from d2modeling import get_dbapi2_conn
from d2modeling.utils import get_match_row_dict


def update_all(conn=None, starting_elo=1200):
    if conn is None:
        conn = get_dbapi2_conn()

    cursor = conn.cursor()

    matches = cursor.execute("SELECT * FROM match ORDER BY date ASC").fetchall()

    if matches:
        cursor.execute("update team set elo = ?", (starting_elo,))
        match_rows = [get_match_row_dict(row) for row in matches]

        elo_query = "select elo from team where name = ?"
        update_elo_query = "update team set elo = ? where name = ?" 
        update_match_elo_query = (
            "UPDATE "
              "match "
            "SET "
              "dire_elo = "
                "CASE WHEN dire_name = ? THEN ? ELSE ? END, "
              "radiant_elo = "
                "CASE WHEN radiant_name = ? THEN ? ELSE ? END "
            "WHERE "
              "id = ?"
        )

        for match in match_rows:

            dire_name = match["dire_name"]
            radiant_name = match["radiant_name"]
            winner = match["winner"]
            match_id = match["match_id"]

            radiant_elo = cursor.execute(elo_query, (radiant_name,)).fetchone()[0]
            dire_elo = cursor.execute(elo_query, (dire_name,)).fetchone()[0]

            radiant_new, dire_new = _get_new_elos(radiant_elo, dire_elo, winner)

            cursor.execute(update_elo_query, (radiant_new, radiant_name))
            cursor.execute(update_elo_query, (dire_new, dire_name))
            cursor.execute(update_match_elo_query,
                (dire_name, dire_new, radiant_new, radiant_name, radiant_new, dire_new, match_id)
            )
        conn.commit()


def _get_new_elos(radiant_elo, dire_elo, match_winner, k_val=32):
    radiant_expected = _get_expected(radiant_elo, dire_elo)
    dire_expected = _get_expected(dire_elo, radiant_elo)

    if match_winner == "RADIANT":
        radiant_outcome = 1
        dire_outcome = 0
    else:
        # Draws are impossible.
        radiant_outcome = 0
        dire_outcome = 1

    radiant_new = radiant_elo + math.ceil(k_val * (radiant_outcome - radiant_expected))
    dire_new = dire_elo + math.ceil(k_val * (dire_outcome - dire_expected))
    return int(radiant_new), int(dire_new)


def _get_expected(team_1_elo, team_2_elo):
    return 1.0 / (1 + 10 ** ((team_2_elo - team_1_elo) / 400.0))

