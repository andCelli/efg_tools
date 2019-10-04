import cfr.best_response as br
from cfr.strategy_structures.realization_plan import RealizationPlan
from cfr.input_structures.game import Game
from cfr.input_structures.utility_matrix import UtilMatrix


SMALL_EPS = 0.01


def is_epsilon_nash(game: Game, real_plan_player: RealizationPlan, real_plan_opponent: RealizationPlan, cur_iter):
    diff = br_values_eps(game, real_plan_player, real_plan_opponent, cur_iter)
    return abs(diff) < SMALL_EPS


def br_values_eps(game: Game, real_plan_player: RealizationPlan, real_plan_opponent: RealizationPlan, cur_iter):
    player = game.player_id
    opponent = game.opponent_id

    br_player, _ = br.compute_best_response(player, br.PLAYER, game, real_plan_opponent)
    br_opponent, _ = br.compute_best_response(opponent, br.OPPONENT, game, real_plan_player)

    val_br_player = game.util_matrix.get_expected_utility(UtilMatrix.PLAYER, br_player, real_plan_opponent)
    val_br_opponent = game.util_matrix.get_expected_utility(UtilMatrix.OPPONENT, br_opponent, real_plan_player)

    den = cur_iter*(cur_iter+1)/2
    diff = val_br_player/den + val_br_opponent/den

    assert diff > 0

    return diff
