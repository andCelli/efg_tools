from enum import IntEnum

from typing import List, Optional
from itertools import product
from collections import OrderedDict


class Suit(IntEnum):
    clubs = 0
    diamonds = 1
    hearts = 2
    spades = 3
    notrump = 4

    def to_char(self) -> str:
        if self == Suit.diamonds:
            return 'd'
        if self == Suit.clubs:
            return 'c'
        if self == Suit.hearts:
            return 'h'
        if self == Suit.spades:
            return 's'
        if self == Suit.notrump:
            return 'n'


def import_suit_from_char(c):
    conv = {
        'c': Suit.clubs,
        'd': Suit.diamonds,
        'h': Suit.hearts,
        's': Suit.spades,
        'n': Suit.notrump
    }
    assert c in conv.keys(), "ERROR: invalid suit, please use c, d, h, s or n"
    return conv[c]


# ======================================================================================================================


rank_conversion = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 1,
}

suit_conversion = {
    'c': Suit.clubs,
    'd': Suit.diamonds,
    'h': Suit.hearts,
    's': Suit.spades
}

legal_cards_set = {
    f"{rank}:{suit}" for rank, suit in product(rank_conversion.keys(), suit_conversion.keys())
}

PID_TO_CARDINAL = {
    0: "N",
    1: "E",
    2: "S",
    3: "W"
}

CARDINAL_TO_PID = {
    'N': 0,
    'E': 1,
    'S': 2,
    'W': 3
}

PlayerId = int


# ======================================================================================================================


class Card:
    def __init__(self, suit: Suit, rank: int):
        assert rank > 0, "cannot create a card with non-positive rank"
        assert suit != Suit.notrump, "cannot create a card with no suit"
        self.rank = rank
        self.suit = suit

    def compare_rank(self, obj: int) -> int:
        """
        Returns 1 if this card rank is higher than the target
        0 if equal
        -1 if lower
        """
        def normalize_ace(a):
            return a+13 if a == 1 else a
        norm_self_rank = normalize_ace(self.rank)
        norm_obj = normalize_ace(obj)

        return 1 if norm_self_rank > norm_obj else (0 if norm_self_rank == norm_obj else -1)

    def compare_to(self, obj, leader: Suit, trump: Optional[Suit]) -> int:
        """
        Compare this card to another card.
        Returns 1 if this card rank is higher than the target, 0 if equal, -1 if lower.
        Leader is the currently leading suit (suit of the first played card),
        trump > leader > else
        """
        if self.suit == obj.suit:
            return self.compare_rank(obj.rank)

        # different suits -> trump wins
        if self.suit == trump:
            return 1
        if obj.suit == trump:
            return -1

        # different suits, no trumps -> leader wins
        if self.suit == leader:
            return 1
        if obj.suit == leader:
            return -1

        return self.compare_rank(obj.rank)

    @staticmethod
    def are_consecutive(card1, card2, ranks=13) -> bool:
        """
        This function returns true if the two parameter cards have consecutive ranks and belong to the same suit.
        The parameter ranks is used for decks smaller than the standard 13 cards-per-suit decks. If, e.g., I have 7
        ranks, the ace is consecutive to the 7.
        The order of the cards in input doesn't matter.
        :param card1: first card
        :param card2: second card
        :param ranks: number of cards per suit in the deck
        :return: True if the cards are consecutive, False otherwise
        """
        assert card1 != card2
        if card1 < card2:
            p = card1
            n = card2
        else:
            p = card2
            n = card1
        if p.suit != n.suit:
            return False
        if n.rank == 1:
            if p.rank == ranks:
                return True
        else:
            if n.rank - p.rank == 1:
                return True
        return False

    def rank_to_char(self):
        if self.rank < 11 and self.rank > 1:
            return self.rank
        else:
            conversion = {
                11: 'J',
                12: 'Q',
                13: 'K',
                1: 'A'
            }
            return conversion[self.rank]

    @staticmethod
    def import_card(s: str):
        """
        Creates a card object from a string of the format '4:c' -> 4 of clubs
        """
        assert s in legal_cards_set, "Error when importing a card: wrong format"
        r = s.split(':')
        return Card(suit_conversion[r[1]], rank_conversion[r[0]])

    def extended_string(self) -> str:
        return str(self.rank_to_char()) + " of " + str(self.suit.name)

    def short_string(self) -> str:
        return str(self.rank_to_char()) + ":" + str(self.suit.to_char())

    def __str__(self):
        return self.short_string()

    def __lt__(self, other):
        return self.suit < other.suit or (other.compare_rank(self.rank) == 1 and self.suit == other.suit)

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    # noinspection PyTypeChecker
    def __hash__(self):
        return self.rank + self.suit * 13


# ======================================================================================================================


def import_single_hand(s: str) -> List[Card]:
    """
    Initialize a list of cards from a string containing cards of the format 'rank:suit', separated by commas.
    White spaces are automatically ignored.
    Example: A:c,2:d,3:h
    """
    result = []
    for c in s.split(','):
        if c != '':
            c = c.replace(' ', '')
            result.append(Card.import_card(c))
    return result


def import_multiple_hands(s: str):
    """
    Initialize a dict of lists of cards from a string containing cards of the format 'rank:suit', separated by commas
    and slashes.
    The dictionary contains player_id:List items, where ids start from 0 and follow the number of hands
    found in the input string.
    White spaces are automatically ignored.
    Players must be given in cardinal order: N, E, S, W
    Example: A:c,2:d,3:h/2:s,3:c,A:s, which will find players 0 and 1
    """
    result = {}
    for idx, hand_str in enumerate(s.split('/')):
        result[idx] = import_single_hand(hand_str)

    return result


def gen_hand_description(pid, hand) -> str:
        s = ""
        s += f"Player {pid} ({PID_TO_CARDINAL[pid]}), hand: "
        for c in hand:
            s += str(c) + ", "
        s += "count: " + str(len(hand))
        return s


def gen_short_hand_desc(hand: List[Card]) -> str:
    return ','.join(card.short_string() for card in hand)


def gen_card_distribution_str(distribution):
    sorted_dict = OrderedDict(sorted(distribution.items()))
    hands = []

    for cards in sorted_dict.values():
        hands.append(gen_short_hand_desc(cards))

    return '/'.join([hand for hand in hands])


# ======================================================================================================================


class Deck:
    """
    Create a deck with 4 suits, *ranks* cards for each
    """
    def __init__(self, ranks: int):
        assert ranks > 0, "must have at least one rank"
        self.ranks = ranks
        self.cards = []
        for r in range(1, ranks+1):
            for s in Suit:
                if s != Suit.notrump:
                    self.cards.append(Card(s, r))

    def __str__(self):
        s = ""
        i = 0
        for c in self.cards:
            s += str(c)
            if c is not self.cards[len(self.cards) - 1]:
                s += ", "
            i += 1
            if i % 12 == 0:
                s += "\n"
        return s


# ======================================================================================================================


class Team:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.members = []

    def add_member(self, player: PlayerId):
        # support up to 2 players per team
        assert len(self.members) <= 1
        self.members.append(player)

    def get_other_member(self, member_id: int) -> int:
        if len(self.members) == 2:
            return (sum(self.members)) - member_id
        else:
            return -1


class Bid:
    def __init__(self, value: int, trump: Optional[Suit]):
        self.value = value
        self.trump = trump

    def __str__(self):
        suit_str = "nt" if self.trump is None else self.trump.to_char()
        return str(self.value) + suit_str


def import_bid(_input: str):
    _len = len(_input)
    suit = import_suit_from_char(_input[_len - 1])
    val = int(_input[0:_len - 1])

    return Bid(val, suit)
