from typing import Dict, List
from game.game_structures import Card, PlayerId, Team, Bid


class TurnInfo:
    def __init__(self, first, current, cards, tricks_won: Dict[int, int]):
        self.first_player_id = first
        self.current_player_id = current
        self.cards = cards
        # map player ids with number of tricks won
        self.tricks_won = tricks_won

    def __str__(self):
        s = "First player of the turn: Player" + str(self.first_player_id+1) + ", current player: Player" + str(self.current_player_id + 1) + "\nCards played: "
        if len(self.cards) == 0:
            s += "none"
        else:
            for card in self.cards:
                s += card.short_string() + ", "
        return s


"""
GameState is the class that contains the core gameplay logic, such as turn order,
performable actions and actions history.

Players and relative hands are passed as parameter because they were necessary
already for the bidding part.
"""
class GameState:
    def __init__(self, n_players, teams: Dict[int, Team], hands: Dict[PlayerId, List[Card]], ranks: int, bid: Bid, bid_winner_id = 0):
        self.ranks = ranks
        # players is a map with player id as key
        self.teams = teams
        self.n_players = n_players
        self.bid = bid
        self.trump = bid.trump
        self.hands = hands

        # Sorting hands to avoid errors during exploration
        for hand in hands.values():
            hand.sort()

        self.turn_info = []
        tricks_won = {}
        for p in range(self.n_players):
            tricks_won[p] = 0
        self.turn_info.append(TurnInfo(bid_winner_id, bid_winner_id, [], tricks_won))

        # actions is a vector of (player_id, action_performed)
        self.actions = []

        self.declarer_id = bid_winner_id
        self.dummy_id = -1
        self.dummy_exists = False
        for team in teams.values():
            if self.declarer_id in team.members and len(team.members) == 2: # teams can only have 1 or 2 players
                # declarer has a partner
                self.dummy_id = team.get_other_member(self.declarer_id)
                self.dummy_exists = True

    def get_curr_turn_info(self) -> TurnInfo:
        return self.turn_info[len(self.turn_info) - 1]

    def get_current_player_id(self):
        return self.get_curr_turn_info().current_player_id

    """
    Returns True if the game is over, namely if there are no cards left in the
    players' hands
    """
    def is_game_over(self) -> bool:
        game_over = True
        for p in range(self.n_players):
            game_over = game_over and (len(self.hands[p]) == 0)
        return game_over

    def push_action(self, card_played: Card):
        # assert that the card is legal
        assert card_played in self.available_actions()
        turn = self.get_curr_turn_info()
        self.actions.append( (turn.current_player_id, card_played) )

        self.hands[turn.current_player_id].remove(card_played)

        next_player = (turn.current_player_id+1)%self.n_players
        # cards = updated cards-on-table vector
        cards = turn.cards.copy()
        cards.append(card_played)

        if next_player == turn.first_player_id:
            # turn ended
            winner_id = self._find_winner_id(cards, turn.first_player_id)
            new_tricks_won = turn.tricks_won.copy()
            new_tricks_won[winner_id] += 1
            # pushing a new turn info object on the stack
            self.turn_info.append(TurnInfo(winner_id, winner_id, [], new_tricks_won))
        else:
            self.turn_info.append(TurnInfo(turn.first_player_id, next_player, cards, turn.tricks_won.copy()))

    def pop_action(self):
        if len(self.actions) == 0:
            return 0
        (popped_player_id, popped_card) = self.actions.pop()
        prev_turn_info = self.turn_info.pop()
        hand = self.hands[popped_player_id]
        hand.append(popped_card)
        hand.sort()

    def _find_winner_id(self, cards: List[Card], first_player_id: int) -> int:
        assert len(cards) == self.n_players, "the turn hasn't ended yet"

        leader_suit = cards[0].suit
        best_card_index = 0
        for i in range(1, len(cards)):
            if cards[i].compare_to(cards[best_card_index], leader_suit, self.trump) == 1:
                best_card_index = i

        return (first_player_id + best_card_index) % self.n_players

    """
    Returns the list of cards that the current player can play.
    If he's the leader, any card can be played. Same if he doesn't have any card that can 
    follow the leading suit.
    If he has some cards that follow the leader, he must play one of those.
    """
    def available_actions(self) -> List[Card]:
        turn = self.get_curr_turn_info()
        leader_suit = turn.cards[0].suit if len(turn.cards) != 0 else None
        if leader_suit is None:
            return self.hands[turn.current_player_id]
        else:
            # cards that have the same suit as the leader
            following_cards = list(filter(lambda c: c.suit == leader_suit, self.hands[turn.current_player_id]))
            if len(following_cards) == 0:
                # no cards can follow, so play any card
                return self.hands[turn.current_player_id]
            else:
                # must follow the leading suit
                return following_cards

    """
    Generates a compact string that associates the current player with his hand and the past actions,
    in chronological order (ie the first card printed is the first card he played and so on).
    """
    def gen_infoset_name(self) -> str:
        s = ""
        if not self.dummy_exists:
            pid = self.get_current_player_id()

            s += "P" + str(pid+1) + "-"
            if len(self.hands[pid]) == 0:
                s += "/"
            else:
                for c in self.hands[pid]:
                    s += "/" + c.short_string()

            s += "-"
            if len(self.actions) == 0:
                s += "/"
            else:
                for (id, action) in self.actions:
                    # print the action
                    s += "/P" + str(id+1) + ":" + action.short_string()
        else:
            pid = self.get_current_player_id()

            dummy_hand = self.hands[self.dummy_id]

            if pid == self.dummy_id:
                pid = self.declarer_id

            s += "P" + str(pid+1) + "-"
            if len(self.hands[pid]) == 0:
                s += "/"
            else:
                for c in self.hands[pid]:
                    s += "/" + c.short_string()

            s += "-"
            if len(dummy_hand) == 0:
                s += "/"
            else:
                for c in dummy_hand:
                    s += "/" + c.short_string()

            s += "-"
            if len(self.actions) == 0:
                s += "/"
            else:
                for (id, action) in self.actions:
                    # print the action
                    s += "/P" + str(self.fix_id(id) + 1) + ":" + action.short_string()

        return s

    """
    Change the dummy id into the declearer one, if necessary
    """
    def fix_id(self, pid: int) -> int:
        if self.dummy_exists and pid == self.dummy_id:
            return self.declarer_id
        return pid

    """
    Debugging function, prints the whole array of actions
    """
    def print_actions(self):
        for (a,b) in self.actions:
            print("Player%d played %s" % (a+1, b), end=", ")
        print("")
