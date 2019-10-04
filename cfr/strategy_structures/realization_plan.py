class RealizationPlan:
    """
    Dictionary that contains sequence:probability items
    Represents the probability of reaching a sequence given a treeplex and a strategy profile
    """
    def __init__(self, player, distribution=None):
        self.player = player
        if distribution:
            self._distribution = distribution
        else:
            self._distribution = {}

    def get_default(self, key, default):
        return self._distribution.get(key, default)

    def items(self):
        return self._distribution.items()

    def values(self):
        return self._distribution.values()

    def __getitem__(self, item):
        return self._distribution[item]

    def __setitem__(self, key, value):
        self._distribution[key] = value

    def __str__(self):
        return str(self._distribution)

    def __eq__(self, other):
        for seq, value in other.items():
            if seq in self._distribution.keys():
                if value != self._distribution[seq]:
                    return False
            else:
                return False

    def __ne__(self, other):
        return not self == other
