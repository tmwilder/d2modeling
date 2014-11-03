from d2modeling.feature_classes import Feature, FeatureSet
from d2modeling.utils import get_match_row_dict
from d2modeling import get_dbapi2_conn


class LastNMatchesFeature(Feature):
    def _construct(self, last_date, team_name, n_matches, conn=None):
        self._load_matches(last_date, team_name, n_matches, conn)

    def _load_matches(self, last_date, team_name, n_matches, conn=None):
        if conn is None:
            conn = get_dbapi2_conn()
        cursor = conn.cursor()
        sql = (
        "SELECT "
            "* "
        "FROM "
            "match "
        "WHERE "
            "dire_name = ? or "
            "radiant_name = ? and "
            "date < ?"
        "ORDER BY "
            "date desc "
        "LIMIT "
            "? "
        )
        data = (team_name, team_name, last_date, n_matches)
        cursor.execute(sql, data)
        rows = cursor.fetchall()
        self.matches = [get_match_row_dict(row) for row in rows]


class SteamMatchDataFeature(LastNMatchesFeature):
    """ Class provides a DRY way of parsing sides on steam API match data. """
    def _construct(self, last_date, team_name, n_matches, conn=None):
        super(SteamMatchDataFeature, self)._construct(last_date, team_name, n_matches, conn=conn)
        for match in self.matches:
            friendly_players, enemy_players = self._get_friendly_and_enemy_players(team_name, match)
            match['friendly_average'] = self._get_team_wide_average(friendly_players)
            match['enemy_average'] = self._get_team_wide_average(enemy_players)

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


class PlayerAverageFeature(SteamMatchDataFeature):
    def _construct(self, laste_date, team_name, n_matches, trait, friendly_or_enemy, conn=None):
        assert(friendly_or_enemy in  ["friendly_average", "enemy_average"])
        super(PlayerAverageFeature, self)._construct(laste_date, team_name, n_matches, conn)
        data_points = []
        for match in self.matches:
            data_points.append(match[friendly_or_enemy][trait])
        if len(data_points) == 0:
            return 0
        return sum(data_points)/float(len(data_points))


def get_all_player_average_features(last_date, team_name, n_matches, conn=None):
    traits = [
        "kills",
        "deaths",
        "assists",
        "leaver_status",
        "gold",
        "last_hits",
        "denies",
        "gold_per_min",
        "xp_per_min",
        "gold_spent",
        "hero_damage",
        "tower_damage",
        "hero_healing",
        "level"
    ]
    all_features = []
    for side in ["friendly_average", "enemy_average"]:
        for trait in traits:
            feature_name = "{}_player_{}_last_{}_team_{}".format(
                side,
                trait,
                n_matches,
                team_name
            )
            feature = PlayerAverageFeature(
                name=feature_name,
                last_date=last_date,
                team_name=team_name,
                n_matches=n_matches,
                trait=trait,
                friendly_or_enemy=side,
                conn=conn
            )
            all_features.append(feature)
    return all_features


class CurrentTeamElo(Feature):
    def _construct(self, last_date, team_name, conn=None):
        if conn is None:
            conn = get_dbapi2_conn()
        cursor = conn.cursor()
        elo_query = (
            "SELECT "
                "CASE WHEN radiant_name = ? THEN radiant_elo ELSE dire_elo END "
            "FROM match "
            "WHERE "
                "date <= ?"
            "ORDER BY "
                "date, time "
            "LIMIT 1"
        )
        cursor.execute(elo_query, (team_name, last_date))
        elo = cursor.fetchall()[0][0]
        return elo


class MatchWinLossPercentage(LastNMatchesFeature):
    def _construct(self, last_date, team_name, n_matches, conn=None):
        super(MatchWinLossPercentage, self)._construct(last_date, team_name, n_matches, conn)

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

        if not (wins or losses):
            # Assign a bad winrate if they have no matches.
            return 0.2

        percentage = float(wins)/(wins + losses)
        # If we run into memory problems, we can call del self.matches here. Not doing now for debug reasons.
        return percentage


class KillPercentage(LastNMatchesFeature):
    def _construct(self, last_date, team_name, n_matches, conn=None):
        super(KillPercentage, self)._construct(last_date, team_name, n_matches, conn)

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
            kills_over_kill_deaths = .5
        else:
            kills_over_kill_deaths = float(kills)/(kills + deaths)

        return kills_over_kill_deaths


class AverageGameDuration(LastNMatchesFeature):
    def _construct(self, last_date, team_name, n_matches, conn=None):
        super(AverageGameDuration, self)._construct(last_date, team_name, n_matches, conn)

        matches = len(self.matches)
        time = 0.0

        for match in self.matches:
            time += match["time"]

        if matches == 0:
            return 2000

        return  time/matches


class DefaultFeatureSet(FeatureSet):
    def __init__(self, last_date, team_1, team_2, conn, matches_back=10, increment=5):
        self.features = []

        for team_name in (team_1, team_2):
            elo = CurrentTeamElo("team_{}_elo".format(team_name), last_date=last_date, team_name=team_name, conn=conn)
            self.features.append(elo)

            last_n_features = {
                'win_percentage_last_{}_team_{}': MatchWinLossPercentage,
                'kill_percentage_last_{}_team_{}': KillPercentage,
                'average_game_duration_last_{}_team_{}': AverageGameDuration,
            }

            for x in range(increment, matches_back+1, increment):
                for name, feature_class in last_n_features.items():
                    feature = feature_class(
                        name=name.format(x, team_name),
                        last_date=last_date,
                        team_name=team_name,
                        n_matches=x,
                        conn=conn
                    )
                    self.features.append(feature)

                player_averages = get_all_player_average_features(
                    last_date=last_date,
                    team_name=team_name,
                    n_matches=x,
                    conn=conn
                )
                self.features.extend(player_averages)

        super(DefaultFeatureSet, self).__init__(last_date, team_1, team_2, conn)
