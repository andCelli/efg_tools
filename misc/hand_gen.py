from typing import Dict, List
import random

from misc.game_structures import Card, Deck
from misc.game_structures import PlayerId, gen_short_hand_desc
import copy


def compare_hands(h1: Dict[PlayerId, List[Card]], h2: Dict[PlayerId, List[Card]]):
    """
    Returns true if two sets of hands are equal.
    Hands must be already sorted.
    """
    for p in h1.keys():
        if h1[p] != h2[p]:
            return False
    return True


def generate_hands(n_players, ranks, game_number=1):
    """
    Generate a game given the number of players and the number of cards per suit.
    Returns a dictionary of hands, cards are ordered by rank.
    The keys are the players ids (0, 1, 2, ...).
    """
    def generate_hands_mono(n_players, ranks) -> Dict[PlayerId, List[Card]]:
        assert (ranks*4)%n_players == 0, "ERROR: choose a rank number such that each player has the same amount of cards"

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


    hands_list = []

    for i in range(game_number):
        duplicate = True
        hands = 0
        while duplicate:
            duplicate = False
            hands = generate_hands_mono(n_players, ranks)
            for elem in hands_list:
                if compare_hands(elem, hands):
                    duplicate = True

        hands_list.append(hands)

    return hands_list


def _get_all_combinations_for_one_hand(cards, hand_size):
    result = []
    for i in range(2 ** len(cards)):
        bit_str = bin(i)[2:]
        if bit_str.count('1') == hand_size:
            l = []
            for idx, bit in enumerate(bit_str[::-1]):
                if bit == '1':
                    l.append(cards[idx])
            result.append(l)
    return result


def _gen_hand_combinations(remaining_cards, cards_to_extract):
    result = []
    draws = _get_all_combinations_for_one_hand(remaining_cards, cards_to_extract)
    for draw in draws:
        # create a new remaining_cards list without those cards
        new_remaining = copy.copy(remaining_cards)
        for card in draw:
            new_remaining.remove(card)
        if len(new_remaining) != 0:
            combos = _gen_hand_combinations(new_remaining, cards_to_extract)
            for combo in combos:
                res = [draw]
                for hand in combo:
                    res.append(hand)
                result.append(res)
        else:
            result.append([draw])
    return result


def generate_hands_fixed(n_players, ranks, declarer, fix_dummy=True, game_number=1):
    assert 1 < n_players < 5, "ERROR: invalid number of players, only 2, 3 and 4 players are supported"
    assert declarer < n_players, "ERROR: invalid declarer id"
    assert (ranks * 4) % n_players == 0, \
        "ERROR: choose a rank number such that each player has the same amount of cards"
    dummy = -1

    if fix_dummy:
        teams = [{0, 2}, {1, 3}]
        for team in teams:
            if declarer in team:
                team.remove(declarer)
                dummy = team.pop()

    # if dummy isn't playing ignore it and label it -1
    if dummy >= n_players:
        dummy = -1

    deck = set(Deck(ranks).cards)
    games = []

    cards_per_hand = int((ranks * 4) / n_players)

    declarer_hand = []

    # generate declarer's hand
    for i in range(cards_per_hand):
        card = random.sample(deck, 1)[0]
        declarer_hand.append(card)
        deck.remove(card)
    declarer_hand.sort()

    # sample dummy's hand
    dummy_hand = []
    if dummy != -1 and fix_dummy:
        for i in range(cards_per_hand):
            card = random.sample(deck, 1)[0]
            dummy_hand.append(card)
            deck.remove(card)
    dummy_hand.sort()

    other_players = set(range(n_players))
    other_players.remove(declarer)
    if dummy in other_players:
        other_players.remove(dummy)

    if len(other_players) < 2:
        print(f"games will be reduced to 1 because sampling will always give the same result "
              f"({len(other_players)} hands to sample)")
        game_number = 1

    # IF RANKS <= 3: there are few possible game to generate, so it's better to create all possible hand
    # assignments and sample some of them
    if ranks <= 3:
        combos = _gen_hand_combinations(list(deck), cards_per_hand)

        if game_number < len(combos):
            # sample games
            games_sampled = random.sample(combos, game_number)
            for combo in games_sampled:
                hands = {declarer: declarer_hand}
                if dummy != -1 and fix_dummy:
                    hands[dummy] = dummy_hand
                for idx, op in enumerate(other_players):
                    hands[op] = sorted(combo[idx])
                games.append(hands)
        else:
            if game_number > 1:
                print("WARNING: the number of games requested is greater than the possible number of games that can"
                      f" be generated, only {len(combos)} games will be generated")
            for combo in combos:
                hands = {declarer: declarer_hand}
                if dummy != -1 and fix_dummy:
                    hands[dummy] = dummy_hand
                for idx, op in enumerate(other_players):
                    hands[op] = sorted(combo[idx])
                games.append(hands)

    # IF RANKS > 3: we can sample hands and compare them with the other sampled hands, if a combination was already
    # extracted, try again
    else:
        for game_id in range(game_number):
            duplicate = True
            while duplicate:
                hands = {declarer: declarer_hand}
                if dummy != -1 and fix_dummy:
                    hands[dummy] = dummy_hand

                new_deck = copy.copy(deck)

                for pl in other_players:
                    hands[pl] = []
                    for i in range(cards_per_hand):
                        c = random.sample(new_deck, 1)[0]
                        hands[pl].append(c)
                        new_deck.remove(c)

                # Sorting cards
                for hand in hands.values():
                    hand.sort()

                duplicate = False
                for game in games:
                    if compare_hands(game, hands):
                        # dup
                        duplicate = True
                if len(games) == 0 or not duplicate:
                    games.append(hands)
                    duplicate = False

    return games


if __name__ == '__main__':
    games = generate_hands_fixed(4, 2, 0, fix_dummy=True, game_number=20)
    for idx, g in enumerate(games):
        print("Game "+str(idx))
        for pid, hand in g.items():
            print(pid, gen_short_hand_desc(hand))
