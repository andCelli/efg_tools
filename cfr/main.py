from cfr.input_parsers.bridge_reader import BridgeReader
from cfr.regret_algorithms.cfr import CFR
from cfr.util import plotting as plt
from cfr.util.tree_print import PrettyTree
import os
import sys


dir_path = os.path.dirname(__file__)

_DEBUG = False


def run_bridge(file_path, iterations=500, add_prev_dir=True):
    """

    :param file_path: path starting from bridge-endgames folder, e.g. 'test_files/2_ranks/test0.txt'
    :param iterations: number of iterations if eps nash isn't met
    """
    reader = BridgeReader(os.path.join(dir_path, ("../" if add_prev_dir else "")+file_path))
    game = reader.process_data()

    cfr = CFR(game, iterations)
    player_plan, opponent_plan = cfr.solve()

    if _DEBUG:
        player_tree = PrettyTree(game.player_treeplex, player_plan)
        opponent_tree = PrettyTree(game.opponent_treeplex, opponent_plan)

        print("Player final tree")
        player_tree.print()
        print("Opponent final tree")
        opponent_tree.print()

        plt.EpsDifferencesPlotter.get_instance().plot()

    player_util = game.util_matrix.get_expected_utility(0, player_plan, opponent_plan)
    opponent_util = game.util_matrix.get_expected_utility(1, opponent_plan, player_plan)

    return player_plan, opponent_plan, player_util, opponent_util


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        file_path = args[1]
        pp, op, pu, ou = run_bridge(file_path)
        print(f"Declarer's expected utility is: {pu}")
        print(f"Defenders' expected utility is: {ou}")
    elif len(args) == 3:
        file_path = args[1]
        iterations = int(args[2])
        pp, op, pu, ou = run_bridge(file_path, iterations)
        print(f"Declarer's expected utility is: {pu}")
        print(f"Defenders' expected utility is: {ou}")
    else:
        print("Please give the path to the file (as if you were in bridge_endgames folder) and, optionally, "
              "the maximum number of iterations")
