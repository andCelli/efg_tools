from cfr.strategy_structures.loss_vector import LossVector
from cfr.strategy_structures.realization_plan import RealizationPlan


class UtilMatrix:
    """
    Container class to formalize utility matrix structure
    """
    PLAYER = 0
    OPPONENT = 1

    ZERO_SUM = 0
    CONST_SUM = 1
    GENERAL_SUM = 2

    def __init__(self, utils_type=GENERAL_SUM):
        # (seq_player,seq_opponent) : (util_player,util_opponent,chance)
        self._outcomes = {}
        self.utils_type = utils_type

    def _get(self, seq_pl, seq_opp):
        return self._outcomes[seq_pl, seq_opp]

    def _set(self, seq_pl, seq_opp, util_pl, util_opp, chance):
        self._outcomes[seq_pl, seq_opp] = util_pl, util_opp, chance

    def __getitem__(self, item):
        self._get(item[0], item[1])

    def __setitem__(self, key, value):
        self._set(key[0], key[1], value[0], value[1], value[2])

    def _marginalize(self, player_to_marginalize, marg_realization_plan: RealizationPlan):
        """
        Given a player and his realization plan, return a loss vector with the other player's TERMINAL sequences as keys
        and the weighted utilities as values -> fix player

        :param player_to_marginalize: the player to marginalize on. IE: if player is declarer, the resulting loss vector has
        defender's sequences as indices. USE PLAYER AND OPPONENT VARIABLES OF UTILMATRIX
        :param marg_realization_plan: realization plan to evaluate
        """
        assert player_to_marginalize == UtilMatrix.OPPONENT or player_to_marginalize == UtilMatrix.PLAYER, \
            "player entry not valid, please use PLAYER or OPPONENT static variables"

        loss = LossVector()
        # 1-player will return opponent if player = player and player otherwise
        other = 1 - player_to_marginalize

        for seq, util_tuple in self._outcomes.items():
            other_seq = seq[other]
            chance = util_tuple[2]
            utility = util_tuple[other]

            # check if the sequence has already been found
            if loss.contains_key(other_seq):
                # sequence found
                loss[other_seq] += marg_realization_plan.get_default(seq[player_to_marginalize], 0.0) * utility * chance
            else:
                # sequence not found
                loss[other_seq] = marg_realization_plan.get_default(seq[player_to_marginalize], 0.0) * utility * chance

        return loss

    def get_loss_vector(self, n_seq_remaining_player, other_player, other_realization_plan: RealizationPlan):
        """
        Compute the loss vector for a given player
        player != other
        """
        assert other_player == UtilMatrix.OPPONENT or other_player == UtilMatrix.PLAYER, \
            "player entry not valid, please use PLAYER or OPPONENT static variables"
        marginalized_loss = self._marginalize(other_player, other_realization_plan)
        loss = LossVector()

        # cycle over all the sequences of the player
        for seq in range(0, n_seq_remaining_player):
            loss[seq] = marginalized_loss.get_default(seq, 0.0)

        return loss

    def get_expected_utility(self, player, real_player: RealizationPlan, real_other: RealizationPlan):
        assert player == UtilMatrix.OPPONENT or player == UtilMatrix.PLAYER, \
            "player entry not valid, please use PLAYER or OPPONENT static variables"

        other = 1 - player

        expected_value = 0.0
        for seq_tuple, util_tuple in self._outcomes.items():
            terminal_seq_player = seq_tuple[player]
            terminal_seq_other = seq_tuple[other]
            util_player = util_tuple[player]
            chance = util_tuple[2]
            expected_value += real_player[terminal_seq_player] * real_other[terminal_seq_other] * util_player * chance

        return expected_value

    def check_util_sum(self):
        _sum = None
        for seqs, utils in self._outcomes.items():
            if self.utils_type == self.ZERO_SUM:
                if utils[self.PLAYER] + utils[self.OPPONENT] != 0:
                    return False
            elif self.utils_type == self.CONST_SUM:
                if _sum is None:
                    _sum = utils[self.PLAYER] + utils[self.OPPONENT]
                else:
                    if utils[self.PLAYER] + utils[self.OPPONENT] != _sum:
                        return False
        return True
