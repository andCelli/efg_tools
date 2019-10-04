from cfr.strategy_structures.realization_plan import RealizationPlan
from cfr.input_structures.treeplex import Treeplex


def is_realization_plan_valid(realization_plan: RealizationPlan, treeplex: Treeplex):
    """
    Check if a realization plan is well structured
    """
    if realization_plan[treeplex.empty_sequence] != 1.0:
        return False

    for seq, val in realization_plan.items():
        if val < 0:
            return False

    for infoset in treeplex.information_sets:
        if infoset != treeplex.empty_info_set:
            children_prob = 0.0
            for child in infoset.get_children_as_list():
                children_prob += realization_plan[child]

            # prob of father = sum prob of children
            if abs(realization_plan[infoset.father_sequence] - children_prob) > 0.0000001:
                return False

    return True
