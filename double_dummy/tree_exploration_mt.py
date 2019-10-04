"""
In this file we define the alpha-beta pruning exploration algorithm. The goal is to find the number of tricks that
the starting team can make given the initial game state.
"""

from double_dummy.game.game_state_old import GameState
import threading
import copy

alpha = -20
beta = 20
lock = threading.Lock()


def _ab_search(game: GameState) -> int:
    """
    Alpha-Beta multithread search.
    The reward is limited to the interval [0,13], because Bridge has always 13 hands to play. We can therefore set alpha
    and beta to +-20 (or any interval that strictly contains 0,13).
    """

    global alpha, beta

    # if the game is over (leaf node), return the number of tricks won by Max
    if game.is_game_over():
        # debug print
        print(f"Leaf node reached: actions = {game.str_actions()}\n\tvalue = {game.get_declarer_tricks()}, alpha = {alpha}, beta = {beta}")
        return game.get_declarer_tricks()

    # turn of a Max team
    if game.is_max():
        max_eval = -20
        actions = game.available_actions()
        # TODO: prune actions here
        for action in actions:
            game.push_action(action)
            curr_eval = _ab_search(game)
            game.pop_action()
            max_eval = max(max_eval, curr_eval)
            lock.acquire()
            alpha = max(alpha, curr_eval)
            # pruning
            if beta <= alpha:
                lock.release()
                print("pruning")
                break
            lock.release()
        return max_eval
    # turn of Min team
    else:
        min_eval = 20
        actions = game.available_actions()
        # TODO: prune actions here
        for action in actions:
            game.push_action(action)
            curr_eval = _ab_search(game)
            game.pop_action()
            min_eval = min(min_eval, curr_eval)
            lock.acquire()
            beta = min(beta, curr_eval)
            # pruning
            if beta <= alpha:
                lock.release()
                break
            lock.release()
        return min_eval


class ABSearchThread(threading.Thread):
    def __init__(self, game):
        threading.Thread.__init__(self)
        self.result = 0
        self.game = game

    def run(self):
        self.result = _ab_search(self.game)

    def join(self, *args) -> int:
        threading.Thread.join(self, *args)
        return self.result


def multi_thread_ab_search(game: GameState) -> int:
    """
    Call the alpha beta pruning search creating one thread per child of the first node
    """
    results = []
    threads = []

    # the first player is the declarer, therefore a Max player
    actions = game.available_actions()
    for i in range(len(actions)):
        game_copy = copy.deepcopy(game)
        game_copy.push_action(actions[i])
        results.append(0)
        threads.append(ABSearchThread(game_copy))
        threads[i].start()
        game.pop_action()

    for i in range(len(actions)):
        results[i] = threads[i].join()

    return max(results)
