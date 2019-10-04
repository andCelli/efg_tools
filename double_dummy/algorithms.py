"""
For any particular deal, given the declarer and the trump suit (or notrump), the double dummy result is the number of
tricks the declarer will win when all four players can see all 52 cards, and each player always plays to his or her best
advantage.
A complete DDA consists of 20 results, calculated by considering, in turn, each of the four players as declarer playing
in each of the five strains (four possible trump suits plus notrump).

******

Given declarer + bid, how many tricks can his team win?
"""

from misc.game_structures import *
import double_dummy.game.game_state as gs
from double_dummy.tree_exploration import ab_search
import time
import statistics
from typing import Dict
import random
import sys


ERROR_WRONG_NUM_OF_PLAYERS = "The number of players is not compatible with the number of hands given"
ERROR_DIFFERENT_HAND_SIZES = "The hands do not contain the same number of cards"
ERROR_WRONG_SET_OF_CARDS = "The cards do not make a legal deck of cards, please use all cards from A to the max rank for " \
                           "each suit"
ERROR_INCOMPATIBLE_RANKS = "The number of ranks is incompatible with the number of players, change the deck size so that " \
                           "each player gets the same number of cards"
ERROR_DUPLICATE_CARDS = "There are duplicates among the declarer's cards"
ERROR_ILLEGAL_RANK = "There are cards that exceed the maximum rank"
ERROR_ILLEGAL_HAND_OWNER = "You must specify a hand owner when giving only one player hand (use parameter hand_owner)"


_DEBUG = True


class DDAMatrix:
    def __init__(self, n_players):
        self._mat = {}

        # init values to -1
        for pid in range(n_players):
            for suit in Suit:
                self._mat[pid, suit.to_char()] = -1

    def __setitem__(self, key, value):
        self._mat[key] = value

    def __getitem__(self, item):
        return self._mat[item]

    def __str__(self):
        return str([f"{PID_TO_CARDINAL[key[0]]},{key[1]}:{self._mat[key]}" for key in self._mat.keys()])


def _check_hand_list(hands: Dict[PlayerId, List[Card]]):
    """
    Performs basic checks on a list of hands. Throws errors if problems are found.
    """
    # check all hands contain the same number of cards
    # check that all cards are present
    ranks = len(hands[0])
    deck = Deck(ranks)
    cards = []
    for hand in hands.values():
        assert len(hand) == ranks, ERROR_DIFFERENT_HAND_SIZES
        cards += hand
    assert set(deck.cards) == set(cards), ERROR_WRONG_SET_OF_CARDS


def _check_hand_declarer(hand: List[Card], ranks):
    # all cards must be different
    hand_set = set(hand)
    assert len(hand) == len(hand_set), ERROR_DUPLICATE_CARDS
    # all cards must have lower rank than 'ranks'
    for card in hand:
        assert card.rank <= ranks, ERROR_ILLEGAL_RANK


def _generate_game(hands, n_players: int, declarer: PlayerId, hand_owner: PlayerId, trump: str):
    """
    Generate the game given the following parameters:
    :param hands_str: string that describes the hands of the players. The strings need to be of the format
    'rank:suit,rank:suit,...', where each hand is separated by a forward slash /.
    Spaces are allowed. The list can either contain the hands of all the players OR the hand
    of the declarer. In the latter case, the other hands will be randomly generated. The length of the hands represent
    the ranks of the cards.
    :param n_players: number of players.
    :param declarer: id of the declarer.
    :param hand_owner: id of the owner of the hand, in case only one hand is passed to the algorithm. Can be different
    from the declarer.
    :param trump: str containing the trump. It can be 'c', 'd', 'h', 's' or 'n' (no trump).
    :return: generated GameState object and hands used (includes sampled hands).
    """
    assert 2 <= n_players <= 4
    assert len(hands) == 1 or len(hands) == n_players, ERROR_WRONG_NUM_OF_PLAYERS

    if len(hands) == 1:
        # need to sample hands
        aux_hands = {}
        aux_hands[hand_owner] = hands[0]
        ranks = n_players*len(aux_hands[hand_owner])/4
        assert ranks*4 % n_players == 0 and ranks.is_integer(), ERROR_INCOMPATIBLE_RANKS
        _check_hand_declarer(aux_hands[hand_owner], ranks)

        deck = Deck(int(ranks))
        available_cards = set(deck.cards) - set(aux_hands[hand_owner])

        for cur_player in range(n_players):
            if cur_player != hand_owner:
                aux_hands[cur_player] = []
                # draw cards
                for j in range(len(aux_hands[hand_owner])):
                    card = random.sample(available_cards, 1)[0]
                    aux_hands[cur_player].append(card)
                    available_cards.remove(card)

        hands = aux_hands

        if _DEBUG:
            for cur_player in sorted(hands.keys()):
                print(PID_TO_CARDINAL[cur_player], [card.short_string() for card in hands[cur_player]])

    else:
        _check_hand_list(hands)
        ranks = len(hands[0])

    teams = {0: Team(0), 1: Team(1)}
    for j in range(n_players):
        teams[j % 2].add_member(j)

    suits = {
        'c': Suit.clubs,
        'd': Suit.diamonds,
        'h': Suit.hearts,
        's': Suit.spades,
        'n': Suit.notrump
    }

    return gs.GameState(n_players, hands, ranks, suits[trump], declarer,
                        teams[declarer % 2].get_other_member(declarer)), hands


def dda_simple(hands, n_players: int, trump: str, declarer: PlayerId, hand_owner=-1, times=1, debug=True):
    """
    Run alpha-beta search algorithm on a single game, given the bid, the declarer and the hand of the declarer or all
    the hands.
    :param hands
    :param n_players: number of players.
    :param declarer: id of the declarer.
    :param hand_owner: id of the owner of the hand, in case only one hand is passed to the algorithm. Can be different
    from the declarer.
    :param trump: str containing the trump. It can be 'c', 'd', 'h', 's' or 'n' (no trump).
    :param times: number of analysis to perform. To be used in case of sampling of hands. If hands_str has more than
    one item, it is considered as a representation of all the hands, therefore times will be reset to 1 anyway.
    :return: value of the DDA analysis.
    """
    if len(hands) != 1:
        times = 1
    else:
        assert 0 <= hand_owner < n_players, ERROR_ILLEGAL_HAND_OWNER
    result_array = []
    if debug:
        print("Processing...")
    for i in range(times):
        if debug:
            print(f"Game {i}")
        game, _ = _generate_game(hands, n_players, declarer, hand_owner, trump)
        result_array.append(ab_search(game))
    result = statistics.mean(result_array)
    if debug:
        print(f"DDA analysis completed. The value is: {result}")
    return result


def dda_extended(hands, n_players: int, hand_owner=-1, times=1):
    """
    Run alpha-beta search algorithm on multiple games. All games are analysed using the same hands, while each game has
    a different declarer-trump combination.
    :param hands:
    :param n_players: number of players.
    :param hand_owner: id of the owner of the hand, in case only one hand is passed to the algorithm. Can be different
    from the declarer.
    :param times: number of analysis to perform. To be used in case of sampling of hands. If hands_str has more than
    one item, it is considered as a representation of all the hands, therefore times will be reset to 1 anyway.
    :return: DDAMatrix object containing the results. DDAMatrix is a dictionary where the keys are tuples made of the
    declarer id (0, 1, 2 or 3, if there are 4 players) and the trump ('c', 'd', 'h', 's' or 'n').
    """
    result_mat = DDAMatrix(n_players)
    new_hands = None
    if len(hands) != 1:
        # if no sampling is needed, then it's useless to do multiple runs
        times = 1
    else:
        assert 0 <= hand_owner < n_players, ERROR_ILLEGAL_HAND_OWNER
    print("Processing...")
    for i in range(times):
        print(f"Game {i}")
        for declarer in range(n_players):
            for trump in Suit:
                game, new_hands = _generate_game(hands if new_hands is None else new_hands,
                                                 n_players, declarer, hand_owner, trump.to_char())
                result = ab_search(game)
                old = result_mat[declarer, trump.to_char()]
                result_mat[declarer, trump.to_char()] = (old*i + result)/(i+1)
                # print(f"old mean = {old}, new mean = {result_mat[declarer, trump.to_char()]}, result added = {result}, new count = {i+1}")
        new_hands = None
    print(f"DDA analysis completed. The values are: {result_mat}")
    return result_mat


if __name__ == '__main__':
    h1 = "2:s,A:s,3:s"
    h4 = "2:s,A:s,3:s/2:c,3:c,A:c/2:d,3:d,A:d/2:h,3:h,A:h"
    n = 4
    d = 0
    t = 's'

    dh1 = import_multiple_hands(h1)
    dh4 = import_multiple_hands(h4)

    dda_simple(dh1, n, t, d, hand_owner=0, times=1)
    dda_extended(dh1, n, hand_owner=2, times=20)
