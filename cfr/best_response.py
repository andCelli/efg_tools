from cfr.strategy_structures.realization_plan import RealizationPlan
from cfr.input_structures.game import Game
from cfr.strategy_structures.behavioral import BehavioralStrategyProfile


PLAYER = 0
OPPONENT = 1


def compute_best_response(player_id, player_type, game: Game, real_plan_other: RealizationPlan) -> (RealizationPlan, float):
    other_type = 1 - player_type
    if player_type == PLAYER:
        cur_treeplex = game.player_treeplex
    else:
        cur_treeplex = game.opponent_treeplex

    n_seq = cur_treeplex.sequence_count

    # compute gradient of player
    gradient = game.util_matrix.get_loss_vector(n_seq, other_type, real_plan_other)

    infoset_values = {}
    cur_treeplex.get_ordered_information_sets()

    # compute a best response behavioral strategy profile
    br_behavioral_strat_profile = BehavioralStrategyProfile(player_id)

    # traverse the ordered infoset in reverse order -> reverse breadth-first
    for infoset in cur_treeplex.information_sets[::-1]:
        # compute the value of an infoset as the value of its best action
        best_seq, best_val = None, None

        for seq in infoset.get_children_as_list():
            # reverse breadth-first => first infosets analysed don't have children
            util_from_children = 0.0
            for child_infoset in cur_treeplex.get_child_information_sets(seq):
                util_from_children += infoset_values[child_infoset]

            cur_val_seq = util_from_children + gradient[seq]

            if best_val is None or cur_val_seq > best_val:
                best_val = cur_val_seq
                best_seq = seq

        infoset_values[infoset] = best_val

        # create the behavioral strategy
        behavioral = dict()
        behavioral[best_seq] = 1.0

        # all sub-optimal sequences must have null probability to be chosen
        for seq in infoset.get_children_as_list():
            if seq != best_seq:
                behavioral[seq] = 0.0

        # load behavior of the infoset
        br_behavioral_strat_profile[infoset] = behavioral

    # behavioral -> sequence
    br_real_plan = br_behavioral_strat_profile.realization_plan(cur_treeplex)

    # compute value associated to the best response
    br_val = 0.0
    for seq, prob in br_real_plan.items():
        br_val += gradient.get_default(seq, 0.0) * prob

    return br_real_plan, br_val
