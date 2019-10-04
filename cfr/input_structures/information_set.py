class InfoSet:
    """
    Information set, uniquely identified with an id.
    Stores the parent sequence, first child sequence and last child sequence. Sequences are in increasing order.
    """
    def __init__(self, i_id, first_child_seq, last_child_seq, father_seq):
        self.i_id = i_id
        self.father_sequence = father_seq
        self.first_child_sequence = first_child_seq
        self.last_child_sequence = last_child_seq

    def __eq__(self, other):
        return self.i_id == other.i_id

    def __ne__(self, other):
        return self.i_id != other.i_id

    def __str__(self):
        return f"<Infoset {self.i_id}: fa={self.father_sequence}, ch={self.first_child_sequence}-{self.last_child_sequence}>"

    def __hash__(self):
        return hash((self.i_id, self.father_sequence, self.first_child_sequence, self.last_child_sequence))

    def get_sequences_triple(self):
        """
        Returns a tuple with father, first child anc last child sequences
        """
        return self.father_sequence, self.first_child_sequence, self.last_child_sequence

    def get_children_as_list(self):
        """
        Returns a list with all children ids.
        Example: first = 1, last = 3 -> [1,2,3]
        """
        return [_id for _id in range(self.first_child_sequence, self.last_child_sequence + 1)]
