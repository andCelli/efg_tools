import datetime, time

from game.game_structures import *
from game.game_state import *
from game.hand_gen import generate_hands

from tree.exploration_functions import *

from logger import Logger

LogID = "logs/Playing/PlayingGenLog_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
OutID = "output/Playing/PlayingGenOut_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')

CHANCE_VALUE = 0.0

"""
Explore the game tree to fill the infosets and payoff data
"""


def explore_tree(game_state: GameState, last_sequence: Dict[PlayerId, Sequence],
                 infosets: Dict[PlayerId, Dict[str, InfosetInfo]], payoff_mat: PayoffMatrix):
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
        # assert that the total number of tricks won is equal to the number of turns played
        tricks_won = game_state.get_curr_turn_info().tricks_won
        assert sum(tricks_won.values()) == game_state.ranks * 4 / game_state.n_players, "turn_info.tricks_won ill-posed"

        team1_tricks = team2_tricks = 0
        for (tid, team) in game_state.teams.items():
            for pid in team.members:
                tricks = tricks_won[pid]
                if tid == 0:
                    team1_tricks += tricks
                else:
                    team2_tricks += tricks

        # current payoff = number of tricks won
        key = tuple(last_sequence.values())
        assert key not in payoff_mat.keys(), "duplicate payoff matrix key! using last sequences not feasible"
        payoff_mat[key] = ({0: team1_tricks, 1: team2_tricks}, CHANCE_VALUE)


"""
Main function of the playing phase
"""
def main_playing_phase(n_players: int, ranks: int, bid: Bid, starting_player: int, hands: List[Dict[PlayerId, List[Card]]]):
    verbose_log = Logger(LogID)
    output = Logger(OutID)

    teams = {0: Team(0), 1: Team(1)}

    games = []
    games_number = len(hands)

    #print printing general info on output
    output.log_line("# n.players - ranks - winning bid - bid winner (player id starts from 1) - n.games")
    output.log_line("{} {} {} {} {}".format(n_players, ranks, bid, starting_player+1, games_number))

    global CHANCE_VALUE
    CHANCE_VALUE = 1 / games_number

    for i in range(n_players):
        if i % 2 == 0:
            teams[0].add_member(i)
        else:
            teams[1].add_member(i)

    output.log_line("# hands of each player, for each game. PlayerID/cards")
    for j in range(games_number):
        verbose_log.log_line("Game {}".format(j))
        games.append(GameState(n_players, teams, hands[j], ranks, bid, starting_player))

        for i in range(n_players):
            verbose_log.log_line("\t{}".format(gen_hand_description(i, hands[j][i])))
            output.log_line("{}".format(gen_short_hand_desc(i, hands[j][i])))

    dummy_id = games[0].dummy_id

    verbose_log.log_line("Team 1: " + str(teams[0].members))
    verbose_log.log_line("Team 2: " + str(teams[1].members))

    print("Generating playing phase...")

    # support 2-3-4 players
    assert 1 < n_players <= 4
    assert 0 <= starting_player < n_players
    assert 0 < ranks <= 13
    for h in hands:
        for hand in h.values():
            assert len(hand) == ranks * 4 / n_players

    verbose_log.log_line("Winning bid: {}, player {}".format(bid, starting_player + 1))
    logstr = "Declearer: P{}".format(starting_player + 1)
    if games[0].dummy_exists:
        logstr += ", dummy: P" + str(dummy_id + 1)
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
        if player_id != dummy_id:
            map = build_parent_seq_to_infoset_map(infosets[player_id])
            sorted_infosets[player_id] = dfs_sort_infosets(map)

    # debug print
    for (pid, si) in sorted_infosets.items():
        verbose_log.log_line("\nPlayer " + str(pid + 1) + " sorted infosets:")
        for infoset in si:
            verbose_log.log_line("\t" + str(infoset))

    # assign a number to each sequence
    sequence_numbering: Dict[PlayerId, Dict[Sequence, int]] = {}
    for player_id in range(n_players):
        if player_id != dummy_id:
            verbose_log.log_line("\nPlayer " + str(player_id + 1) + " sequences:")
            sequence_numbering[player_id] = assign_sequence_numbers(sorted_infosets[player_id])
            for (seq, num) in sequence_numbering[player_id].items():
                verbose_log.log_line("\tSeq " + str(num) + ": " + str(seq))
    verbose_log.log_line("")

    output.log_line("# Treeplexes. First line is player id (starting from 1) - number of sequences of the treeplex. Following lines are start_sequence - end_sequence - parent_sequence")
    # creating a map of treeplexes
    treeplexes: Dict[PlayerId, Treeplex] = {}
    for player_id in range(n_players):
        if player_id != dummy_id:
            treeplexes[player_id] = create_treeplex(player_id, sorted_infosets[player_id],
                                                    sequence_numbering[player_id])
            # debug print
            verbose_log.log_line(treeplexes[player_id])
            output.log_str(treeplexes[player_id].short_str())

    output.log_line("# Payoff matrix. Sequences of players 1..n that reach the outcome - Team1 utility - Team2 utility - chance value. 'e' means empty sequence, symbolizes dummy player")
    for (sequences, (pay_dict, chance)) in payoff_mat.items():
        verbose_log.log_str("Chance: {}, Seq: ".format(chance))
        for i in range(n_players):
            if i != dummy_id:
                numbering = sequence_numbering[i]
                seq = sequences[i]
                verbose_log.log_str(str(numbering[seq]) + "  ")
                output.log_str("{} ".format(numbering[seq]))
            else:
                verbose_log.log_str("empty  ")
                output.log_str("e ")
        verbose_log.log_str("\n")
        for (team, util) in pay_dict.items():
            verbose_log.log_line("\tTeam " + str(team + 1) + " util: " + str(util))
            output.log_str("{} ".format(util))
        output.log_line("{}".format(chance))

    print("Process ended")
    print("The output file has been saved as: " + LogID)
    verbose_log.close_logger()
    output.close_logger()


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

# generate_hands(n_players, ranks, game_number=2)
main_playing_phase(n_players, ranks, Bid(3, Suit.clubs), 0, hands)
