from cfr.input_parsers.bridge_reader import BridgeReader
from cfr.regret_algorithms.cfr import CFR
from cfr.util import plotting as plt
from cfr.util.tree_print import PrettyTree
import os


dir_path = os.path.dirname(__file__)
first_bridge_cs = os.path.join(dir_path, "input_files/PlayingGenOut_2019-09-04_19-22-44.txt")
complex_bridge = os.path.join(dir_path, "input_files/PlayingGenOut_2019-09-16_11-49-25.txt")
four_ranks_bridge = os.path.join(dir_path, "input_files/PlayingGenOut_2019-09-16_15-54-10.txt")
stupid_bridge = os.path.join(dir_path, "input_files/PlayingGenOut_2019-09-18_10-24-26.txt")

_DEBUG = True


iterations = 1000
file = four_ranks_bridge
reader = BridgeReader(file)
game = reader.process_data()

cfr_test = CFR(game, iterations)
player_plan, opponent_plan = cfr_test.solve()

if _DEBUG:
    player_tree = PrettyTree(game.player_treeplex, player_plan)
    opponent_tree = PrettyTree(game.opponent_treeplex, opponent_plan)

    print("Player final tree")
    player_tree.print()
    print("Opponent final tree")
    opponent_tree.print()

plt.EpsDifferencesPlotter.get_instance().plot()

print(f"Declarer's expected utility is: {game.util_matrix.get_expected_utility(0, player_plan, opponent_plan)}")
print(f"Defenders' expected utility is: {game.util_matrix.get_expected_utility(1, opponent_plan, player_plan)}")
