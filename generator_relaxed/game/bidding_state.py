from typing import Dict, List, Tuple

from misc.game_structures import Card, PlayerId, Team
from generator_relaxed.game.bidding_actions import *


class BidInfo:
    def __init__(self, cp: PlayerId, lb: Optional[BiddingAction], lbc: Optional[PlayerId], passes: int):
        assert cp >= 0
        assert passes >= 0
        if lb is not None:
            assert lbc is not None

        # player that needs to take action
        self.current_player_id = cp
        # last non-pass action played
        self.last_bid = lb
        # player that called the last bid
        self.last_bid_caller = lbc
        # passes after last action
        self.passes = passes

    def __str__(self):
        return "Current player: " + str(self.current_player_id + 1) + ", last bid: " + ("none" if self.last_bid is None else str(self.last_bid)) + " called by P"+str(self.last_bid_caller+1)+", passes after last bid: " + str(self.passes)


class BiddingState:
    def __init__(self, n_players: int, teams: Dict[int, Team], ranks: int, hands: Dict[PlayerId, List[Card]]):
        self.ranks = ranks
        self.teams = teams
        self.n_players = n_players
        self.hands = hands

        # actions is a vector of (player_id, action_performed)
        self.actions: List[Tuple[int, BiddingAction]] = []

        # bid info stack
        self.bid_info: List[BidInfo] = []
        self.bid_info.append(BidInfo(0, None, None, 0))

    def get_curr_bid_info(self) -> BidInfo:
        return self.bid_info[len(self.bid_info) - 1]

    def get_current_player_id(self):
        return self.get_curr_bid_info().current_player_id

    """
    Returns True if the game is over
    """
    def is_game_over(self) -> bool:
        # for testing purposes, the game stops at a specific depth
        #if len(self.actions) == 20:
        #    return True

        info = self.get_curr_bid_info()
        # if no bid yet and all players passed -> end no bid, game must restart
        # if a bid was made and all other players passed in a row -> end
        if info.last_bid is None:
            return info.passes == self.n_players
        else:
            return info.passes == self.n_players - 1

    def push_action(self, action_played: BiddingAction):
        # assert that the action is legal
        assert action_played in self.available_actions(), "bidding action illegal!"
        turn = self.get_curr_bid_info()
        self.actions.append( (turn.current_player_id, action_played) )

        last_bid = 0
        last_bid_caller = 0
        pass_counter = 0
        if action_played.type == ActionEnum.pass_action:
            # if a pass is called, increment the number of consecutive passes and don't update the last bid played
            last_bid = turn.last_bid
            last_bid_caller = turn.last_bid_caller
            pass_counter = turn.passes + 1
        else:
            # otherwise reset the counter to 0 and update the last bid to this action
            last_bid = action_played
            last_bid_caller = turn.current_player_id
        self.bid_info.append(BidInfo((turn.current_player_id + 1)%self.n_players, last_bid, last_bid_caller, pass_counter))

    def pop_action(self):
        if len(self.actions) == 0:
            return 0
        self.actions.pop()
        self.bid_info.pop()

    """
    Returns the list of actions that the current player can perform.
    """
    def available_actions(self) -> List[BiddingAction]:
        turn = self.get_curr_bid_info()
        last_bid = turn.last_bid
        action_list = []

        # can always pass. Pass bid value and trump of last bid if it exists
        action_list.append(BiddingAction(ActionEnum.pass_action, (None if last_bid is None else last_bid.bid_data)))

        #def isPlayerAnEnemyOf(p1, p2):
            # is p1 an enemy of p2?
            #if (p1 in self.teams[0].members and p2 in self.teams[1].members) or \
                    #(p1 in self.teams[1].members and p2 in self.teams[0].members):
                #return True
            #return False

        #if turn.last_bid is not None and isPlayerAnEnemyOf(turn.current_player_id, turn.last_bid_caller):
            # if the last non-pass call was a bid, i can double
            #if turn.last_bid.type == ActionEnum.bid_action:
                #action_list.append(BiddingAction(ActionEnum.double_action, turn.last_bid.bid_data))

            # if the last non-pass call was a double, i can redouble
            #if turn.last_bid.type == ActionEnum.double_action:
                #action_list.append(BiddingAction(ActionEnum.redouble_action, turn.last_bid.bid_data))

        # i can bid all values that are better than the current highest bid
        action_list += BiddingAction.higher_bids_list(last_bid, self.ranks)

        return action_list

    """
    Generates a compact string that associates the current player with the past actions,
    in chronological order (ie the first action printed is the first bid he played and so on).
    """
    def gen_infoset_name(self) -> str:
        pid = self.get_current_player_id()
        s = "P" + str(pid+1) + "-"

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
                s += "/P" + str(id+1) + ":" + str(action)
        return s


    """
    Debugging function, prints the whole array of actions
    """
    def print_actions(self):
        for (a,b) in self.actions:
            print("Player%d played %s" % (a+1, b), end=", ")
        print("")
