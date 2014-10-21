from d2modeling.feature_classes import Feature, FeatureSet
from d2modeling.utils import get_match_row_dict
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
            "dire_score, radiant_score, time, date, winner, dire_name, radiant_name, match_data "
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
        self.matches = [get_match_row_dict(row) for row in rows]


class SteamMatchDataFeature(LastNMatchesFeature):
    """ Class provides a DRY way of parsing sides on steam API match data. """
    def _get_player_side_from_int(self, player_slot_int):
        """ The match data blob uses an 8 bit unsigned int to represent side/player slot.
            The first bit represents side.
        """
        assert([player_slot_int < 256])
        if player_slot_int < 128:
            return "RADIANT"
        else:
            return "DIRE"

    def _get_players_by_sides(self, match_data):
        radiant_players = []
        dire_players = []
        for player in match_data["players"]:
            if self._get_player_side_from_int(player["player_slot"]) == "DIRE":
                radiant_players.append(player)
            else:
                dire_players.append(player)
        return radiant_players, dire_players

    def _get_friendly_and_enemy_players(self, team_name, match):
        """ Takes full data row that contains "match_data" key. I.E. top level data. """
        dire_players, radiant_players = self._get_players_by_sides(match["match_data"])
        radiant_name = match["radiant_name"]
        dire_name = match["dire_name"]

        if team_name == radiant_name:
            friendly_players = radiant_players
            enemy_players = dire_players
        elif team_name == dire_name:
            friendly_players = dire_players
            enemy_players = radiant_players
        else:
            raise(ValueError(
                "team_name: {} didn't match dire_name: {} or radiant_name: {} for match_id: {}".format(
                    team_name,
                    dire_name,
                    radiant_name,
                    match["match_id"]
                )
            ))

        return friendly_players, enemy_players

    def _get_team_wide_average(self, players):
        traits_to_average = {
            "kills": [],
            "deaths": [],
            "assists": [],
            "leaver_status": [],
            "gold": [],
            "last_hits": [],
            "denies": [],
            "gold_per_min": [],
            "xp_per_min": [],
            "gold_spent": [],
            "hero_damage": [],
            "tower_damage": [],
            "hero_healing": [],
            "level": []
        }
        for player in players:
            for key in traits_to_average.keys():
                if key == "leaver_status":
                    # Special case, status indicates if abandoned game, 0 or 1 == !abandoned.
                    if player[key] in (0, 1):
                        status = 0
                    else:
                        status = 1
                    traits_to_average["leaver_status"].append(status)
                    continue
                traits_to_average[key].append(player[key])

        for key, value in traits_to_average.items():
            traits_to_average[key] = sum(value)/5.0
        return traits_to_average


class GoldPerMinute(SteamMatchDataFeature):
    def _construct(self, team_name, n_matches, conn=None):
        super(GoldPerMinute, self)._construct(team_name, n_matches, conn)
        gpms = []
        for match in self.matches:
            friendly_players, _ = self._get_friendly_and_enemy_players(team_name, match)
            friendly_average = self._get_team_wide_average(friendly_players)
            gpms.append(friendly_average["gold_per_min"])
        if len(gpms) == 0:
            return 0
        return sum(gpms)/float(len(gpms))


class CurrentTeamElo(Feature):
    def _construct(self, team_name, conn=None):
        if conn is None:
            conn = get_dbapi2_conn()
        cursor = conn.cursor()
        elo_query = "select elo from team where name = ?"
        cursor.execute(elo_query, (team_name,))
        elo = cursor.fetchall()[0][0]
        return elo


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
            elo = CurrentTeamElo(
                "team_{}_elo".format(team_name),
                team_name=team_name
            )
            self.features.append(elo)

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
