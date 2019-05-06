from typing import Dict, List

import random

from game.game_structures import Card, Deck
from tree.exploration_functions import PlayerId


def generate_hands(n_players, ranks, game_number = 1):
    """
    Generate a game given the number of players and the number of cards per suit.
    Returns a dictionary of hands, cards are ordered by rank.
    The keys are the players ids (0, 1, 2, ...).
    """
    def generate_hands_mono (n_players, ranks) -> Dict[PlayerId, List[Card]]:
        assert (ranks*4)%n_players == 0, "choose a rank number such that each player has the same amount of cards"

        cards = Deck(ranks).cards
        deck = set()
        hands = {}
        for p in range(n_players):
            hands[p] = []

        # Creating a dictionary of cards
        for card in cards:
            deck.add(card)

        # Extracting the players cards
        while len(deck) != 0:
            for player in range(n_players):
                if len(deck) != 0:
                    card = random.choice(list(deck))
                    hands[player].append(card)
                    deck.remove(card)

        # assert all cards have been dealt
        tot = 0
        for p in range(n_players):
            tot += len(hands[p])
        assert tot == ranks * 4, "card dealing error"

        # Sorting cards
        for player in hands.keys():
            hands[player].sort()

        return hands

    """
    Returns true if two sets of hands are equal.
    Hands must be already sorted.
    """
    def compare_hands(h1: Dict[PlayerId, List[Card]], h2: Dict[PlayerId, List[Card]]):
        for p in h1.keys():
            if h1[p] != h2[p]:
                return False
        return True

    hands_list = []

    for i in range(game_number):
        double = True
        hands = 0
        while double:
            double = False
            hands = generate_hands_mono(n_players, ranks)
            for elem in hands_list:
                if compare_hands(elem, hands):
                    double = True

        hands_list.append(hands)

    return hands_list
