import unittest
import string

import d2modeling.features as features
import test.utils as utils
import d2modeling.elo as elo


class TestFeatures(utils.DatabaseTest, unittest.TestCase):
    def test_MatchWinLossPercentage(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        expected = [('5_matches', 0.8), ('10_matches', 0.5), ('15_matches', 0.4), ('20_matches', 0.3), ('25_matches', 0.32), ('30_matches', 0.36666666666666664)]
        actual = []
        for x in range(5, 31, 5):
            n_matches = features.MatchWinLossPercentage(
                name="{}_matches".format(x),
                team_name="a",
                n_matches=x,
                conn=self.db_api_2_conn
            )
            actual.append(n_matches.as_tuple())
        self.assertEqual(expected, actual)

    def test_KillPercentage(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        expected = [('5_matches', 0.5064935064935064), ('10_matches', 0.4845360824742268), ('15_matches', 0.45255474452554745), ('20_matches', 0.45058139534883723), ('25_matches', 0.46444444444444444), ('30_matches', 0.49401709401709404)]
        actual = []
        for x in range(5, 31, 5):
            n_matches = features.KillPercentage(
                name="{}_matches".format(x),
                team_name="a",
                n_matches=x,
                conn=self.db_api_2_conn
            )
            actual.append(n_matches.as_tuple())
        self.assertEqual(expected, actual)

    def test_CurrentTeamElo(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        elo_a = features.CurrentTeamElo(
            name="team_{}_elo".format("a"),
            team_name="a",
            conn=self.db_api_2_conn
        )
        elo_b = features.CurrentTeamElo(
            name="team_{}_elo".format("b"),
            team_name="b",
            conn=self.db_api_2_conn
        )
        self.assertEqual((elo_a.as_value(), elo_b.as_value()), (1200, 1200))
        elo.update_all(conn=self.db_api_2_conn)
        
        elo_a2 = features.CurrentTeamElo(
            name="team_{}_elo".format("a"),
            team_name="a",
            conn=self.db_api_2_conn
        )
        elo_b2 = features.CurrentTeamElo(
            name="team_{}_elo".format("b"),
            team_name="b",
            conn=self.db_api_2_conn
        )
        self.assertEqual((elo_a2.as_value(), elo_b2.as_value()), (1171.0, 1179.0))

    def test_AverageGameDuration(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        expected = [('5_matches', 521.2403339845883), ('10_matches', 624.8510651101103), ('15_matches', 594.9876973158823), ('20_matches', 632.1082840756069), ('25_matches', 587.3676210345193), ('30_matches', 561.7558011401103)]
        actual = []
        for x in range(5, 31, 5):
            n_matches = features.AverageGameDuration(
                name="{}_matches".format(x),
                team_name="a",
                n_matches=x,
                conn=self.db_api_2_conn
            )
            actual.append(n_matches.as_tuple())
        self.assertEqual(expected, actual)

    def test_DefaultFeatureSet(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()

        feature_set = features.DefaultFeatureSet(team_1="a", team_2="b", conn=self.db_api_2_conn)

        self.assertEqual(len(feature_set.as_dict().keys()), 498)
        self.assertEqual(type(feature_set.as_dict()), dict)
        self.assertEqual(type(feature_set.as_values()), list)
        self.assertEqual(len(feature_set.as_values()), 498)


if __name__ == "__main__":
    unittest.main(verbosity=3)
