from d2modeling.feature_classes import Feature, FeatureSet
from d2modeling.schema import get_dbapi2_conn


class LastNMatchesFeature(Feature):

    def _construct(self, team_name, n_matches):
        self._load_matches(team_name, n_matches)

    def _load_matches(self, team_name, n_matches):
        conn = get_dbapi2_conn()
        cursor = conn.cursor()
        sql = (
        "SELECT "
            "dire_score, radiant_score, time, date, winner, dire_name, radiant_name "
        "FROM "
            "match "
        "WHERE "
            "dire_name = ? or "
            "radiant_name = ? "
        "ORDER BY "
            "date desc "
        "LIMIT"
            "? "
        )
        data = (team_name, team_name, n_matches)
        cursor.execute(sql, data)
        rows = cursor.fetchall()
        self.matches = [self._get_row_dict(row) for row in rows]

    def _get_row_dict(self, row):
        return {
            "dire_score": row[0],
            "radiant_score": row[1],
            "time": row[2],
            "date": row[3],
            "winner": row[4],
            "dire_name": row[5],
            "radiant_name": row[6]
        }


class MatchWinLossPercentage(LastNMatchesFeature):
    def _construct(self, team_name, n_matches):
        super(MatchWinLossPercentage, self)._construct(team_name, n_matches)

        wins = 0
        losses = 0

        for match in self.matches:
            winner = match["winner"]
            radiant_name = match["radiant_name"]

            if winner == "RADIANT" and radiant_name == team_name:
                wins += 1
            elif winner == "DIRE" and radiant_name != team_name:
                wins += 1
            else:
                losses += 1

        percentage = float(wins)/(wins + losses)
        # If we run into memory problems, we can call del self.matches here. Not doing now for debug reasons.
        return percentage

