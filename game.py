import random
import argparse
from copy import deepcopy

class Game:
    def __init__(self):
        self.board = [[random.choice([1, 2]) if random.random() < 0.67 else 0 for _ in range(8)] for _ in range(8)] # Starting the 8x8 board filled to 67%
        self.player_positions = [(0, 0), (7, 7)]
        self.board[0][0], self.board[7][7] = 0, 0  # Ensure starting positions don't have coins
        self.scores = [0, 0]
        self.streak = [0, 0] # Consecutive coins
        self.current_player = 0
        self.update_coin_count() # Update the amount of coin left
        self.directions = ['up', 'down', 'left', 'right']

    def update_coin_count(self):
        self.coin_left = sum(sum(row) for row in self.board)

    def update_coin_state(self):
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == 2:
                    if random.random() < 0.5:
                        self.board[r][c] = 1  # Becomes a solid coin
                elif self.board[r][c] == 1:
                    if random.random() < 0.5:
                        self.board[r][c] = 2  # Becomes transparent

    def print_board(self):
        print("   " + "   ".join([str(i) for i in range(8)]))
        print(" +" + "---+"*8)  # Print a top border

        for r in range(8):
            row = f"{r}| "
            for c in range(8):
                if (r, c) == self.player_positions[0]:
                    cell = 'A'
                elif (r, c) == self.player_positions[1]:
                    cell = 'B'
                elif self.board[r][c] == 1:
                    cell = 'o'  # Solid coin
                elif self.board[r][c] == 2:
                    cell = '*'  # Transparent coin
                else:
                    cell = ' '

                row += f" {cell} |"
            print(row)
            print(" +" + "---+"*8)

        print(f"Scores: Player A = {self.scores[0]}, Player B = {self.scores[1]}")

    def move(self, direction):
        if direction not in self.directions:
            return False
        r, c = deepcopy(self.player_positions[self.current_player])
        move_mapping = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        dr, dc = move_mapping[direction]
        r, c = r + dr, c + dc

        # If the updated coordinate crashes with the other player or goes out of bound --> End turn (return Fasle)
        if (r, c) == self.player_positions[1 - self.current_player] or not (0 <= r < 8 and 0 <= c < 8):
            self.current_player = 1 - self.current_player
            self.streak[self.current_player] = 0
            return False

        # Set new position
        self.player_positions[self.current_player] = (r, c)

        # Scoring logic
        if self.board[r][c] == 1:
            self.streak[self.current_player] += 1
            # If the player is on streak (consecutive) change the streaked scores to streaks squared, e.g. if current streak if 3 then add 3**2 - 2**2 = 5 to the current score
            new_score = (self.streak[self.current_player] ** 2) - ((self.streak[self.current_player] - 1) ** 2)
            self.scores[self.current_player] += new_score
            self.board[r][c] = 0
            self.update_coin_count()
        elif self.board[r][c] == 0 or self.board[r][c] == 2:
            # Reset streak
            self.streak[self.current_player] = 0

        # Update coin left and end turn
        self.current_player = 1 - self.current_player
        self.update_coin_state()

        return True

    def evaluate_game_state(self, w1, w2):
        # Score of the player at that position
        score = self.scores[self.current_player]

        # Accessible coins in proximity for getting consecutive coin bonus
        player_pos = self.player_positions[self.current_player]
        accessible_coins = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = player_pos[0] + dr, player_pos[1] + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    # If coin is currently solid then add 1
                    if self.board[r][c] == 1:
                        accessible_coins += 1
                    # If coin is transparent, 50% chance of becoming solid, add 0.5
                    elif self.board[r][c] == 2:
                        accessible_coins += 0.5

        # Return weighted score of each heuristics
        return w1 * score + w2 * accessible_coins

    # Expectimax: decision making algorithm in a stochastic environment where each decision is based on the expected outcome rather than guaranteed outcome (minimax)
    def expectimax(self, depth, alpha, beta, node_type, w1, w2):
        # When depth limit is reached or there is no coin left, evaluate the heuristic (game state) at the state
        if depth == 0 or self.coin_left == 0:
            return self.evaluate_game_state(w1, w2)

        # "Max Nodes": choose the child node the have the highest expected utility (highest average heuristics)
        if node_type == 'max':
            max_eval = float('-inf')
            for move in self.directions:
                game_copy = deepcopy(self)
                if game_copy.move(move):
                    eval = game_copy.expectimax(depth - 1, alpha, beta, 'chance', w1, w2)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval

        # "Chance Nodes": return the average value (expected utility) of all child nodes
        elif node_type == 'chance':
            avg_eval = 0
            count = 0
            # Simulate the randomness of the coin state changes
            for move in self.directions:
                game_copy = deepcopy(self)
                # Simulate both scenarios where a coin is solid (1) or transparent (2)
                for state in [1, 2]:
                    game_copy.update_coin_state()
                    if game_copy.move(move):
                        eval = game_copy.expectimax(depth - 1, alpha, beta, 'max', w1, w2)
                        avg_eval += eval
                        count += 1
            avg_eval = avg_eval / count if count != 0 else 0
            return avg_eval

        return 0

    # Get the direction to immediate adjacent coin for optimality
    def move_towards_single_adjacent_coin(self):
        player_pos = self.player_positions[self.current_player]
        directions = {
            'up': (player_pos[0] - 1, player_pos[1]),
            'down': (player_pos[0] + 1, player_pos[1]),
            'left': (player_pos[0], player_pos[1] - 1),
            'right': (player_pos[0], player_pos[1] + 1)
        }

        available_coins = []

        for direction, pos in directions.items():
            r, c = pos
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == 1:
                available_coins.append(direction)

        # Return the only direction that has a coin
        if len(available_coins) == 1:
            return available_coins[0]

        return None

    def best_move(self, depth, w1, w2):
        # If there is a coin next to the player, just move there
        single_coin_direction = self.move_towards_single_adjacent_coin()
        if single_coin_direction:
            return single_coin_direction

        best_moves = []
        best_score = float('-inf')

        # Find best move among four directions using expectimax
        for move in self.directions:
            game_copy = deepcopy(self)
            if game_copy.move(move):
                score = game_copy.expectimax(depth - 1, float('-inf'), float('inf'), 'max', w1, w2)
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        # Choose randomly among the best moves and one random direction to avoid deterministic loops
        all_moves = best_moves + [random.choice(self.directions)]
        weights = [5] * len(best_moves) + [1]
        if best_moves:
            return random.choices(all_moves, weights=weights, k=1)[0]
        return None

# Training function to find best weights for state evaluation function:
# [Depth 2] w1 = 9, w2 = 6, avg_turns = 79.0
# [Depth 3] w1 = 9, w2 = 6, avg_turns = 79.0
def find_best_weights(depth):
    game = Game()
    best_w1, best_w2 = 0, 0
    best_score = float('inf')

    # Testing weight of 100x100 integer sample space
    for w1 in range(1, 10):
        for w2 in range(1, 10):
            score = 0
            # Run 100 trials for each weight combination to reduce degree of randomness
            for i in range(100):
                game = Game()
                turns = 0
                while game.coin_left > 0:
                    for player in range(2):
                        game.current_player = player
                        move = game.best_move(depth, w1, w2)
                        game.move(move)
                        if game.coin_left == 0:
                            break
                    turns += 1
                score += turns

            average_score = score / 100.0
            print(f"Testing weights (w1={w1}, w2={w2}): Average Turns = {average_score}")

            if average_score < best_score:
                best_score = average_score
                best_w1, best_w2 = w1, w2

    print(best_w1, best_w2, best_score)

    return best_w1, best_w2, best_score

# Play the game by having two agents each useexpectimax against each other
def play_game(depth=2, w1=1, w2=1, game=Game()):
    turns = 0
    while game.coin_left > 0:
        for player in range(2):
            game.current_player = player
            move = game.best_move(depth, w1, w2)
            game.move(move)

            if game.coin_left == 0:
                break
        turns += 1
    return turns

# Play the game by having two agents each moving randomly against each other as a baseline to test expectimax efficiency
def random_game(game=Game()):
    turns = 0
    while game.coin_left > 0:
        for player in range(2):
            game.current_player = player
            move = random.choice(game.directions)
            game.move(move)

            if game.coin_left == 0:
                break
        turns += 1
    return turns

def demo(depth=3, w1=9, w2=6, game = Game()):
    turns = 0
    while game.coin_left > 0:
        for player in range(2):
            game.current_player = player
            move = game.best_move(depth, w1, w2)
            game.move(move)

            if game.coin_left == 0:
                break
        game.print_board()
        turns += 1
    print(f"Game finished in {turns} turns")
    return turns

def run_game(depth=3, w1=9, w2=6, sample_size=10):
    total_play = 0
    total_random = 0
    for i in range(sample_size):
        game = Game()
        game.print_board()
        total_play += play_game(depth, w1, w2, deepcopy(game))
        total_random += random_game(deepcopy(game))
    print(f"\nExpectimax: {total_play / sample_size} turns")
    print(f"Random: {total_random / sample_size} turns")
    print(f"\nThe Expectimax Algorithm is {round(total_random/total_play, 2)} Times Faster Than Random Baseline")

def main():
    parser = argparse.ArgumentParser(description="Run the Coin Collection Game Played By Expectimax Algorithm")
    parser.add_argument('--demo', action='store_true', help='Run a demo game using Expectimax.')
    parser.add_argument('--run', action='store_true', help='Evaluate and compare AI efficiency against random.')
    parser.add_argument('--optimize', action='store_true', help='Find the best weights for the evaluation function.')

    args = parser.parse_args()

    if args.demo:
        demo()
    elif args.run:
        run_game()
    elif args.optimize:
        find_best_weights(depth=3)
    else:
        print("No argument provided. Use --help for options.")

if __name__ == '__main__':
    main()
