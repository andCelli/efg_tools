from cfr.regret_algorithms.regret_minimizer_normal import RegretMinimizer
from cfr.strategy_structures.behavioral import BehavioralStrategyProfile
from cfr.strategy_structures.loss_vector import LossVector
from cfr.input_structures.treeplex import Treeplex


class TreeplexRegretMinimizer:
    """
    Sequence-form regret minimizer
    """
    def __init__(self, treeplex: Treeplex):
        self._treeplex = treeplex

        # initialize a regret minimizer for each infoset
        # infoset:rms
        self._simplex_rms = {}
        for infoset in self._treeplex.information_sets:
            actions = infoset.get_children_as_list()
            self._simplex_rms[infoset] = RegretMinimizer(actions)

    def observe_loss(self, loss: LossVector):
        subtree_util = self._treeplex.subtree_utility(self.suggest_strategy(), loss)

        for infoset in self._treeplex.information_sets:
            infoset_loss = LossVector()
            for child_seq in infoset.get_children_as_list():
                infoset_loss[child_seq] = loss[child_seq] + subtree_util.get_default(child_seq, 0.0)

            self._simplex_rms[infoset].observe_loss(infoset_loss)

    def suggest_strategy(self):
        behavioral_profile = BehavioralStrategyProfile(self._treeplex.player)

        # call suggest_strategy for each infoset
        for infoset, rms in self._simplex_rms.items():
            behavioral_profile[infoset] = rms.suggest_strategy()

        return behavioral_profile

    def mean_regrets(self, iteration):
        return sum(rm.max_regret() for rm in self._simplex_rms.values()) / iteration