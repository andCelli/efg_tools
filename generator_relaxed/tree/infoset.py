class Infoset:
    def __init__(self, start: int, end: int, parent: int, infoset_id):
        assert start <= end, "invalid sequence interval"
        # note: sequences are ordered in DFS manner, so the parent has a higher id than the children
        assert parent > end, "invalid parent"

        self.start_sequence_id = start
        self.end_sequence_id = end
        self.parent_sequence_id = parent

        self.infoset_id = infoset_id

    def size(self) -> int:
        return self.end_sequence_id - self.start_sequence_id + 1

    # TODO? -> return iterator for start-end

    def __eq__(self, other):
        return self.start_sequence_id == other.start_sequence_id and \
            self.end_sequence_id == other.end_sequence_id and \
            self.parent_sequence_id == other.parent_sequence_id

    def __str__(self):
        return "Infoset " + str(self.infoset_id) + " - start: " + str(self.start_sequence_id) + ", end: " + str(self.end_sequence_id) + ", parent: " + str(self.parent_sequence_id)

    def short_str(self):
        return "{} {} {}".format(self.start_sequence_id, self.end_sequence_id, self.parent_sequence_id)
