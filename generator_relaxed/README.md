# Bridge generator README

## General information

The generators work with 2, 3 or 4 players and with any number of ranks between 1 and 13 included. They also support any number of games, which is implicitely given by the number of games used to generate the hands (generate_hands function). The hands are generated randomly so don't exaggerate with their number (I tried up to 1500 with 3 ranks and, although a bit slow, it works fine).

The algorithms are really slow, so I suggest to use 4 players and 3 or 4 ranks for playing phase and 2 players and 2 ranks for bidding phase if you just want to run the programs and take a look at the logs.

## Standard output
The output of the generators should follow this format (the examples is a 3 player instance):
~~~~
# info
game 
number_players
card_ranks
number_seq_pl1 number_seq_pl2 number_seq_pl3
number_infoset_pl1 number_infoset_pl2 number_infoset_pl3
game_type 
payoff_min_pl1 payoff_max_pl1 payoff_min_pl2 payoff_max_pl2 payoff_min_pl3 payoff_max_pl3 
-----
# game specific info
...
-----
# treeplexes
=== Player 1
start_seq end_seq parent_seq
...
=== Player 2
...
=== Player 3
...
-----
# utility matrix 
seq1 seq2 seq3 u1 u2 u3 chance_factor
...
~~~~
where *game* is the game played (i.e., *Kuhn*, *Leduc*, *Bridge Card Playing* etc.), *game_type* is either *zero-sum*, *constant-sum*, *general-sum*, *payoff_min_pl1* and *payoff_max_pl1* are respectively the minimum and maximum payoff for Player 1.

The section *game specific info* contains (if needed) information specific to a particular kind of game (i.e., the winner of the bidding phase in a card-playing game instance).

## Playing phase

### How to use

All you need to do is to call the main_playing_phase function of bridge_playing_phase_gen.py. This function will output two different files: 
- in the logs/Playing folder you will find a logging file that's useful to read the infosets generated, the treeplexes and the payoffs; 
- in the output/Playing folder you will find an output file that can be easily parsed by a program to import the treeplexes and the payoffs. 

The output is more compact and way less understandable than the log, so you should only use it for import purposes.

The parameters received by the function are:
- the number of players
- the number of ranks of each suit (i.e. 3 ranks means 12 cards in total)
- the winning bid (pass a Bid object, which needs the bidding value and the trump)
- the bidding phase winner id (id that starts from 0, i.e. if player 2 wins pass 1)
- a list of hands for each game that you want to explore (use the generate_hands function of game/hand_gen.py)

The dummy player doesn't play and all of its actions are actually taken by the declearer.

The sorted infosets in the log describe all the infosets of a player. They show the following properties:
- ID of the infoset
- Name of the infoset: this is the string that's used to distinguish the infosets. If two nodes produce the same name, they belong to the same infoset. It contains all the observable information, i.e. the player's hand, the dummy's hand and the history of actions undertaken by every player. In the history, the cards played by the dummy's hand are still counted as actions performed by the declearer
- Parent sequence: the sequence of the same player that leads to the infoset. It shows the previous infoset traversed and the action taken at that infoset
- Actions: the actions available to the player at the infoset

The sequences show all the sequences found in the tree. They contain the last infoset traversed and the action taken in that infoset.

The treeplexes represent the tree in a compact way, where each infoset is associated with its parent sequence and with all the sequences that are found by extending it. The children sequences are ordered, therefore if you see start:4 and end:6, it includes sequences 4, 5 and 6 as extensions.

The payoffs show the chance to reach that terminal node (1/number of games analysed), the terminal sequences needed to reach that node and the payoffs associated with the two teams. The terminal sequences are ordered by player id. The dummy player sequence is shown as empty because he isn't playing.

## Bidding phase

### How to use

The bidding phase generator works similarly to the playing phase. Use the file bridge_bidding_phase_gen.

The log also works exactly like the playing phase. The only thing that changes in the infoset names is that there is no dummy hand, therefore you can only see the current player's hand and the history of bids.

Bids are represented by 3 characters:
- The type of bid: pass, bid, double and redouble
- The value of the bid
- The suit: clubs, diamonds, hearts, spades and no-trump
For instance, b1h means a bid of 1 of hearts, while p2n means a pass where the previous bid was 2 of no-trump.

Since the tree has a really high exponential complexity, you might want to uncomment the first 'if' of the is_game_over function in game/bidding_state.py. This simple statement allows to limit the depth of the tree so that you can run a 4 player game without having to wait a lot of time.

IMPORTANT: this generator is still incomplete, TODOs are the output file and the implementation of the payoffs.

## Notes

The playing phase generator has been tested extensively, but, due to the complexity of the output, it's hard to spot mistakes such as bad infoset generation or bad treeplex generation. If you happen to find any error while working on your projects, please report it to me (Stefano) or Andrea, so that we can work on a fix or at least help you out.
