from enum import Enum
import math

from typing import List, Optional, Tuple

from misc.game_structures import Suit


class ActionEnum(Enum):
    bid_action = 0
    double_action = 1
    redouble_action = 2
    pass_action = 3

    def to_char (self) -> str:
        if self == ActionEnum.bid_action:
            return 'b'
        if self == ActionEnum.double_action:
            return 'd'
        if self == ActionEnum.redouble_action:
            return 'r'
        if self == ActionEnum.pass_action:
            return 'p'


class BiddingAction:
    def __init__(self, type: ActionEnum, bid_data: Optional[Tuple[int, Suit]]):
        if type != ActionEnum.pass_action:
            assert bid_data is not None
            (value, trump) = bid_data
            assert value > 0
            assert trump is not None
        else:
            if bid_data is not None:
                (value, trump) = bid_data
                assert value > 0
                assert trump is not None

        self.type = type
        self.bid_data = bid_data

    def __str__(self):
        s = self.type.to_char()
        if self.bid_data is not None:
            (value, trump) = self.bid_data
            s += str(value) + trump.to_char()
        return s

    def __eq__(self, other):
        return self.type == other.type and \
            self.bid_data == other.bid_data

    def __hash__(self):
        return hash((self.type, self.bid_data))

    """
    Returns a list of bids higher than self.
    Should pass the last_bid attribute of BidInfo
    """
    @staticmethod
    def higher_bids_list(bid, ranks: int) -> List:
        if bid is not None:
            assert bid.type != ActionEnum.pass_action, "can't evaluate higher bids of a pass"

        ret_list = []
        value_limit = math.ceil(ranks / 2)

        if bid is not None:
            (value, trump) = bid.bid_data
            for suit in Suit:
                if int(suit) > int(trump):
                    # same value, higher trump
                    ret_list.append(BiddingAction(ActionEnum.bid_action, (value, suit)))
                # higher value, any trump
                for v in range(value + 1, value_limit + 1):
                    ret_list.append(BiddingAction(ActionEnum.bid_action, (v, suit)))
        else:
            # Return all possible biddings (used for first bid of the game)
            for suit in Suit:
                for v in range(1, value_limit + 1):
                    ret_list.append(BiddingAction(ActionEnum.bid_action, (v, suit)))
        return ret_list
