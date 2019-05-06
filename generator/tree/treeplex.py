from typing import List, Dict

from customtests import CustomTests

from tree.infoset import Infoset

from game.game_structures import PlayerId

"""
A treeplex is a tree of infosets
"""
class Treeplex:
    def __init__(self, player: PlayerId, infosets: List[Infoset]):
        self.num_sequences = self.validate(infosets)
        self.player = player
        self.infosets = infosets

    def num_infosets(self) -> int:
        return len(self.infosets)

    def has_sequence(self, sequence: int) -> bool:
        return sequence < self.num_sequences

    def empty_sequence_id(self) -> int:
        return self.num_sequences - 1

    def __str__(self):
        s = "Treeplex of player " + str(self.player + 1) + ", number of sequences = " + str(self.num_sequences) + "\n"
        for infoset in self.infosets:
            s += "\t" + str(infoset) + "\n"
        return s

    def short_str(self) -> str:
        s = "{} {}\n".format(self.player+1, self.num_sequences)
        for infoset in self.infosets:
            s += "{}\n".format(infoset.short_str())
        return s

    """
    1. The DFS visit of the tree induced by the infosets coincides with the list of infosets
    2. The sequence numbers are laid out in order
    """
    def validate(self, infosets: List[Infoset]) -> int:
        # maps each sequence id with the infosets generated by it -> sibilings
        adjacency_map: Dict[int, List[Infoset]] = {}
        empty_sequence_id = 0

        # Point 1
        for infoset in infosets:
            ps_id = infoset.parent_sequence_id
            if ps_id not in adjacency_map.keys():
                adjacency_map[ps_id] = []
            adjacency_map[ps_id].append(infoset)

            if ps_id > empty_sequence_id:
                empty_sequence_id = ps_id

        expected_infoset_order: List[Infoset] = []
        def visit_tree(root: int, adj_map: Dict[int, List[Infoset]], expected_infoset_order: List[Infoset]):
            if root in adj_map.keys():
                next_infosets = adj_map[root]
                for next_infoset in next_infosets:
                    for next_sequence_id in range(next_infoset.start_sequence_id, next_infoset.end_sequence_id + 1):
                        visit_tree(next_sequence_id, adj_map, expected_infoset_order)
                    expected_infoset_order.append(next_infoset)

        visit_tree(empty_sequence_id, adjacency_map, expected_infoset_order)

        # asserting that infosets and expected_infoset_order are the same list (order counts)
        assert len(infosets) == len(expected_infoset_order)
        test_instance = CustomTests()
        test_instance.assert_list_equal(infosets, expected_infoset_order)

        # Point 2
        expected_next_sequence_id = 0
        for infoset in infosets:
            test_instance.assert_equal(infoset.start_sequence_id, expected_next_sequence_id)
            assert infoset.start_sequence_id <= infoset.end_sequence_id
            assert infoset.parent_sequence_id > infoset.end_sequence_id

            expected_next_sequence_id = infoset.end_sequence_id + 1
        test_instance.assert_equal(empty_sequence_id, expected_next_sequence_id)

        return empty_sequence_id + 1