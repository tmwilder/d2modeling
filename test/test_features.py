import unittest
import os.path as op
import os
import string

import d2modeling.features as features
import test.utils as utils


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

    def test_ScoreDifferential(self):
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

    def test_DefaultFeatureSet(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        feature_set = features.DefaultFeatureSet(team_1="a", team_2="b", conn=self.db_api_2_conn)
        
        result = feature_set.as_dict()
        self.assertEqual(len(result.keys()), 32)


if __name__ == "__main__":
    unittest.main(verbosity=3)
