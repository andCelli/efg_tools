from cfr.strategy_structures.loss_vector import LossVector


class RegretMinimizer:
    """
    Normal-form regret minimizer
    Regret minimizer for a single infoset
    """
    def __init__(self, actions):

        # dict of sequence:regret
        self._regrets = {}

        # init regrets to 0
        for action in actions:
            self._regrets[action] = 0

    def observe_loss(self, loss: LossVector):
        # compute and get the current strategy
        last_strategy = self.suggest_strategy()

        expected_value = 0.0
        for action, prob in last_strategy.items():
            expected_value += loss[action] * prob

        # regret update
        # for each action add the regret: util of that action in pure strategy minus expected value
        for action, regret in self._regrets.items():
            val = regret + loss[action] - expected_value
            # if negative, store 0
            self._regrets[action] = max(val, 0.0)

    def suggest_strategy(self):
        """
        Compute the strategy given by regrets
        """
        strategy = dict()

        if self.is_zero():
            # first iteration; init all probabilities to a uniform distribution
            uniform_prob = 1 / len(self._regrets)
            for action in self._regrets.keys():
                strategy[action] = uniform_prob
        else:
            regret_sum = sum([regret for regret in self._regrets.values()])

            assert regret_sum > 0, "Regret sum is negative!!!"

            # update the strategy with normalized regrets
            for action, regret in self._regrets.items():
                prob = regret / regret_sum
                strategy[action] = prob

        return strategy

    def is_zero(self):
        """
        Return True if all regrets are 0
        """
        for action, prob in self._regrets.items():
            if prob != 0.0:
                return False
        return True

    def max_regret(self):
        return max(self._regrets.values())


# TEST
if __name__ == "__main__":
    rm = RegretMinimizer([0, 1, 2])
    # rm must be init as 0
    assert rm.is_zero()
    # tm must suggest uniform strategy
    print(rm.suggest_strategy())
    l = LossVector()
    l[0] = 0.3
    l[1] = 0.5
    l[2] = 1.0
    rm.observe_loss(l)
    print(rm.suggest_strategy())
