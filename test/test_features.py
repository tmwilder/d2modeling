import unittest
import string

import d2modeling.features as features
import test.utils as utils
import d2modeling.elo as elo


class TestFeatures(utils.DatabaseTest, unittest.TestCase):
    def test_MatchWinLossPercentage(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        expected = [
            ('5_matches', 0.6),
            ('10_matches', 0.3),
            ('15_matches', 0.26666666666666666),
            ('20_matches', 0.25),
            ('25_matches', 0.32),
            ('30_matches', 0.3),
        ]
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
        expected = [
            ('5_matches', 0.4794520547945205),
            ('10_matches', 0.5818181818181818),
            ('15_matches', 0.628),
            ('20_matches', 0.5340314136125655),
            ('25_matches', 0.515274949083503),
            ('30_matches', 0.49597423510466987)
        ]
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
        self.assertEqual((elo_a2.as_value(), elo_b2.as_value()), (1109.0, 1426.0))

    def test_AverageGameDuration(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        expected = [
            ('5_matches', 393.72798590178974),
            ('10_matches', 581.896094004632),
            ('15_matches', 540.990399493227),
            ('20_matches', 522.1112682721316),
            ('25_matches', 527.9481123225119),
            ('30_matches', 490.14676167079955)
        ]
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
        
        self.assertEqual(len(feature_set.as_dict().keys()), 50)
        self.assertEqual(type(feature_set.as_dict()), dict)
        self.assertEqual(type(feature_set.as_values()), list)
        self.assertEqual(len(feature_set.as_values()), 50)


if __name__ == "__main__":
    unittest.main(verbosity=3)
