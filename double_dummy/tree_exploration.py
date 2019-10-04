"""
In this file we define the alpha-beta pruning exploration algorithm. The goal is to find the number of tricks that
the starting team can make given the initial game state.
"""

from double_dummy.game.game_state_old import GameState


def ab_search(game: GameState, alpha = -20, beta = 20) -> int:
    """
    Alpha-Beta search.
    The reward is limited to the interval [0,13], because Bridge has always 13 hands to play. We can therefore set alpha
    and beta to +-20 (or any interval that strictly contains 0,13).
    """

    # if the game is over (leaf node), return the number of tricks won by Max
    if game.is_game_over():
        # debug print
        # print(f"Leaf node reached: actions = {game.str_actions()}\n\tvalue = {game.get_declarer_tricks()}, alpha = {alpha}, beta = {beta}")
        return game.get_declarer_tricks()

    # turn of a Max team
    if game.is_max():
        max_eval = -20
        actions = game.available_actions()
        # TODO: prune actions here
        for action in actions:
            game.push_action(action)
            curr_eval = ab_search(game, alpha, beta)
            game.pop_action()
            max_eval = max(max_eval, curr_eval)
            alpha = max(alpha, curr_eval)
            # pruning
            if beta <= alpha:
                break
        return max_eval
    # turn of Min team
    else:
        min_eval = 20
        actions = game.available_actions()
        # TODO: prune actions here
        for action in actions:
            game.push_action(action)
            curr_eval = ab_search(game, alpha, beta)
            game.pop_action()
            min_eval = min(min_eval, curr_eval)
            beta = min(beta, curr_eval)
            # pruning
            if beta <= alpha:
                break
        return min_eval
