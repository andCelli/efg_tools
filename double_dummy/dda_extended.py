import sys
from misc.game_structures import import_multiple_hands, CARDINAL_TO_PID
from double_dummy.algorithms import dda_extended


if __name__ == "__main__":
    args = sys.argv
    # 1: hands, n_players, hand_owner, iterations
    if len(sys.argv) == 5:
        hands = import_multiple_hands(args[1])
        n_players = int(args[2])
        assert args[3] in CARDINAL_TO_PID.keys(), "ERROR: invalid owner, use N, E, S or W"
        owner = CARDINAL_TO_PID[args[3]]
        iterations = int(args[4])

        result = dda_extended(hands, n_players, owner, iterations)
    # 2: hands, n_players
    elif len(sys.argv) == 3:
        hands = import_multiple_hands(args[1])
        n_players = int(args[2])

        result = dda_extended(hands, n_players)
    else:
        print("Please give the following parameters:\n"
              "hands n_players\n"
              "Hands shall be given in the format A:s,2:c/A:h,2:h/ {...}\n"
              "If hands is only made by one hand, please also input:\n"
              "hand_owner(N,E,S,W) number_of_simulations")
