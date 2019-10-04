from typing import Dict, List
from misc.game_structures import Card, PlayerId, Suit


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


class Hand:
    """ Class used to generate clusters of cards. Clusters contain cards of consecutive ranks, same suit. """
    def __init__(self, cards: List[Card]):

        self.ranks = len(cards)

        # Dict of [suit, List[List[Card]], gives clusters for each suit in player's hand
        self._suits = {}

        # for each card, shows the corresponding cluster
        self.card_to_cluster_dict: Dict[Card, List] = {}

        self._remaining = len(cards)

        for card in cards:
            # init clusters per suit
            if card.suit in self._suits.keys():
                cluster_list = self._suits[card.suit]
            else:
                cluster_list = self._suits[card.suit] = []
            # retrieve all cards of the suit already clustered
            analysed_cards = []
            for cluster in cluster_list:
                analysed_cards += cluster
            found = False
            for c in analysed_cards:
                if Card.are_consecutive(card, c, self.ranks):
                    # need to cluster card in the same cluster as c
                    cl = self.card_to_cluster_dict[c]
                    cl.append(card)
                    self.card_to_cluster_dict[card] = cl
                    found = True
                    break
            if not found:
                # cluster not found, need to create a new one
                cl = [card]
                cluster_list.append(cl)
                self.card_to_cluster_dict[card] = cl

        #for suit in self._suits.values():
        #    for cluster in suit:
        #        print(f"\tcluster: {[card.short_string() for card in cluster]}")

    def can_follow(self, suit):
        result = []
        if suit in self._suits:
            # Return a list of lowest cards of each consecutive cards cluster
            for cluster in self._suits[suit]:
                if len(cluster) > 0:
                    result.append(cluster[0])
        return result

    def get_available_actions(self, lead):
        if lead is not None:
            actions = self.can_follow(lead)
            if len(actions) > 0:
                return actions
        # Either the player is first to play or cannot follow, return all the lowest cards he can play
        actions = []
        for clusters_per_suit in self._suits.values():
            for cluster in clusters_per_suit:
                # Pick only the lowest card
                if len(cluster) > 0:
                    actions.append(cluster[0])
        return actions

    def remove_played(self, card):
        self._remaining -= 1
        cluster = self.card_to_cluster_dict[card]
        cluster.remove(card)

    def undo(self, card):
        self._remaining += 1
        cluster = self.card_to_cluster_dict[card]
        cluster.append(card)

    def __len__(self):
        # print(f"len = {self._remaining}")
        return self._remaining


class GameState:
    """
    GameState is the class that contains the core gameplay logic, such as turn order,
    performable actions and actions history.

    Players and relative hands are passed as parameter because they were necessary
    already for the bidding part.
    """

    def __init__(self, n_players, hands: Dict[PlayerId, List[Card]], ranks: int, trump: Suit, bid_winner_id=0, declarer_partner_id=-1, reverse=True):
        self.ranks = ranks
        self.n_players = n_players
        self.trump = trump
        self.hands = {}

        # Sorting hands to avoid errors during exploration
        for hand in hands.values():
            if reverse:
                hand.sort(reverse=True)
            else:
                hand.sort()

        for player, hand in hands.items():
            # print("Player clusters")
            self.hands[player] = Hand(hand)

        self.turn_info = []
        tricks_won = {}
        for p in range(self.n_players):
            tricks_won[p] = 0
        self.turn_info.append(TurnInfo(bid_winner_id, bid_winner_id, [], tricks_won))

        # actions is a vector of (player_id, action_performed)
        self.actions = []

        self.declarer_id = bid_winner_id
        self.declarer_partner_id = declarer_partner_id

    def get_curr_turn_info(self) -> TurnInfo:
        return self.turn_info[len(self.turn_info) - 1]

    def get_current_player_id(self):
        return self.get_curr_turn_info().current_player_id

    def is_game_over(self) -> bool:
        """
        Returns True if the game is over, namely if there are no cards left in the
        players' hands
        """
        game_over = True
        for p in range(self.n_players):
            game_over = game_over and (len(self.hands[p]) == 0)
        return game_over


    def push_action(self, card_played: Card):
        # assert that the card is legal
        # assert card_played in self.available_actions()
        turn = self.get_curr_turn_info()
        self.actions.append( (turn.current_player_id, card_played) )

        self.hands[turn.current_player_id].remove_played(card_played)

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
        self.turn_info.pop()
        hand = self.hands[popped_player_id]
        hand.undo(popped_card)

    def _find_winner_id(self, cards: List[Card], first_player_id: int) -> int:
        assert len(cards) == self.n_players, "the turn hasn't ended yet"

        leader_suit = cards[0].suit
        best_card_index = 0
        for i in range(1, len(cards)):
            if cards[i].compare_to(cards[best_card_index], leader_suit, self.trump) == 1:
                best_card_index = i

        return (first_player_id + best_card_index) % self.n_players

    def available_actions(self) -> List[Card]:
        """
        Returns the list of cards that the current player can play.
        If he's the leader, any card can be played. Same if he doesn't have any card that can
        follow the leading suit.
        If he has some cards that follow the leader, he must play one of those.
        """
        turn = self.get_curr_turn_info()
        leader_suit = turn.cards[0].suit if len(turn.cards) != 0 else None

        result = self.hands[turn.current_player_id].get_available_actions(leader_suit).copy()
        return result

    def get_declarer_tricks(self):
        """
        Return the number of tricks won by the declarer team
        """
        # sum the declarer's tricks and his partner's
        turn = self.get_curr_turn_info()
        res = turn.tricks_won[self.declarer_id]
        if self.declarer_partner_id != -1:
            res += turn.tricks_won[self.declarer_partner_id]
        return res

    def is_max(self):
        """
        Return if it's the turn of the declaring team (max player for ab-search)
        -> next action (push) will be made by max team
        """
        turn = self.get_curr_turn_info()
        return turn.current_player_id == self.declarer_partner_id or turn.current_player_id == self.declarer_id

    def print_actions(self):
        """
        Debugging function, prints the whole array of actions
        """
        for (a,b) in self.actions:
            print("Player%d played %s" % (a+1, b), end=", ")
        print("")

    def str_actions(self) -> str:
        """
        Create a string with the sequence of cards played during the game
        :return: string with all actions played this game
        """
        s = ""
        for (a,b) in self.actions:
            s += f"Player{a+1} played {b}, "
        return s
