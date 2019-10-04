## Counterfactual Regret Minimization

This folder contains the files necessary to run the Counterfactual Regret Minimization algorithm. All the *_test.py files can be run,
each one of them evaluates a different type of game but they all function the same way.

The main entry point of the package is main.py. The only needed parameter is the path to the input file, as if you were located outside 
of the cfr folder. The program will print the expected utilites of the two players.

### How to run

Using the terminal, go into the main directory (outside of /cfr/) and run 'python -m cfr.main path/file_name.txt'

Python 3.7 is required.
