from d2modeling.feature_classes import Feature, FeatureSet
from d2modeling import get_dbapi2_conn


class LastNMatchesFeature(Feature):

    def _construct(self, team_name, n_matches, conn=None):
        self._load_matches(team_name, n_matches, conn)

    def _load_matches(self, team_name, n_matches, conn=None):
        if conn is None:
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
        "LIMIT "
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
    def _construct(self, team_name, n_matches, conn=None):
        super(MatchWinLossPercentage, self)._construct(team_name, n_matches, conn)

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


class DefaultFeatureSet(FeatureSet):
    def __init__(self, team_1, team_2, conn):
        self.features = []

        for team_name in (team_1, team_2):
            for x in range(5, 16, 5):
                f = MatchWinLossPercentage(
                    name='last_{}_matches_team_{}'.format(x, team_name),
                    team_name=team_name,
                    n_matches=x,
                    conn=conn
                )
                self.features.append(f)
        super(DefaultFeatureSet, self).__init__(team_1, team_2, conn)
