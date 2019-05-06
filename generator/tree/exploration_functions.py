from typing import List, Dict, Tuple, Set

from game.game_structures import PlayerId

from tree.sequence import Sequence
from tree.infoset_info import InfosetInfo
from tree.infoset import Infoset
from tree.treeplex import Treeplex

TeamId = int
PayoffMatrix = Dict[Tuple[Sequence], Tuple[Dict[TeamId, int], float]]


"""
Function that builds a map from sequence to infoset
sequence = parent of infoset
The parameter is the dictionary of infosets belonging to a single player
"""
def build_parent_seq_to_infoset_map(infosets: Dict[str, InfosetInfo]) -> Dict[Sequence, List[InfosetInfo]]:
    map = {}
    for infoset in infosets.values():
        if infoset.parent_sequence not in map.keys():
            map[infoset.parent_sequence] = []
        map[infoset.parent_sequence].append(infoset)

    for infoset_list in map.values():
        infoset_list.sort()

    return map


"""
Build an InfosetInfo list ordered in a DFS manner
pti_map = parent sequence to infoset map
"""
def dfs_sort_infosets(pti_map: Dict[Sequence, List[InfosetInfo]]) -> List[InfosetInfo]:
    # auxiliary function
    def dfs_visit(sequence: Sequence, pti_map: Dict[Sequence, List[InfosetInfo]], visited_info_ids: Set[int], sorted_infosets: List[InfosetInfo]):
        infosets = pti_map[sequence]
        for info in infosets:
            info_id = info.info_id
            actions = info.actions

            # adding current infoset to list of visited infosets
            assert info_id not in visited_info_ids
            visited_info_ids.add(info_id)

            for action in actions:
                next_seq = Sequence(info_id, action)
                if next_seq in pti_map.keys():
                    dfs_visit(next_seq, pti_map, visited_info_ids, sorted_infosets)

            sorted_infosets.append(info)

    # back to the parent function...
    sorted_infosets = []
    visited_info_ids = set()
    dfs_visit(Sequence(), pti_map, visited_info_ids, sorted_infosets)

    return sorted_infosets


"""
Assign an id to each sequence, as ordered with dfs_sort_infosets
"""
def assign_sequence_numbers(sorted_infosets: List[InfosetInfo]) -> Dict[Sequence, int]:
    next_seq_number = 0
    sequence_numbering: Dict[Sequence, int] = {}

    for infoset in sorted_infosets:
        infoset_id = infoset.info_id
        actions = infoset.actions

        for action in actions:
            sequence = Sequence(infoset_id, action)
            assert sequence not in sequence_numbering.keys()

            sequence_numbering[sequence] = next_seq_number
            next_seq_number += 1

    sequence_numbering[Sequence()] = next_seq_number
    return sequence_numbering


"""
Create a treeplex
"""
def create_treeplex(player: PlayerId, sorted_infosets: List[InfosetInfo], sequence_numbering: Dict[Sequence, int]) -> Treeplex:
    infosets = []
    for infoset_info in sorted_infosets:
        infoset_id = infoset_info.info_id

        # sequence_numbering = sequence_numbering ??????

        first_sequence = Sequence(infoset_id, infoset_info.get_first_action())
        last_sequence = Sequence(infoset_id, infoset_info.get_last_action())
        first_sequence_number = sequence_numbering[first_sequence]
        last_sequence_number = sequence_numbering[last_sequence]

        assert last_sequence_number >= first_sequence_number
        assert last_sequence_number - first_sequence_number + 1 == len(infoset_info.actions)

        parent_sequence_number = sequence_numbering[infoset_info.parent_sequence]
        infosets.append(Infoset(first_sequence_number, last_sequence_number, parent_sequence_number, infoset_id))

    return Treeplex(player, infosets)
