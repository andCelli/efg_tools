from cfr.input_structures.utility_matrix import UtilMatrix


class Game:
    def __init__(self, player_id, opponent_id, player_treeplex, opponent_treeplex, util_matrix: UtilMatrix,
                 utils_type=UtilMatrix.GENERAL_SUM):
        # player vs opponent
        self.player_id = player_id
        self.opponent_id = opponent_id

        self.player_treeplex = player_treeplex
        self.opponent_treeplex = opponent_treeplex

        self.util_matrix = util_matrix

        # check that the sum of the utils is zero/const/general
        assert self.util_matrix.check_util_sum()
