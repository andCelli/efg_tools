from cfr.input_parsers.leduc_2_reader import LeducReader
from cfr.regret_algorithms.cfr import CFR
from cfr.util import plotting as plt
from cfr.util.tree_print import PrettyTree
import os


dir_path = os.path.dirname(__file__)
leduc_3_ranks = os.path.join(dir_path, "input_files/output_leduc_2.txt")
leduc_6_ranks = os.path.join(dir_path, "input_files/output_leduc_2_harder.txt")

_DEBUG = True


iterations = 2000
file = leduc_6_ranks
reader = LeducReader(file)
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
print(f"Defenders' expected utility is: {game.util_matrix.get_expected_utility(1, player_plan, opponent_plan)}")
