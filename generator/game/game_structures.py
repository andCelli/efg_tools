from enum import IntEnum

from typing import List, Optional

class Suit(IntEnum):
    clubs = 0
    diamonds = 1
    hearts = 2
    spades = 3
    notrump = 4

    def to_char (self) -> str:
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


class Card:
    def __init__(self, suit: Suit, rank: int):
        assert rank > 0, "cannot create a card with non-positive rank"
        assert suit != Suit.notrump, "cannot create a card with no suit"
        self.rank = rank
        self.suit = suit

    """
    Returns 1 if this card rank is higher than the target
    0 if equal
    -1 if lower
    """
    def compare_rank(self, obj: int) -> int:
        def normalize_ace(a):
            return a+13 if a == 1 else a
        norm_self_rank = normalize_ace(self.rank)
        norm_obj = normalize_ace(obj)

        return 1 if norm_self_rank > norm_obj else (0 if norm_self_rank == norm_obj else -1)

    """
    Compare this card to another card.
    Returns 1 if this card rank is higher than the target, 0 if equal, -1 if lower.
    Leader is the currently leading suit (suit of the first played card),
    trump > leader > else
    """
    def compare_to(self, obj, leader: Suit, trump: Optional[Suit]) -> int:
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

    def extended_string (self) -> str:
        return str(self.rank) + " of " + str(self.suit.name)

    def short_string (self) -> str:
        return str(self.rank) + str(self.suit.to_char())

    def __str__(self):
        return self.short_string()

    def __lt__(self, other):
        return self.suit.value < other.suit.value or (self.rank < other.rank and self.suit.value == other.suit.value)

    def __eq__(self, other):
        return self.suit.value == other.suit.value and self.rank == other.rank

    # noinspection PyTypeChecker
    def __hash__(self):
        return self.rank + self.suit.value * 13


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
            if i%12 == 0:
                s += "\n"
        return s


PlayerId = int


def gen_hand_description(pid, hand) -> str:
        s = ""
        s += "Player {}, hand: ".format(pid)
        for c in hand:
            s += str(c) + ", "
        s += "count: " + str(len(hand))
        return s


def gen_short_hand_desc(pid, hand) -> str:
    s = "{}".format(pid+1)
    if len(hand) == 0:
        s += "/"
    else:
        for c in hand:
            s += "/" + c.short_string()
    return s


class Team:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.members = []

    def add_member(self, player: PlayerId):
        # support up to 2 players per team
        assert len(self.members) <= 1
        self.members.append(player)

    def get_other_member(self, member_id: int) -> int:
        if len(self.members) == 2 and member_id in self.members:
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

