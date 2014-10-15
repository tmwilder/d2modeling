import unittest

import test.utils as utils
import d2modeling.elo as elo


class TestElo(utils.DatabaseTest, unittest.TestCase):
    def test_get_new_elos(self):
        nt1, nt2 = elo._get_new_elos(1200, 1200, "DIRE")
        self.assertEqual((1184, 1216), (nt1, nt2))

        nt1, nt2 = elo._get_new_elos(1200, 1200, "RADIANT")
        self.assertEqual((1216, 1184), (nt1, nt2))

        nt1, nt2 = elo._get_new_elos(1000, 2000, "DIRE")
        self.assertEqual((1000, 2001), (nt1, nt2))

        nt1, nt2 = elo._get_new_elos(1000, 2000, "RADIANT")
        self.assertEqual((1032, 1969), (nt1, nt2))

    def test_update_all(self):
        utils.populate(session=self.session, team_names=["a", "b", "c", "d"])
        self.transaction.commit()

        elo.update_all(conn=self.db_api_2_conn)

        self.assertEqual(
            self.db_api_2_conn.execute("select * from team").fetchall(),
            [(u'a', 1206.0), (u'b', 1227.0), (u'c', 1197.0), (u'd', 1181.0)]
        )


if __name__ == "__main__":
    unittest.main(verbosity=3)
