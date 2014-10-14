from abc import ABCMeta, abstractmethod


class Feature:
    """ Base class to represent single interface for storing
        and accessing one feature in memory.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.value = self._construct(*args, **kwargs)

    @abstractmethod
    def _construct(self, *args, **kwargs):
        """ Loads data for the feature. """
        pass

    def as_tuple(self):
        assert(self.value is not None)
        return (self.name, self.value)

    def as_value(self):
        assert(self.value is not None)
        return self.value


class FeatureSet:
    """ Class used to contain a list of Features.

        Purpose is to provide single interface for getting features in
        arbitrary formats for different ML library functions.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, team_1, team_2, conn):
        # Subclasses define self.features in their constructors.
        for feature in self.features:
            assert(isinstance(feature, Feature))

    def as_dict(self):
        return dict([feature.as_tuple() for feature in self.features])

    def as_values(self):
        return [feature.value for feature in self.features]
