from cfr.strategy_structures.realization_plan import RealizationPlan


class BehavioralStrategyProfile:
    """
    Dictionary that contains infoset:behavioral_strategy items
    Associates a behavioral strategy to each infoset of a treeplex
    """
    def __init__(self, player):
        self.player = player
        self._strategies = {}

    def __setitem__(self, key, value):
        self._strategies[key] = value

    def __getitem__(self, item):
        return self._strategies[item]

    def realization_plan(self, treeplex):
        """
        Return the realization plan corresponding to this strategy
        """
        realization_plan = RealizationPlan(self.player)

        ordered_infosets = treeplex.get_ordered_information_sets()

        for infoset in ordered_infosets:
            if infoset == treeplex.empty_info_set:
                # empty seq has 100% probability of being chosen
                realization_plan[treeplex.empty_sequence] = 1.0
            else:
                # seq prob = father's prob * behavior of the parent infoset
                father_seq = infoset.father_sequence
                for child_seq in infoset.get_children_as_list():
                    behavioral_prob = self._strategies[infoset][child_seq]
                    father_prob = realization_plan[father_seq]
                    realization_plan[child_seq] = behavioral_prob * father_prob
        return realization_plan

    def __str__(self):
        return ", ".join([f"{infoset}: {behavior}" for infoset, behavior in self._strategies])
