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

    def test_DefaultFeatureSet(self):
        utils.populate(session=self.session, team_names=list(string.lowercase))
        self.transaction.commit()
        feature_set = features.DefaultFeatureSet(team_1="a", team_2="b", conn=self.db_api_2_conn)
        
        expected = {
            'last_15_matches_team_a': 0.26666666666666666,
            'last_15_matches_team_b': 0.8666666666666667,
            'last_5_matches_team_b': 0.8,
            'last_5_matches_team_a': 0.6,
            'last_10_matches_team_a': 0.3,
            'last_10_matches_team_b': 0.8
        }
        self.assertEqual(expected, feature_set.as_dict())


if __name__ == "__main__":
    unittest.main(verbosity=3)
