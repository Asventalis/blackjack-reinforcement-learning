# Blackjack Reinforcement Learning

Two experiments on learning to play blackjack. `21_point.ipynb` models a simplified game (player sum 4-20, actions HIT/STICK, no dealer, reward proportional to the final sum) as a tabular MDP and learns Q-values with epsilon-greedy Q-learning (fixed and 1/N learning rates) and first-visit Monte Carlo control, printing the learned policy. `blackjack.py` / `blackjack.ipynb` is a fuller environment with hashable `Hand` and `BlackjackState` classes supporting hit, stand, double down and split, soft/hard totals and a dealer that plays to 17, with payouts as rewards, meant as the state representation for a future agent.

## How to run
Python 3 with `numpy` and `matplotlib`. Open the notebooks in Jupyter; `python blackjack.py` starts an interactive text game where you type the action for each hand.

## Notes
- The simplified state (sum only) cannot distinguish "sum 19, can still hit" from "sum 19, already stuck", which the notebook notes as the reason the Q-learning variant misbehaves; the full environment fixes this but has no learning loop yet.
- The 21-point environment skeleton follows the structure of the Lazy Programmer RL course examples.
