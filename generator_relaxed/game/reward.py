from abc import ABC, abstractmethod


_ZERO_SUM = "zero_sum"
_CONSTANT_SUM = "constant_sum"


class RewardCalculator(ABC):
    @abstractmethod
    def compute(self, game_state):
        pass


class RewardNumberOfTricks(RewardCalculator):
    def __init__(self):
        self.type = _CONSTANT_SUM

    def compute(self, game_state):
        tricks_won = game_state.get_curr_turn_info().tricks_won

        team1_tricks = team2_tricks = 0
        for (tid, team) in game_state.teams.items():
            for pid in team.members:
                tricks = tricks_won[pid]
                if tid == 0:
                    team1_tricks += tricks
                else:
                    team2_tricks += tricks

        return {0: team1_tricks, 1: team2_tricks}


class RewardZeroSumWinnerTricks(RewardCalculator):
    def __init__(self):
        self.type = _ZERO_SUM

    def compute(self, game_state):
        tricks_won = game_state.get_curr_turn_info().tricks_won

        team1_tricks = team2_tricks = 0
        for (tid, team) in game_state.teams.items():
            for pid in team.members:
                tricks = tricks_won[pid]
                if tid == 0:
                    team1_tricks += tricks
                else:
                    team2_tricks += tricks

        if team1_tricks > team2_tricks:
            # team 1 wins
            return {0: team1_tricks, 1: -team1_tricks}
        elif team2_tricks > team1_tricks:
            # team 2 wins
            return {0: -team2_tricks, 1: team2_tricks}
        else:
            # draw
            return {0: 0, 1: 0}


class RewardWinLoss(RewardCalculator):
    def __init__(self):
        self.type = _ZERO_SUM

    def compute(self, game_state):
        tricks_won = game_state.get_curr_turn_info().tricks_won

        team1_tricks = team2_tricks = 0
        for (tid, team) in game_state.teams.items():
            for pid in team.members:
                tricks = tricks_won[pid]
                if tid == 0:
                    team1_tricks += tricks
                else:
                    team2_tricks += tricks

        if team1_tricks > team2_tricks:
            # team 1 wins
            return {0: 1, 1: -1}
        elif team2_tricks > team1_tricks:
            # team 2 wins
            return {0: -1, 1: 1}
        else:
            # draw
            return {0: 0, 1: 0}
