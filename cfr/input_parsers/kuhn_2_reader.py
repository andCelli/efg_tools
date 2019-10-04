from cfr.input_parsers.abs_reader import AbstractReader
from cfr.input_structures.game import Game
from cfr.input_structures.information_set import InfoSet
from cfr.input_structures.treeplex import Treeplex
from cfr.input_structures.utility_matrix import UtilMatrix


class KuhnReader(AbstractReader):
    def process_data(self):
        # TREEPLEX SECTION
        treeplexes = {}
        current_treeplex = None
        infoset_count = None
        for l in self._tree_section:
            if l.find("=== ") != -1:
                if current_treeplex is not None:
                    current_treeplex.set_empty_information_set(InfoSet(infoset_count,
                                                               current_treeplex.empty_sequence,
                                                               current_treeplex.empty_sequence, None))
                x = l.split(' ')
                pid = int(x[1])-1
                # 2 player game
                treeplexes[pid] = Treeplex(pid)
                current_treeplex = treeplexes[pid]
                infoset_count = 0
                print(f"Found player {pid}")
            else:
                x = l.split(' ')
                current_treeplex.add_information_set(InfoSet(infoset_count, int(x[0]), int(x[1]), int(x[2])))
                current_treeplex.set_empty_sequence(int(x[2]))
                infoset_count += 1
        current_treeplex.set_empty_information_set(InfoSet(infoset_count,
                                                   current_treeplex.empty_sequence,
                                                   current_treeplex.empty_sequence, None))

        # UTILITY MATRIX SECTION
        util_matrix = UtilMatrix(utils_type=UtilMatrix.ZERO_SUM)
        for l in self._util_section:
            val = l.split(' ')
            # format: seq_pl_N seq_pl_E seq_pl_S seq_pl_W team_NS_util team_EW_util chance
            seq_0 = int(val[0])
            seq_1 = int(val[1])
            util_0 = int(val[2])
            util_1 = int(val[3])
            chance = float(val[4])
            util_matrix[seq_0, seq_1] = util_0, util_1, chance

        # creating game structure
        game = Game(0, 1, treeplexes[0], treeplexes[1], util_matrix)

        return game
