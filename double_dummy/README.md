## Double Dummy Analysis

This package performs DDA of a given Bridge game. DDA returns the number of tricks that each team gets when all the players play
optimally. All the algorithms are located in algorithm.py, but the entry points of the package are dda_simple.py and dda_extended.py.

dda_simple is used when the contract is known and returns the number of tricks taken by the declarer given such contract.
dda_extended instead performs the analysis for each possible trump-declarer combination (therefore also takes longer to run).

### How to run

Open a terminal and go to the project folder (outside of /double_dummy/) and run 'python -m double_dummy.dda_simple' or 
'python -m double_dummy.dda_extended'. The program will print out the parameters required to run.

Python 3.7 is required.
