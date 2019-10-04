## Relaxed Bridge Generrator

This package generates a game of Bridge with the assumption that the defenders can see each others' cards, therefore changing the game to
a 2-player game. 

The entry points are bridge_playing_phase_relaxed_gen.py, test_generator.py and test_generator_fixed.py.
The first file simply generates a game and outputs it in the logs and output folders. The other two files are used to generate a block of
games (e.g. card ranks from 2 to 4, 20 games for each rank) and save them in the test_files and test_files_fixed folders. Fixed means that each game samples a series of card distributions (instead of only one), where the declarer's cards (and, if desired, the dummy cards) are the same in each sample. In other words, it's like knowing only the hand of the declarer and wanting to create a structure that considers the uncertainty of the opponents' hands by sampling some of them.

For more details on the generator, check out the generator folder.

### How to run

Open a terminal and go to the project folder (outside of /generator_relaxed/) and run 'python -m generator_relaxed.bridge_playing_phase_relaxced_gen' (or any of the other two entry points). The program will print out the parameters required to run.

Python 3.7 is required.
