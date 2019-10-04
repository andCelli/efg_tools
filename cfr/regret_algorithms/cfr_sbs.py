from cfr.regret_algorithms.regret_minimizer_sequence import TreeplexRegretMinimizer
from cfr.strategy_structures.realization_plan import RealizationPlan
from cfr.input_structures.treeplex import Treeplex
from cfr.input_structures.utility_matrix import UtilMatrix
from cfr.util.verify_realization_plan import is_realization_plan_valid
from cfr.util import plotting as plt
import cfr.epsilon_nash_eq as eps
from cfr.util.tree_print import PrettyTree


_DEBUG = False


class CFR:
    """
    CFR step by step
    """
    def __init__(self, game, exponential_regret_update=True):
        self._exponential_regret_update = exponential_regret_update
        self._eps_reached = False

        self.iterations = 1

        # get player ids
        self._player = game.player_id
        self._opponent = game.opponent_id

        self._treeplex_player: Treeplex = game.player_treeplex
        self._treeplex_opponent: Treeplex = game.opponent_treeplex

        self._util_matrix: UtilMatrix = game.util_matrix

        self._cumulative_pl = {}
        self._cumulative_opp = {}

        # init sequence-form regret minimizers
        self._trm_player = TreeplexRegretMinimizer(self._treeplex_player)
        self._trm_opponent = TreeplexRegretMinimizer(self._treeplex_opponent)

        self._n_seq_player = self._treeplex_player.sequence_count
        self._n_seq_opponent = self._treeplex_opponent.sequence_count

        # init strategies
        self._cur_strat_profile_player = self._trm_player.suggest_strategy()
        self._cur_strat_profile_opponent = self._trm_opponent.suggest_strategy()

        self._cur_realization_plan_player = self._cur_strat_profile_player.realization_plan(self._treeplex_player)
        self._cur_realization_plan_opponent = self._cur_strat_profile_opponent.realization_plan(self._treeplex_opponent)

        if _DEBUG:
            print("Init realization plan of player:")
            PrettyTree(self._treeplex_player, self._cur_realization_plan_player).print()
            print("Init realization plan of opponent:")
            PrettyTree(self._treeplex_opponent, self._cur_realization_plan_opponent).print()

        # init cumulative real plans
        self._cumulative_pl = self._cur_realization_plan_player
        self._cumulative_opp = self._cur_realization_plan_opponent

        self._avg_real_plan_player = RealizationPlan(self._player)
        self._avg_real_plan_opponent = RealizationPlan(self._opponent)

    def _den(self):
        if self._exponential_regret_update:
            return (self.iterations * (self.iterations + 1)) / 2
        else:
            return self.iterations

    def _regret_update_val(self, _val):
        if self._exponential_regret_update:
            return _val * self.iterations
        else:
            return _val

    def evaluate_and_update(self):
        self.iterations += 1

        # compute loss vectors by marginalizing the utility matrix
        loss_vector_player = self._util_matrix.get_loss_vector(self._n_seq_player, UtilMatrix.OPPONENT,
                                                               self._cur_realization_plan_opponent)
        # update regret minimizers
        self._trm_player.observe_loss(loss_vector_player)
        cur_strat_profile_player = self._trm_player.suggest_strategy()
        cur_realization_plan_player = cur_strat_profile_player.realization_plan(self._treeplex_player)
        assert is_realization_plan_valid(cur_realization_plan_player, self._treeplex_player)

        # repeat for opponent
        loss_vector_opp = self._util_matrix.get_loss_vector(self._n_seq_opponent, UtilMatrix.PLAYER,
                                                            cur_realization_plan_player)
        self._trm_opponent.observe_loss(loss_vector_opp)
        cur_strat_profile_opponent = self._trm_opponent.suggest_strategy()
        cur_realization_plan_opponent = cur_strat_profile_opponent.realization_plan(self._treeplex_opponent)
        assert is_realization_plan_valid(cur_realization_plan_opponent, self._treeplex_opponent)

        # update cumulative values
        for seq, val in cur_realization_plan_player.items():
            self._cumulative_pl[seq] += self._regret_update_val(val)
        for seq, val in cur_realization_plan_opponent.items():
            self._cumulative_opp[seq] += self._regret_update_val(val)

        for seq, cumulative_value in self._cumulative_pl.items():
            self._avg_real_plan_player[seq] = cumulative_value / self._den()
        for seq, cumulative_value in self._cumulative_opp.items():
            self._avg_real_plan_opponent[seq] = cumulative_value / self._den()

        if _DEBUG:
            print(f"Iteration {self.iterations} completed")

        assert is_realization_plan_valid(self._avg_real_plan_player, self._treeplex_player)
        assert is_realization_plan_valid(self._avg_real_plan_opponent, self._treeplex_opponent)

        return self._avg_real_plan_player, self._avg_real_plan_opponent, self._eps_reached
