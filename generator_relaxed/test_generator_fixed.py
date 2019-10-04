import os
import sys
import generator_relaxed.bridge_playing_phase_relaxed_gen as gen
from misc.hand_gen import generate_hands_fixed
from misc.game_structures import Bid, import_suit_from_char, CARDINAL_TO_PID


parent_path = os.path.join(gen.dir_path, "../test_files_fixed/")


if __name__ == "__main__":
    args = sys.argv
    if len(sys.argv) == 9:
        args.pop(0)

        n_players = int(args[0])
        min_ranks = int(args[1])
        max_ranks = int(args[2])
        bid_value = int(args[3])
        trump = import_suit_from_char(args[4])
        assert args[5] in CARDINAL_TO_PID.keys(), "ERROR: invalid declarer, use N, E, S or W"
        declarer = CARDINAL_TO_PID[args[5]]
        n_games = int(args[6])
        n_samples = int(args[7])

        for ranks in range(min_ranks, max_ranks + 1):
            path = os.path.join(parent_path, f"{ranks}_ranks/")
            for idx in range(n_games):
                print(f"Generating game {idx} of {ranks} ranks block...")
                gen.OutID = os.path.join(path, f"test{idx}")
                hands = generate_hands_fixed(n_players, ranks, declarer, fix_dummy=True, game_number=n_samples)
                bid = Bid(bid_value, trump)
                gen.main_playing_phase(n_players, ranks, bid, declarer, hands)

        print("All games generated. You can find them in the test_files_fixed folder.")

    else:
        print("Please insert the following parameters:\n"
              "n_players min_ranks max_ranks bid_value trump(c,d,h,s,n) declarer(N,E,S,W) n_games_for_each_rank "
              "n_samplings_for_each_game")

        # n_players = 4
        # min_ranks = 2
        # max_ranks = 4
        # trump = 'n'
        # declarer = 0
        # n_games = 5
        # bid_value = 1
