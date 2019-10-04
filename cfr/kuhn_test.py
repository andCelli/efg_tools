from cfr.input_parsers.kuhn_2_reader import KuhnReader
from cfr.regret_algorithms.cfr_sbs import CFR
from cfr.util import plotting as plt
from cfr.util.tree_print import PrettyTree
import cfr.epsilon_nash_eq as eps
import os


dir_path = os.path.dirname(__file__)
kuhn = os.path.join(dir_path, "input_files/output_kuhn_2.txt")

_DEBUG = True


iterations = 200
file = kuhn
reader = KuhnReader(file)
game = reader.process_data()
cfr_test = CFR(game, iterations)

player_plan = opponent_plan = None

for iteration in range(iterations):
    player_plan, opponent_plan, _ = cfr_test.evaluate_and_update()
    eps_value = eps.br_values_eps(game, player_plan, opponent_plan, cfr_test.iterations)
    eps_plotter = plt.EpsDifferencesPlotter.get_instance()
    eps_plotter.data_x.append(cfr_test.iterations)
    eps_plotter.data_y.append(eps_value)

    if _DEBUG:
        print(eps_value)

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
