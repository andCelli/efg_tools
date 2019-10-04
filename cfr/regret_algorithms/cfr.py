from cfr.regret_algorithms.regret_minimizer_sequence import TreeplexRegretMinimizer
from cfr.strategy_structures.realization_plan import RealizationPlan
from cfr.input_structures.treeplex import Treeplex
from cfr.input_structures.utility_matrix import UtilMatrix
from cfr.util.verify_realization_plan import is_realization_plan_valid
from cfr.util import plotting as plt
import cfr.epsilon_nash_eq as eps
from cfr.util.tree_print import PrettyTree


_DEBUG = False
_EXPONENTIAL_REGRET_UPDATE = True


class CFR:
    def __init__(self, game, iterations):
        self._game = game
        self._iterations = iterations

        # get player ids
        self._player = game.player_id
        self._opponent = game.opponent_id

        self._treeplex_player: Treeplex = game.player_treeplex
        self._treeplex_opponent: Treeplex = game.opponent_treeplex

        self._util_matrix: UtilMatrix = game.util_matrix

        self.cumulative_pl = {}
        self.cumulative_opp = {}

    @staticmethod
    def _den(_iter):
        if _EXPONENTIAL_REGRET_UPDATE:
            return (_iter * (_iter + 1)) / 2
        else:
            return _iter

    @staticmethod
    def _regret_update_val(_val, _iter):
        if _EXPONENTIAL_REGRET_UPDATE:
            return _val * _iter
        else:
            return _val

    def solve(self, break_if_low_eps=True, print_eps_values=False):
        # init sequence-form regret minimizers
        trm_player = TreeplexRegretMinimizer(self._treeplex_player)
        trm_opponent = TreeplexRegretMinimizer(self._treeplex_opponent)

        n_seq_player = self._treeplex_player.sequence_count
        n_seq_opponent = self._treeplex_opponent.sequence_count

        # init strategies
        cur_strat_profile_player = trm_player.suggest_strategy()
        cur_strat_profile_opponent = trm_opponent.suggest_strategy()

        cur_realization_plan_player = cur_strat_profile_player.realization_plan(self._treeplex_player)
        cur_realization_plan_opponent = cur_strat_profile_opponent.realization_plan(self._treeplex_opponent)

        if _DEBUG:
            print("Init realization plan of player:")
            PrettyTree(self._treeplex_player, cur_realization_plan_player).print()
            print("Init realization plan of opponent:")
            PrettyTree(self._treeplex_opponent, cur_realization_plan_opponent).print()

        # init cumulative real plans
        self.cumulative_pl = cur_realization_plan_player
        self.cumulative_opp = cur_realization_plan_opponent

        avg_real_plan_player = RealizationPlan(self._player)
        avg_real_plan_opponent = RealizationPlan(self._opponent)

        for cur_iteration in range(2, self._iterations+1):

            # compute loss vectors by marginalizing the utility matrix
            loss_vector_player = self._util_matrix.get_loss_vector(n_seq_player, UtilMatrix.OPPONENT,
                                                                   cur_realization_plan_opponent)
            # update regret minimizers
            trm_player.observe_loss(loss_vector_player)
            cur_strat_profile_player = trm_player.suggest_strategy()
            cur_realization_plan_player = cur_strat_profile_player.realization_plan(self._treeplex_player)
            assert is_realization_plan_valid(cur_realization_plan_player, self._treeplex_player)

            # repeat for opponent
            loss_vector_opp = self._util_matrix.get_loss_vector(n_seq_opponent, UtilMatrix.PLAYER,
                                                                cur_realization_plan_player)
            trm_opponent.observe_loss(loss_vector_opp)
            cur_strat_profile_opponent = trm_opponent.suggest_strategy()
            cur_realization_plan_opponent = cur_strat_profile_opponent.realization_plan(self._treeplex_opponent)
            assert is_realization_plan_valid(cur_realization_plan_opponent, self._treeplex_opponent)

            # update cumulative values
            for seq, val in cur_realization_plan_player.items():
                self.cumulative_pl[seq] += self._regret_update_val(val, cur_iteration)
            for seq, val in cur_realization_plan_opponent.items():
                self.cumulative_opp[seq] += self._regret_update_val(val, cur_iteration)

            # PLOTTING EPSILON NASH
            for seq, cumulative_value in self.cumulative_pl.items():
                avg_real_plan_player[seq] = cumulative_value / self._den(cur_iteration)
            for seq, cumulative_value in self.cumulative_opp.items():
                avg_real_plan_opponent[seq] = cumulative_value / self._den(cur_iteration)
            eps_value = eps.br_values_eps(self._game, avg_real_plan_player, avg_real_plan_opponent, cur_iteration)
            eps_plotter = plt.EpsDifferencesPlotter.get_instance()
            eps_plotter.data_x.append(cur_iteration)
            eps_plotter.data_y.append(eps_value)

            if print_eps_values:
                print(eps_value)

            if _DEBUG:
                print("regrets player = " + str(trm_player.mean_regrets(cur_iteration)))
                print("regrets opponent = " + str(trm_opponent.mean_regrets(cur_iteration)))
                print(f"Iteration {cur_iteration} completed")

            if eps_value < eps.SMALL_EPS and break_if_low_eps:
                print(f"Reached eps nash after iteration {cur_iteration}, stopping process...")
                break

        assert is_realization_plan_valid(avg_real_plan_player, self._game.player_treeplex)
        assert is_realization_plan_valid(avg_real_plan_opponent, self._game.opponent_treeplex)

        return avg_real_plan_player, avg_real_plan_opponent
