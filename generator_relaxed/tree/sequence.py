class Sequence:
    """
    None,None -> root of the game tree
    """
    def __init__(self, seq_id: int = None, action=None):
        assert (seq_id is None and action is None) or (seq_id is not None and action is not None)

        # seq_id = seq_id of infoset that generated this sequence
        self.seq_id = seq_id
        self.action = action

    def __str__(self):
        if self.seq_id is not None:
            return "[info-id: " + str(self.seq_id) + ", action: " + str(self.action) + "]"
        else:
            return "[Empty]"

    def __eq__(self, other):
        return self.seq_id == other.seq_id and self.action == other.action

    def __hash__(self):
        return hash( (self.seq_id, self.action) )
