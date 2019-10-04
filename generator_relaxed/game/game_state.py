from typing import Dict
from misc.game_structures import *


class TurnInfo:
    def __init__(self, first, current, cards, tricks_won: Dict[int, int]):
        self.first_player_id = first
        self.current_player_id = current
        self.cards = cards
        # map player ids with number of tricks won
        self.tricks_won = tricks_won

    def __str__(self):
        s = f"First player of the turn: {PID_TO_CARDINAL[self.first_player_id]}, current player: {PID_TO_CARDINAL[self.current_player_id]}\nCards played: "
        if len(self.cards) == 0:
            s += "none"
        else:
            for card in self.cards:
                s += card.short_string() + ", "
        return s


class Hand:
    """ Class used to generate clusters of cards. Clusters contain cards of consecutive ranks, same suit. """
    def __init__(self, cards: List[Card], pid):

        self.player = PID_TO_CARDINAL[pid]

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

        print(self.get_clusters_str())

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
        cluster.sort(reverse=True)

    def __len__(self):
        # print(f"len = {self._remaining}")
        return self._remaining

    def get_hand_str(self):
        """ Return a string describing all cards """
        hand = []
        for cluster_list in self._suits.values():
            for cluster in cluster_list:
                hand += cluster
        return gen_short_hand_desc(hand)

    def get_clusters_str(self):
        """ Return a string describing all clusters """
        s = f"Clusters of {self.player}:\n\t"
        all_clusters = []
        for cluster_list in self._suits.values():
            all_clusters += cluster_list
        s += ' - '.join([gen_short_hand_desc(cluster) for cluster in all_clusters])
        return s

    def __str__(self):
        return self.get_hand_str()


class GameState:
    """
    GameState is the class that contains the core gameplay logic, such as turn order,
    performable actions and actions history.

    Players and relative hands are passed as parameter because they were necessary
    already for the bidding part.
    """
    def __init__(self, n_players, teams: Dict[int, Team], hands: Dict[PlayerId, List[Card]], ranks: int, bid: Bid, bid_winner_id=0):
        self.ranks = ranks
        # players is a map with player id as key
        self.teams = teams
        self.n_players = n_players
        self.bid = bid
        self.trump = bid.trump
        self.hands = {}

        # Sorting hands to avoid errors during exploration
        for hand in hands.values():
            hand.sort(reverse=True)

        for player, hand in hands.items():
            self.hands[player] = Hand(hand, player)

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
            # teams can only have 1 or 2 players
            if self.declarer_id in team.members:
                if len(team.members) == 2:
                    # declarer has a partner
                    self.dummy_id = team.get_other_member(self.declarer_id)
                    self.dummy_exists = True
            else:
                self.defender_team = team

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
        assert card_played in self.available_actions()
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

    def gen_infoset_name(self) -> str:
        """
        Infosets are identified by every bit of information that the player knows.
        Generates a compact string that associates the current player with his hand and the past actions,
        in chronological order (ie the first card printed is the first card he played and so on).
        """
        s = ""

        pid = self.get_current_player_id()

        defenders = self.defender_team.members
        first_defender = defenders[0]
        second_defender = defenders[1] if len(defenders) == 2 else -1

        # if there are 3 or 4 players, the defenders can see each other's cards - we treat them as a single player,
        # because it's like having two players that coordinate their actions

        # dummy actions are actually made by the declarer
        if pid == self.dummy_id:
            pid = self.declarer_id

        # only one defender "plays"
        if pid == second_defender:
            pid = first_defender

        s += f"{PID_TO_CARDINAL[pid]}-"
        # append current player's hand
        if len(self.hands[pid]) == 0:
            s += "/"
        else:
            s += self.hands[pid].get_hand_str()

        # if there are 2 defenders and pid is first_defender, append second_defender's hand
        if second_defender != -1 and pid == first_defender:
            s += "-"
            if len(self.hands[second_defender]) == 0:
                s += "/"
            else:
                s += self.hands[second_defender].get_hand_str()

        if self.dummy_exists:
            dummy_hand = self.hands[self.dummy_id]
            s += "-"
            # append dummy hand
            if len(dummy_hand) == 0:
                s += "/"
            else:
                s += dummy_hand.get_hand_str()

        s += "-"
        # append game history
        if len(self.actions) == 0:
            s += "/"
        else:
            for (_id, action) in self.actions:
                # print the action
                s += f"/{PID_TO_CARDINAL[_id]}" + action.short_string()

        return s

    def fix_id(self, pid: int) -> int:
        """
        Change the dummy id into the declearer one, if necessary.
        Change the second defending member into the first one, if necessary.
        """
        if self.dummy_exists and pid == self.dummy_id:
            return self.declarer_id
        defenders = self.defender_team.members
        if len(defenders) == 2 and pid == defenders[1]:
            return defenders[0]
        return pid

    def print_actions(self):
        """
        Debugging function, prints the whole array of actions
        """
        for (a,b) in self.actions:
            print("Player%d played %s" % (a+1, b), end=", ")
        print("")
