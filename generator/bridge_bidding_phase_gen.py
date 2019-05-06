import datetime, time

from game.game_structures import *
from game.hand_gen import generate_hands
from game.bidding_state import BiddingState

from tree.exploration_functions import *

from logger import Logger

LogID = "logs/Bidding/BiddingGenLog_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
OutID = "output/Bidding/BiddingGenOut_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')


# This function returns (Max_payoff_Team_0, Min_payoff_Team_0, Max_payoff_Team_1, Min_payoff_Team_1)
def explore_tree(game_state: BiddingState, last_sequence: Dict[PlayerId, Sequence],
                 infosets: Dict[PlayerId, Dict[str, InfosetInfo]], payoff_mat: PayoffMatrix):
    ret_payoff = [0,0,0,0]
    if not game_state.is_game_over():
        # gathering all information
        player = game_state.get_current_player_id()
        parent_sequence = last_sequence[player]

        infoset_name = game_state.gen_infoset_name()
        available_actions = game_state.available_actions()

        # retrieving the correct infoset if it exists or generating a new one otherwise
        infoset_id = 0
        player_infosets = infosets[player]

        if infoset_name in player_infosets.keys():
            entry = player_infosets[infoset_name]
            infoset_id = entry.info_id
        else:
            infoset_id = len(player_infosets)
            infoset_info = InfosetInfo(infoset_id, infoset_name, parent_sequence, available_actions.copy())
            player_infosets[infoset_name] = infoset_info

        for action in available_actions:
            last_sequence[player] = Sequence(infoset_id, action)

            check_maxmin = []
            game_state.push_action(action)
            check_maxmin = explore_tree(game_state, last_sequence.copy(), infosets, payoff_mat)
            game_state.pop_action()
            for i in range(4): #Max and Min payoff for each of 2 teams
                if i%2 == 0:
                    if check_maxmin[i] > ret_payoff[i]:
                        ret_payoff[i] = check_maxmin[i]
                else:
                    if check_maxmin[i] < ret_payoff[i]:
                        ret_payoff[i] = check_maxmin[i]
        return ret_payoff
    else:
        #game is over
        #evaluate utility for both teams
        key = tuple(last_sequence.values())
        assert key not in payoff_mat.keys(), "duplicate payoff matrix key! using last sequences not feasible"
        if game_state.get_curr_bid_info().last_bid is None:
            payoff = 0
            payoff_mat[key] = ({0: payoff, 1: payoff}, CHANCE_VALUE)
        else:
            payoff = payoff_evaluator(last_sequence, game_state)
            payoff_mat[key] = ({0: payoff, 1: -payoff}, CHANCE_VALUE)
        ret_payoff = [payoff, payoff, -payoff, -payoff]
        return ret_payoff



def payoff_evaluator(last_sequence: Dict[PlayerId, Sequence], game_state: BiddingState):
    # TODO Double dummy solver, this function returns the payoff for Team 0
    return 1



"""
Main function of the playing phase
"""
def main_bidding_phase(n_players: int, ranks: int, hands: List[Dict[PlayerId, List[Card]]], verbose = True):
    if verbose == True:
        verbose_log = Logger(LogID)
    output = Logger(OutID)

    teams = {0: Team(0), 1: Team(1)}
    games = []
    games_number = len(hands)

    global CHANCE_VALUE
    CHANCE_VALUE = 1 / games_number

    for i in range(n_players):
        if i % 2 == 0:
            teams[0].add_member(i)
        else:
            teams[1].add_member(i)

    output.log_line("# info")
    output.log_line("Bridge Bidding Phase")

    output.log_str("{}".format(n_players) + "\n")
    if verbose == True:
        verbose_log.log_line("# Bridge Bidding Game")
        verbose_log.log_line("{} players".format(n_players))


    for j in range(games_number):
        games.append(BiddingState(n_players, teams, ranks, hands[j]))
        if verbose== True:
            verbose_log.log_line("Game {}".format(j))
        for i in range(n_players):
            if verbose== True:
                verbose_log.log_line("\t{}".format(gen_hand_description(i, hands[j][i])))
    if verbose == True:
        verbose_log.log_line("Team 1: " + str(teams[0].members))
        verbose_log.log_line("Team 2: " + str(teams[1].members))

    print("Generating bidding phase...")

    #support 2-3-4 players
    assert n_players > 1 and n_players <= 4
    assert ranks > 0 and ranks <= 13
    for h in hands:
        for hand in h.values():
            assert len(hand) == ranks*4/n_players

    infosets: Dict[PlayerId, Dict[str, InfosetInfo]] = {}
    last_sequence: Dict[PlayerId, Sequence] = {}
    payoff_mat: PayoffMatrix = {}

    for p in range(n_players):
        # init infoset dictionary
        infosets[p] = {}
        # init root sequence -> no action performed
        last_sequence[p] = Sequence()


    maxmin_payoff = []

    # generating the infosets
    for game in games:
        for s in last_sequence.values():
            s = Sequence()
        maxmin_payoff = explore_tree(game, last_sequence, infosets, payoff_mat)

    # 1. build the map sequence -> infoset where the sequence is the parent of the corresponding infosets
    # 2. sort the infosets according to a DFS order
    sorted_infosets: Dict[PlayerId, List[InfosetInfo]] = {}
    for player_id in range(n_players):
        map = build_parent_seq_to_infoset_map(infosets[player_id])
        sorted_infosets[player_id] = dfs_sort_infosets(map)

    # debug print
    if verbose == True:
        for (pid, si) in sorted_infosets.items():
            verbose_log.log_line("\nPlayer {} sorted infosets:".format(pid+1))
            for infoset in si:
                verbose_log.log_line("\t{}".format(infoset))



    # assign a number to each sequence
    sequence_numbering: Dict[PlayerId, Dict[Sequence, int]] = {}
    for player_id in range(n_players):
        sequence_numbering[player_id] = assign_sequence_numbers(sorted_infosets[player_id])
        if verbose== True:
            verbose_log.log_line("\nPlayer " + str(player_id + 1) + " sequences:")
            for (seq, num) in sequence_numbering[player_id].items():
                verbose_log.log_line("\tSeq " + str(num) + ": " + str(seq))
        output.log_str("{} ".format(len(sequence_numbering[player_id])) + "\t")
    output.log_str("\n")

    for player_id in range(n_players):
        output.log_str("{} ".format(len(sorted_infosets[player_id])) + "\t")
    output.log_str("\n")



    output.log_line("zero-sum")

    if verbose== True:
        verbose_log.log_str("\n\n # Number of sequences per player\n\n")
        for player_id in range(n_players):
            verbose_log.log_str("{} ".format(len(sequence_numbering[player_id])))
            verbose_log.log_str("sequences for Player {} \n".format(player_id))
        verbose_log.log_line("")


    for player_id in range(n_players): #max and min payoff for each player
        if player_id % 2 == 0:
            output.log_str("{} ".format(maxmin_payoff[0]))
            output.log_str(" {} ".format(maxmin_payoff[1]) + "\t")
        else:
            output.log_str("{} ".format(maxmin_payoff[2]))
            output.log_str(" {} ".format(maxmin_payoff[3]) + "\t")

    output.log_line("\n-------------------------")

    output.log_line("# game specific info")
    output.log_line("-------------------------")

    # creating a map of treeplexes
    output.log_line("# treeplex")
    treeplexes: Dict[PlayerId, Treeplex] = {}
    for player_id in range(n_players):
        output.log_line("==== Player " + str(player_id + 1))
        treeplexes[player_id] = create_treeplex(player_id, sorted_infosets[player_id], sequence_numbering[player_id])
        # debug print
        s = ""
        for infoset in treeplexes[player_id].infosets:
            s += "{}\n".format(infoset.short_str())
        output.log_line(s)

    output.log_line("# Utility matrix. Sequences of players 1..n that reach the outcome - Team1 utility - Team2 utility - chance value")
    for (sequences, (pay_dict, chance)) in payoff_mat.items():
        for i in range(n_players):
            numbering = sequence_numbering[i]
            seq = sequences[i]
            output.log_str(str(numbering[seq]) + "  ")
        for (team, util) in pay_dict.items():
            output.log_str("{} ".format(util))
        output.log_line("{}".format(chance))

    print("Process ended")
    print("The output file has been saved as: " + LogID)
    if verbose== True:
        verbose_log.close_logger()





n_players = 4
ranks = 2

hands = [
    {
        0: [
            Card(Suit.diamonds, 2),
            Card(Suit.spades, 2)
        ],
        1: [
            Card(Suit.clubs, 1),
            Card(Suit.spades, 1)
        ],
        2: [
            Card(Suit.clubs, 2),
            Card(Suit.hearts, 2)
        ],
        3: [
            Card(Suit.diamonds, 1),
            Card(Suit.hearts, 1)
        ]
    },
    {
        0: [
            Card(Suit.diamonds, 2),
            Card(Suit.spades, 2)
        ],
        1: [
            Card(Suit.diamonds, 1),
            Card(Suit.clubs, 1)
        ],
        2: [
            Card(Suit.clubs, 2),
            Card(Suit.hearts, 2)
        ],
        3: [
            Card(Suit.hearts, 1),
            Card(Suit.spades, 1)
        ]
    }
]


main_bidding_phase(n_players, ranks, hands)
