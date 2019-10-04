from cfr.input_structures.information_set import InfoSet
from cfr.strategy_structures.loss_vector import LossVector
from cfr.strategy_structures.behavioral import BehavioralStrategyProfile


PID_TO_CARDINAL = {
    0: 'N',
    1: 'E',
    2: 'S',
    3: 'W'
}


class Treeplex:
    """
    A treeplex is a tree of infosets
    """
    def __init__(self, player: int):
        self.player = player
        self.information_sets = []

        self.empty_sequence = None
        self.empty_info_set: InfoSet = None

        self.sequence_count = 0
        self.info_set_count = 0

        self.is_ordered = False

    def set_empty_sequence(self, empty_seq: int):
        """
        Set the empty sequence id
        """
        self.empty_sequence = empty_seq
        if empty_seq + 1 > self.sequence_count:
            self.sequence_count += 1

    def set_empty_information_set(self, empty_info_set: InfoSet):
        """
        Set the empty information set
        """
        self.empty_info_set = empty_info_set
        self.information_sets.append(empty_info_set)
        self.info_set_count += 1

    def add_information_set(self, new_info_set: InfoSet):
        self.information_sets.append(new_info_set)
        self.info_set_count += 1
        last_seq_id = new_info_set.last_child_sequence
        if last_seq_id + 1 > self.sequence_count:
            self.sequence_count = last_seq_id + 1

    def get_child_information_sets(self, sequence):
        """
        Return the information sets that follow the input sequence
        """
        result = []
        for infoset in self.information_sets:
            if infoset.father_sequence is not None and infoset.father_sequence == sequence:
                result.append(infoset)
        return result

    def has_sequence(self, seq_id):
        return seq_id < self.sequence_count

    def has_information_set(self, infoset_id: int):
        for infoset in self.information_sets:
            if infoset.id == infoset_id:
                return True
        return False

    def get_information_set_by_id(self, infoset_id: int):
        for infoset in self.information_sets:
            if infoset.id == infoset_id:
                return infoset
        raise LookupError

    def get_ordered_information_sets(self):
        """
        Orders infosets in breadth-first fashion and returns the infoset list
        """
        if not self.is_ordered:
            # order the information sets

            # infosets to explore
            to_explore = [self.empty_info_set]

            # output list
            ordered_infosets = [self.empty_info_set]

            while to_explore:
                father_infoset = to_explore.pop()
                for seq in father_infoset.get_children_as_list():
                    for child_infoset in self.get_child_information_sets(seq):
                        # for each child sequence of father_infoset
                        to_explore.append(child_infoset)
                        self.information_sets.remove(child_infoset)
                        ordered_infosets.append(child_infoset)
            self.information_sets = ordered_infosets
            self.is_ordered = True
        return self.information_sets

    def subtree_utility(self, behavioral_plan: BehavioralStrategyProfile, gradient: LossVector):
        """
        Given a loss vector (utilities), compute a new gradient such that (seq, value) represents the value obtained in
        the subtree corresponding to the choice of seq
        No value is returned for terminal sequences
        """
        assert self.player == behavioral_plan.player

        utility = LossVector()

        # visit ordered infosets in reversed breadth-first order
        if not self.is_ordered:
            self.get_ordered_information_sets()

        for infoset in self.information_sets[::-1]:
            for child_seq in infoset.get_children_as_list():
                if infoset != self.empty_info_set:
                    father_seq = infoset.father_sequence

                    # get probability of choosing action child_seq from infoset
                    prob_child = behavioral_plan[infoset][child_seq]

                    # get utility of child_seq; returns 0 if not present
                    util_child = utility.get_default(child_seq, 0.0)

                    # get util of child_seq
                    gradient_entry = gradient[child_seq]

                    val = prob_child * (util_child + gradient_entry)

                    if utility.contains_key(father_seq):
                        utility[father_seq] += val
                    else:
                        utility[father_seq] = val
        return utility

    def __str__(self):
        return ', '.join([str(info) for info in self.information_sets])
