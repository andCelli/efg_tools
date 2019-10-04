from cfr.input_parsers.abs_reader import AbstractReader
from cfr.input_structures.game import Game
from cfr.input_structures.information_set import InfoSet
from cfr.input_structures.treeplex import Treeplex
from cfr.input_structures.utility_matrix import UtilMatrix


class BridgeReader(AbstractReader):
    def process_data(self):
        # INFO SECTION
        n_players = int(self._info_section[1])

        # GAME SPECIFIC SECTION
        game_info_list = self._game_section[1].split(", ")
        declarer = self.CARDINAL_TO_PID[game_info_list[1]]
        defender = -1

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
                pid = self.CARDINAL_TO_PID[x[1]]
                # 2 player game
                if pid != declarer:
                    defender = pid
                treeplexes[pid] = Treeplex(pid)
                current_treeplex = treeplexes[pid]
                infoset_count = 0
                # print(f"Found player {pid}")
            else:
                x = l.split(' ')
                current_treeplex.add_information_set(InfoSet(infoset_count, int(x[0]), int(x[1]), int(x[2])))
                current_treeplex.set_empty_sequence(int(x[2]))
                infoset_count += 1
        current_treeplex.set_empty_information_set(InfoSet(infoset_count,
                                                   current_treeplex.empty_sequence,
                                                   current_treeplex.empty_sequence, None))

        # UTILITY MATRIX SECTION
        def team_of(player):
            return player % 2

        util_matrix = UtilMatrix()
        for l in self._util_section:
            val = l.split(' ')
            # format: seq_pl_N seq_pl_E seq_pl_S seq_pl_W team_NS_util team_EW_util chance
            seq_decl = int(val[declarer])
            seq_def = int(val[defender])
            decl_util = int(val[team_of(declarer) + n_players])
            def_util = int(val[team_of(defender) + n_players])
            chance = float(val[len(val) - 1])
            util_matrix[seq_decl, seq_def] = decl_util, def_util, chance

        # creating game structure
        assert defender != -1
        game = Game(declarer, defender, treeplexes[declarer], treeplexes[defender], util_matrix)

        return game
