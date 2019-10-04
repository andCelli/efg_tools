import sys
from misc.game_structures import import_multiple_hands, CARDINAL_TO_PID
from double_dummy.algorithms import dda_simple


if __name__ == "__main__":
    args = sys.argv
    # 1: hands, n_players, trump, declarer, hand_owner, iterations
    if len(sys.argv) == 7:
        hands = import_multiple_hands(args[1])
        n_players = int(args[2])
        trump = args[3]
        assert args[4] in CARDINAL_TO_PID.keys(), "ERROR: invalid declarer, use N, E, S or W"
        declarer = CARDINAL_TO_PID[args[4]]
        assert args[5] in CARDINAL_TO_PID.keys(), "ERROR: invalid owner, use N, E, S or W"
        owner = CARDINAL_TO_PID[args[5]]
        iterations = int(args[6])

        result = dda_simple(hands, n_players, trump, declarer, owner, iterations)
    # 2: hands, n_players, trump, declarer
    elif len(sys.argv) == 5:
        hands = import_multiple_hands(args[1])
        n_players = int(args[2])
        trump = args[3]
        assert args[4] in CARDINAL_TO_PID.keys(), "ERROR: invalid declarer, use N, E, S or W"
        declarer = CARDINAL_TO_PID[args[4]]

        result = dda_simple(hands, n_players, trump, declarer)
    else:
        print("Please give the following parameters:\n"
              "hands n_players trump(c,d,h,s,n) declarer(N,E,S,W)\n"
              "Hands shall be given in the format A:s,2:c/A:h,2:h/ {...}\n"
              "If hands is only made by one hand, please also input:\n"
              "hand_owner(N,E,S,W) number_of_simulations")
