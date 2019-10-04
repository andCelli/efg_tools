"""
Loss = Utility after fixing the strategy of the other player
"""


class LossVector:
    """
    Dictionary of sequence:value
    """
    def __init__(self, entries=None):
        if entries:
            self._entries = entries
        else:
            self._entries = {}

    def contains_key(self, key):
        return key in self._entries.keys()

    def get_default(self, key, default):
        """
        Returns _entries[key] if key exists, default otherwise
        """
        return self._entries.get(key, default)

    def items(self):
        return self._entries.items()

    def __getitem__(self, item):
        return self._entries[item]

    def __setitem__(self, key, value):
        self._entries[key] = value

    def __str__(self):
        return str(self._entries)
