from typing import Dict

#from bridge_playing_phase_gen import *

from game.game_structures import *
from game.game_state import GameState
from game.hand_gen import generate_hands_mono

from tree.infoset_info import InfosetInfo
from game.bidding_actions import *
from game.bidding_state import BidInfo, BiddingState


n_players = 4
ranks = 3
players = {}
teams = {0:Team(0), 1:Team(1)}
hands = generate_hands_mono(n_players, ranks)
for i in range(n_players):
    # creating players ...
    # hashmap id - player instance
    players[i] = Player(i, hands[i])
    print(players[i].hand_description())
    if i%2 == 0:
        teams[0].add_member(players[i])
    else:
        teams[1].add_member(players[i])

state = BiddingState(players, teams, ranks)

print(state.get_curr_bid_info())

av = state.available_actions()
for a in av:
    print(str(a))

print("player taking action...")
state.push_action(av[5])

print(state.gen_infoset_name())
print(state.get_curr_bid_info())
av = state.available_actions()
for a in av:
    print(str(a))

av = state.available_actions()
print("player taking action...")
state.push_action(av[1])

print(state.gen_infoset_name())
print(state.get_curr_bid_info())
av = state.available_actions()


"""
n_players = 4
ranks = 2
trump = Suit.diamonds
starting_player = 0
players = {}

hands = generate_hands(n_players, ranks)

for i in range(n_players):
    # creating players ...
    # hashmap id - player instance
    players[i] = Player(i, hands[i])
    print(players[i].hand_description())

game = GameState(players, ranks, trump, starting_player)

last_sequence: Dict[int, Sequence] = {}
infosets: Dict[int, Dict[str, InfosetInfo]] = {}
for p in players:
    infosets[p] = {}
    # init root sequence -> no action performed
    last_sequence[p] = Sequence()

explore_tree(game, last_sequence, infosets)

print("\nInfosets")
for p in infosets.keys():
    print("Player %d" % (p+1))
    for info in infosets[p].values():
        print(info)

print("\nBuilding parent-sequence-to-infoset map for player 1")
p1_map = build_parent_seq_to_infoset_map(infosets[0])
for (seq, infoset_list) in p1_map.items():
    print("Sequence " + str(seq) + "\t")
    for infoset in infoset_list:
        print("\t" + str(infoset))


print("\nSorting infosets following a depth-first approach")
sorted_p1_list = dfs_sort_infosets(p1_map)
for infoset in sorted_p1_list:
    print(infoset)


print("\nAssigning sequence numbers")
seq_numbers = assign_sequence_numbers(sorted_p1_list)
for (seq, id) in seq_numbers.items():
    print("Sequence " + str(seq) + ": " + str(id))

print("\nResulting treeplex for player 1")
treeplex = create_treeplex(players[0], sorted_p1_list, seq_numbers)
print(str(treeplex))
"""
