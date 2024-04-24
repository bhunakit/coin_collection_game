# Coin Collection Game with Expectimax

## Overview

The Coin Collection Game is an automated 2-player strategy game where two AI agents compete on an 8x8 board. Players aim to collect coins that can randomly change between being solid (collectible) and transparent (non-collectible), using the Expectimax algorithm to make decisions under uncertainty.

## Game Rules

- **Board Setup**: An 8x8 grid filled with coins at random. Each coin has a 67% chance of being placed initially, and can either be solid or transparent.
- **Players**: Two players start at opposite corners of the board. Player A starts at (0, 0) and Player B starts at (7, 7).
- **Turns**: Players take turns moving one cell in any of the four cardinal directions (up, down, left, right).
- **Coin Collection**: On landing on a cell with a solid coin, a player collects the coin, increasing their score by 1 plus any applicable bonuses for consecutive collections. The coin then disappears from the board.
- **Coin State Transition**: At the end of each turn, each coin on the board has a 50% chance to switch from being solid to transparent, and vice versa.
- **Consecutive Collections**: If a player collects coins on consecutive turns, they receive bonus points. The bonus for consecutive collections is calculated as the square of the length of the streak. Added to score would be the squared length of the streak minus the square of the streak length minus one.
- **Ending the Game**: The game ends when there are no more solid coins left on the board. The player with the highest score wins.

## Features

- **Dynamic Game Board**: The board is initialized filled by 67% with coins which can either be solid or transparent.
- **Expectimax AI**: Implements the Expectimax algorithm for strategic decision-making in a stochastic game environment. The goal here is to maximize the expected utility.
- **Consecutive Coin Bonuses**: Players earn points by collecting coins, with bonuses for consecutive collections calculated as the square of the streak length.

## Prerequisites

- Python 3.6 or higher.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone [your-repository-link]
cd [repository-name]
```

## Running the Code

### Demo Mode

python game.py --demo

This will initiate a game session and automatically manage both players' moves, showing how the AI makes decisions under a stochastic environment.

### Evaluate Expectimax

python game.py --run

This mode will typically run multiple simulations and provide statistical feedback on the performance of the expectimax algorithm compared to random decision-making.

### Optimize Parameters

python game.py --optimize

This will run algorithms designed to tune the expectimax heuristic parameters for optimal performance.

### Help

python game.py --help

For help with the commands
