import d2modeling.features as features
from d2modeling.feature_classes import FeatureSet
from d2modeling.schema import get_dbapi2_conn


class PercentageFeatureSet(FeatureSet):
    """ Tiny feature set to show class relations. """
    def __init__(self, team_1, team_2):
        self.features = []
        for team_name in (team_1, team_2):
            for n_matches in range(5, 41, 5):
                feature = features.MatchWinLossPercentage(
                    name="last_{0}_matches_for_{1}".format(n_matches, team_name),
                    team_name=team_name,
                    n_matches=n_matches
                )
                self.features.append(feature)
        # Called just to run checks.
        super(PercentageFeatureSet, self).__init__(team_1, team_2)



if __name__ == "__main__":
    # Example use. 
    feature_set = PercentageFeatureSet(team_1="NaVi", team_2="EG")
    import pprint
    pprint.pprint(feature_set.as_dict())
