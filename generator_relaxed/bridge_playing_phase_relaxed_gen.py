import datetime
import time
from generator_relaxed.game.game_state import *
from misc.hand_gen import generate_hands
from generator_relaxed.tree.exploration_functions import *
from generator_relaxed.logger import Logger
import generator_relaxed.game.reward as reward
import sys
import os


dir_path = os.path.dirname(__file__)
LogID = os.path.join(dir_path, "logs/Playing/PlayingGenLog_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S'))
OutID = os.path.join(dir_path, "output/Playing/PlayingGenOut_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S'))

CHANCE_VALUE = 0.0

reward_calculator = reward.RewardNumberOfTricks()


def explore_tree(game_state: GameState, last_sequence: Dict[PlayerId, Sequence],
                 infosets: Dict[PlayerId, Dict[str, InfosetInfo]], payoff_mat: PayoffMatrix):
    """
    Explore the game tree to fill the infosets and payoff data
    """
    if not game_state.is_game_over():
        # gathering all information
        # getting declarer id instead of dummy one
        player = game_state.fix_id(game_state.get_current_player_id())
        parent_sequence = last_sequence[player]

        infoset_name = game_state.gen_infoset_name()
        available_actions = game_state.available_actions()

        # retrieving the correct infoset if it exists or generating a new one otherwise
        # the id will be overwritten anyway, the assignment is just to create the variable
        infoset_id = 0
        player_infosets = infosets[player]

        # use the name attribute to identify the infosets and see if they've been already analysed
        if infoset_name in player_infosets.keys():
            # update the id with the already existing id
            entry = player_infosets[infoset_name]
            infoset_id = entry.info_id
        else:
            # generate the id to continue the succession
            infoset_id = len(player_infosets)
            infoset_info = InfosetInfo(infoset_id, infoset_name, parent_sequence, available_actions.copy())
            player_infosets[infoset_name] = infoset_info

        for action in available_actions:
            last_sequence[player] = Sequence(infoset_id, action)

            game_state.push_action(action)
            explore_tree(game_state, last_sequence.copy(), infosets, payoff_mat)
            game_state.pop_action()

    else:
        # game is over
        # determine the winner(s) of the game and push the utilities in the payoff matrix
        rewards = reward_calculator.compute(game_state)

        # current payoff = number of tricks won
        key = tuple(last_sequence.values())
        payoff_mat[key] = (rewards, CHANCE_VALUE)


def main_playing_phase(n_players: int, ranks: int, bid: Bid, declarer: int, hands: List[Dict[PlayerId, List[Card]]]):
    """
    Main function of the playing phase. Tests a finite number of combinations of hands, keeping the bid constant.
    """
    verbose_log = Logger(LogID)
    output = Logger(OutID)

    hands_str_list = [gen_card_distribution_str(hand_distr) for hand_distr in hands]

    teams = {0: Team(0), 1: Team(1)}

    games = []
    games_number = len(hands)

    # buffers used to store information to be printed in output file
    output_buffer_info = f"### info\nBridge playing phase - relaxed version: the defenders can see each other's hand and are therefore treated as the same player\n{n_players}\n{ranks}\n"
    output_buffer_game = "### game specific info\n"
    output_buffer_tree = "### treeplexes\n"
    output_buffer_util = "### utility matrix\n"

    output_buffer_game += "# winning bid - declarer - n.games\n"
    output_buffer_game += f"{bid}, {PID_TO_CARDINAL[declarer]}, {games_number}\n"
    output_buffer_game += '\n'.join(hands_str_list)

    global CHANCE_VALUE
    CHANCE_VALUE = 1 / games_number

    for i in range(n_players):
        teams[i % 2].add_member(i)

    defenders = []
    for team in teams.values():
        if declarer not in team.members:
            defenders = team.members
    second_defender = defenders[1] if len(defenders) == 2 else -1

    for j in range(games_number):
        verbose_log.log_line("Game {}".format(j))
        games.append(GameState(n_players, teams, hands[j], ranks, bid, declarer))

        for i in range(n_players):
            verbose_log.log_line("\t{}".format(gen_hand_description(i, hands[j][i])))

    dummy_id = games[0].dummy_id

    verbose_log.log_line("Team 1: " + ', '.join([PID_TO_CARDINAL[member] for member in teams[0].members]))
    verbose_log.log_line("Team 2: " + ', '.join([PID_TO_CARDINAL[member] for member in teams[1].members]))

    print("Generating playing phase...")

    # support 2-3-4 players
    assert 1 < n_players <= 4
    assert 0 <= declarer < n_players
    assert 0 < ranks <= 13
    for h in hands:
        for hand in h.values():
            assert len(hand) == ranks * 4 / n_players

    verbose_log.log_line(f"Winning bid: {bid}, {PID_TO_CARDINAL[declarer]}")
    logstr = f"Declarer: {PID_TO_CARDINAL[declarer]}"
    if games[0].dummy_exists:
        logstr += f", dummy: {PID_TO_CARDINAL[dummy_id]}"
    verbose_log.log_line(logstr)

    infosets: Dict[PlayerId, Dict[str, InfosetInfo]] = {}
    last_sequence: Dict[PlayerId, Sequence] = {}
    payoff_mat: PayoffMatrix = {}

    for p in range(n_players):
        # init infoset dictionary
        infosets[p] = {}
        # init root sequence -> no action performed
        last_sequence[p] = Sequence()

    # generating the infosets
    for game in games:
        for s in last_sequence.values():
            s = Sequence()
        explore_tree(game, last_sequence, infosets, payoff_mat)

    # 1. build the map sequence -> infoset where the sequence is the parent of the corresponding infosets
    # 2. sort the infosets according to a DFS order
    sorted_infosets: Dict[PlayerId, List[InfosetInfo]] = {}
    for player_id in range(n_players):
        if player_id != dummy_id and player_id != second_defender:
            map = build_parent_seq_to_infoset_map(infosets[player_id])
            sorted_infosets[player_id] = dfs_sort_infosets(map)

    # debug print
    for (pid, si) in sorted_infosets.items():
        verbose_log.log_line(f"\n{PID_TO_CARDINAL[pid]} sorted infosets:")
        for infoset in si:
            verbose_log.log_line("\t" + str(infoset))

    # assign a number to each sequence
    sequence_numbering: Dict[PlayerId, Dict[Sequence, int]] = {}
    for player_id in range(n_players):
        if player_id != dummy_id and player_id != second_defender:
            verbose_log.log_line(f"\n{PID_TO_CARDINAL[player_id]} sequences:")
            sequence_numbering[player_id] = assign_sequence_numbers(sorted_infosets[player_id])
            for (seq, num) in sequence_numbering[player_id].items():
                verbose_log.log_line("\tSeq " + str(num) + ": " + str(seq))
    verbose_log.log_line("")

    # creating a map of treeplexes
    treeplexes: Dict[PlayerId, Treeplex] = {}
    for player_id in range(n_players):
        if player_id != dummy_id and player_id != second_defender:
            treeplexes[player_id] = create_treeplex(player_id, sorted_infosets[player_id],
                                                    sequence_numbering[player_id])
            # debug print
            verbose_log.log_line(treeplexes[player_id])
            output_buffer_tree += treeplexes[player_id].short_str()

    output_buffer_info += f"{ ' '.join(str(tree.num_sequences) for tree in treeplexes.values()) }\n"
    infosets_count = []
    for _, info_list in sorted_infosets.items():
        infosets_count.append(len(info_list))
    output_buffer_info += f"{ ' '.join(str(c) for c in infosets_count) }\n"
    output_buffer_info += f"{reward_calculator.type}\n"

    # handling payoffs
    min_payoffs = {
        0: 10000,
        1: 10000
    }
    max_payoffs = {
        0: 0,
        1: 0
    }
    for (sequences, (pay_dict, chance)) in payoff_mat.items():
        verbose_log.log_str(f"Chance: {chance}, Seq: ")
        for i in range(n_players):
            if i != dummy_id and i != second_defender:
                numbering = sequence_numbering[i]
                seq = sequences[i]
                verbose_log.log_str(str(numbering[seq]) + "  ")
                output_buffer_util += f"{numbering[seq]} "
            else:
                verbose_log.log_str("empty  ")
                output_buffer_util += "e "
        verbose_log.log_str("\n")
        for (team, util) in pay_dict.items():
            if util < min_payoffs[team]:
                min_payoffs[team] = util
            if util > max_payoffs[team]:
                max_payoffs[team] = util
            verbose_log.log_line("\tTeam " + str(team + 1) + " util: " + str(util))
            output_buffer_util += f"{util} "
        output_buffer_util += f"{chance}\n"

    output_buffer_info += f"{ ' '.join( f'{min_payoffs[team]} {max_payoffs[team]}' for team in [0,1]) }\n"

    output.log_str(output_buffer_info)
    output.log_line(output_buffer_game)
    output.log_str(output_buffer_tree)
    output.log_line(output_buffer_util)
    output.close_logger()
    print("Process ended")
    print("The output file has been saved as: " + LogID)
    verbose_log.close_logger()


# ======================================================================================================================


if __name__ == "__main__":
    args = sys.argv
    if len(sys.argv) == 7:
        # called from command line
        # syntax: n_players ranks game_number bid trump declarer
        args.pop(0)

        n_players = int(args[0])
        ranks = int(args[1])
        n_games = int(args[2])
        bid_val = int(args[3])
        trump = args[4]
        assert args[5] in CARDINAL_TO_PID.keys(), "ERROR: invalid declarer, use N, E, S or W"
        declarer = CARDINAL_TO_PID[args[5]]

        hands = generate_hands(n_players, ranks, n_games)
        main_playing_phase(n_players, ranks, Bid(bid_val, import_suit_from_char(trump)), declarer, hands)
    else:
        print("Please insert the following parameters:\n"
              "n_players n_ranks n_games_to_simulate bid_value trump(c,d,h,s,n) declarer(N,E,S,W)")

        # default generation
        # n_players = 4
        # ranks = 3
        # h = generate_hands(n_players, ranks, game_number=5)
        # main_playing_phase(n_players, ranks, Bid(3, Suit.notrump), 1, h)
