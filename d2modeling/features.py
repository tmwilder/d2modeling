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


class KillPercentage(LastNMatchesFeature):
    def _construct(self, team_name, n_matches, conn=None):
        super(KillPercentage, self)._construct(team_name, n_matches, conn)

        kills = 0
        deaths = 0

        for match in self.matches:
            radiant_score = match["radiant_score"]
            radiant_name = match["radiant_name"]

            dire_score = match["dire_score"]
            dire_name = match["dire_name"]

            if team_name == "dire_name":
                kills += dire_score
                deaths += radiant_score
            else:
                kills += radiant_score
                deaths += dire_score

        if kills + deaths == 0:
            kills_over_kill_deaths = 1
        else:
            kills_over_kill_deaths = float(kills)/(kills + deaths)

        return kills_over_kill_deaths


class AverageGameDuration(LastNMatchesFeature):
    def _construct(self, team_name, n_matches, conn=None):
        super(AverageGameDuration, self)._construct(team_name, n_matches, conn)

        matches = len(self.matches)
        time = 0.0

        for match in self.matches:
            time += match["time"]

        return  time/matches


class DefaultFeatureSet(FeatureSet):
    def __init__(self, team_1, team_2, conn):
        self.features = []

        for team_name in (team_1, team_2):
            for x in range(5, 41, 5):
                wlp = MatchWinLossPercentage(
                    name='win_percentage_last_{}_team_{}'.format(x, team_name),
                    team_name=team_name,
                    n_matches=x,
                    conn=conn
                )
                self.features.append(wlp)

                kp = KillPercentage(
                    name='kill_percentage_last_{}_team_{}'.format(x, team_name),
                    team_name=team_name,
                    n_matches=x,
                    conn=conn
                )
                self.features.append(kp)

                agd = AverageGameDuration(
                    name='average_game_duration_last_{}_team_{}'.format(x, team_name),
                    team_name=team_name,
                    n_matches=x,
                    conn=conn
                )
                self.features.append(agd)

        super(DefaultFeatureSet, self).__init__(team_1, team_2, conn)
