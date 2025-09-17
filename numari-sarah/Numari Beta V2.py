import random
import os
import time

# ==============================================================================
# ## Class 1: MapGenerator (NO CHANGE)
# ==============================================================================
class MapGenerator:
    """
    Generates a valid and solvable Numari puzzle of a given size.
    """
    def __init__(self, rows=4, cols=4):
        """Initializes the generator for a specific grid size."""
        self.rows = rows
        self.cols = cols
        self.total_cells = rows * cols

    def generate_map(self):
        """Generates and returns a valid puzzle and its corresponding solution."""
        while True:
            path = self._find_hamiltonian_path()
            if not path:
                continue 
            solution_grid = self._convert_path_to_solution_grid(path)
            puzzle_grid = self._convert_path_to_puzzle_grid(path)
            if self._is_puzzle_valid(puzzle_grid):
                return puzzle_grid, solution_grid
    
    def _find_hamiltonian_path(self):
        """Finds a random Hamiltonian path using a recursive backtracking algorithm."""
        path = []
        visited = set()
        start_node = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))

        def backtrack(node):
            path.append(node)
            visited.add(node)
            if len(path) == self.total_cells:
                return True
            r, c = node
            neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            random.shuffle(neighbors)
            for neighbor_r, neighbor_c in neighbors:
                if 0 <= neighbor_r < self.rows and 0 <= neighbor_c < self.cols:
                    if (neighbor_r, neighbor_c) not in visited:
                        if backtrack((neighbor_r, neighbor_c)):
                            return True
            path.pop()
            visited.remove(node)
            return False

        if backtrack(start_node):
            return path
        return None

    def _convert_path_to_solution_grid(self, path):
        """Converts a coordinate path into a direction-based solution grid."""
        grid = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(len(path) - 1):
            r1, c1 = path[i]; r2, c2 = path[i+1]
            if r2 > r1: grid[r1][c1] = 'D'
            elif r2 < r1: grid[r1][c1] = 'U'
            elif c2 > c1: grid[r1][c1] = 'R'
            elif c2 < c1: grid[r1][c1] = 'L'
        final_r, final_c = path[-1]
        grid[final_r][final_c] = 'F'
        return grid

    def _convert_path_to_puzzle_grid(self, path):
        """Converts a path into a playable puzzle with numbers."""
        min_groups = self.total_cells // 5 if self.total_cells > 16 else 4
        max_groups = self.total_cells // 3 if self.total_cells > 16 else 6
        k = random.randint(min_groups, max_groups)
        target_sum = self.total_cells - k
        max_val = (self.rows + self.cols) - 1
        partition = self._get_constrained_partition(k, target_sum, max_val=max_val)
        puzzle_grid = [['C' for _ in range(self.cols)] for _ in range(self.rows)]
        path_cursor = 0
        for num in partition:
            if path_cursor < len(path):
                r, c = path[path_cursor]
                puzzle_grid[r][c] = num
                path_cursor += (num + 1)
        return puzzle_grid

    def _get_constrained_partition(self, k, target_sum, max_val):
        """Helper to find k integers that sum to target_sum, each <= max_val."""
        while True:
            nums = [0] * k
            for _ in range(target_sum):
                valid_indices = [i for i, val in enumerate(nums) if val < max_val]
                if not valid_indices: break
                chosen_index = random.choice(valid_indices)
                nums[chosen_index] += 1
            if sum(nums) == target_sum:
                random.shuffle(nums)
                return nums
                
    def _is_puzzle_valid(self, puzzle_grid):
        """Checks if the puzzle meets constraints (e.g., no adjacent numbers > 0)."""
        for r in range(self.rows):
            for c in range(self.cols):
                if isinstance(puzzle_grid[r][c], int) and puzzle_grid[r][c] > 0:
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            neighbor_val = puzzle_grid[nr][nc]
                            if isinstance(neighbor_val, int) and neighbor_val > 0:
                                return False
        return True

# ==============================================================================
# ## Class 2: Board (MODIFIED)
# ==============================================================================
class Board:
    """Represents the game board, holding the puzzle state and handling display."""
    def __init__(self, puzzle_grid, solution_grid=None):
        """Initializes the Board object."""
        if not puzzle_grid:
            raise ValueError("A puzzle grid must be provided.")
        self.puzzle_grid = puzzle_grid
        self.solution_grid = solution_grid
        self.rows = len(puzzle_grid)
        self.cols = len(puzzle_grid[0]) if self.rows > 0 else 0
        self.total_cells = self.rows * self.cols

    def display(self, player_path=None):
        """Displays the puzzle grid, highlighting the player's current path."""
        if player_path is None:
            player_path = []
        print("\n   " + "   ".join(map(str, range(self.cols))))
        print("  " + "----" * self.cols)
        for r in range(self.rows):
            row_str = f"{r}| "
            for c in range(self.cols):
                cell_value = self.puzzle_grid[r][c]
                if (r, c) in player_path:
                    row_str += f"[{cell_value}] " if isinstance(cell_value, int) else "[X] "
                else:
                    row_str += f" {cell_value}  "
            print(row_str)
        print()

    # --- NEW METHOD TO DISPLAY THE SOLUTION ---
    def display_solution(self):
        """Displays the hidden solution grid."""
        if not self.solution_grid:
            print("\n*** No solution grid available for this puzzle. ***")
            return
            
        print("\n--- SOLUTION GRID ---")
        print("   " + "   ".join(map(str, range(self.cols))))
        print("  " + "----" * self.cols)
        for r in range(self.rows):
            row_str = f"{r}| "
            for c in range(self.cols):
                cell_value = self.solution_grid[r][c]
                row_str += f" {cell_value}  "
            print(row_str)
        print()

# ==============================================================================
# ## Class 3: Game (MODIFIED TO CORRECTLY SHOW SOLUTION)
# ==============================================================================
class Game:
    """Manages the main game loop, player input, and all game logic."""
    def __init__(self):
        """Initializes a new game session."""
        self.board = None
        self.game_over = False
        self.player_path = []
        self.move_count = 0
        self.start_time = None
        self.status_message = ""
        self.player_quit = False
        self.current_group_target_size = 0
        self.current_group_progress = 0
        self.group_start_indices = []
        self.hint_limit = 0
        self.hints_used = 0
        self.hint_move_penalty = 0
        self.hint_time_penalty = 0

    def start_new_game(self):
        """Handles the complete flow of starting a new game."""
        grid_size, difficulty = self.select_difficulty()
        if grid_size is None:
            self.player_quit = True
            return

        self.setup_difficulty(grid_size, difficulty)
        
        print(f"Generating a new {grid_size}x{grid_size} Numari puzzle...")
        generator = MapGenerator(rows=grid_size, cols=grid_size)
        puzzle, solution = generator.generate_map()
        self.board = Board(puzzle_grid=puzzle, solution_grid=solution)
        self.start_time = time.time()
        self.reset_game_state(new_game=True)
        self.run_game_loop()

    def select_difficulty(self):
        """Displays a difficulty selection menu for the player."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("==============================")
            print("===   CHOOSE A DIFFICULTY    ===")
            print("==============================")
            print("1. Easy   (4x4)")
            print("2. Medium (5x5)")
            print("3. Hard   (6x6)")
            print("\nType 'quit' to exit.")
            choice = input("Enter your choice (1-3): ").strip()

            if choice == '1': return 4, "Easy"
            if choice == '2': return 5, "Medium"
            if choice == '3': return 6, "Hard"
            if choice.lower() == 'quit': return None, None
            
            input("Invalid choice. Press Enter to try again...")
    
    def setup_difficulty(self, size, difficulty_name):
        """Sets game parameters like hint limits based on the chosen difficulty."""
        if difficulty_name == "Easy":
            self.hint_limit = 3; self.hint_move_penalty = 3; self.hint_time_penalty = 30
        elif difficulty_name == "Medium":
            self.hint_limit = 2; self.hint_move_penalty = 5; self.hint_time_penalty = 45
        elif difficulty_name == "Hard":
            self.hint_limit = 1; self.hint_move_penalty = 7; self.hint_time_penalty = 60

    def reset_game_state(self, new_game=False):
        """Resets the current level's state, keeping the timer running."""
        self.player_path = []; self.move_count = 0
        self.current_group_target_size = 0; self.current_group_progress = 0
        self.group_start_indices = []
        self.status_message = "Level restarted. Good luck!"
        if new_game:
            self.hints_used = 0

    def run_game_loop(self):
        """The main loop that runs until the game is over."""
        while not self.game_over:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=============================="); print("===      NUMARI CONSOLE      ==="); print("==============================")
            self.board.display(self.player_path)
            self.display_status()
            self.process_player_input()
        
        # --- MODIFICATION ---
        # The loop is now simpler. The final display is handled by
        # the methods that end the game (make_move or show_solution).

    def display_status(self):
        """Prints the current status of the game to the console."""
        if self.start_time:
            elapsed_seconds = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed_seconds, 60)
            print(f"Time: {minutes:02d}:{seconds:02d}")

        print(f"Moves: {self.move_count} | Hints Left: {self.hint_limit - self.hints_used}")
        
        if self.current_group_target_size > 0:
            print(f"Current Group: {self.current_group_progress} / {self.current_group_target_size}")
        else:
            print("Select a numbered cell to start a group.")
        
        if self.status_message:
            print(f"\n*** {self.status_message} ***")
            self.status_message = ""

    def process_player_input(self):
        """Gets and processes input from the player."""
        prompt = "\nEnter 'row col' | 'reset' | 'hint' | 'solve' | 'new' | 'quit': "
        user_input = input(prompt).lower().strip()

        if user_input == 'quit': self.game_over = True; self.player_quit = True; self.status_message = "You have quit the game."; return
        if user_input == 'reset': self.reset_game_state(); return
        if user_input == 'new': self.game_over = True; return
        if user_input == 'hint': self.provide_hint(); return
        if user_input == 'solve': self.show_solution(); return

        try:
            parts = user_input.split()
            if len(parts) != 2: raise ValueError()
            row, col = int(parts[0]), int(parts[1])
            if len(self.player_path) > 0 and (row, col) == self.player_path[-1]:
                self.undo_last_move()
            else:
                self.make_move(row, col)
        except (ValueError, IndexError):
            self.status_message = "Invalid input. Please enter coordinates like '2 1'."
    
    def provide_hint(self):
        """Provides a hint to the player and applies penalties."""
        if self.hints_used >= self.hint_limit:
            self.status_message = "No hints left!"; return

        solution_path = self.reconstruct_path_from_solution_grid()
        if not solution_path:
            self.status_message = "Could not generate a hint."; return

        current_pos_index = len(self.player_path)
        if current_pos_index >= len(solution_path):
            self.status_message = "You are at the end! No more hints needed."; return
        
        hint_length = 0
        if self.hint_limit == 3: # Easy
            next_group_start = next((i for i, c in enumerate(solution_path) if i >= current_pos_index and isinstance(self.board.puzzle_grid[c[0]][c[1]], int)), -1)
            if next_group_start != -1:
                group_num = self.board.puzzle_grid[solution_path[next_group_start][0]][solution_path[next_group_start][1]]
                hint_length = group_num + 1
        elif self.hint_limit == 2: # Medium
            next_group_start = next((i for i, c in enumerate(solution_path) if i >= current_pos_index and isinstance(self.board.puzzle_grid[c[0]][c[1]], int)), -1)
            if next_group_start != -1:
                group_num = self.board.puzzle_grid[solution_path[next_group_start][0]][solution_path[next_group_start][1]]
                hint_length = (group_num + 1) // 2
        else: # Hard
            hint_length = 2
        
        if hint_length == 0: hint_length = 1

        self.hints_used += 1
        self.move_count += self.hint_move_penalty
        self.start_time -= self.hint_time_penalty
        
        hint_path = solution_path[current_pos_index : current_pos_index + hint_length]
        self.status_message = f"Hint: Next step(s) are {hint_path}. Penalties applied."

    def undo_last_move(self):
        """Reverts the last move made by the player."""
        if not self.player_path: return
        
        undone_move = self.player_path.pop()
        self.move_count -= 1; self.current_group_progress -= 1
        self.status_message = f"Undid move to {undone_move}."

        if self.current_group_progress == 0:
            self.current_group_target_size = 0
            self.group_start_indices.pop()
            if self.group_start_indices:
                prev_idx = self.group_start_indices[-1]
                prev_coords = self.player_path[prev_idx]
                prev_num = self.board.puzzle_grid[prev_coords[0]][prev_coords[1]]
                self.current_group_target_size = prev_num + 1
                self.current_group_progress = len(self.player_path) - prev_idx

    # --- MODIFIED ---
    def show_solution(self):
        """Displays the solution grid, pauses, and ends the game."""
        self.game_over = True
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=============================="); print("===       SOLUTION           ==="); print("==============================")
        self.board.display(self.player_path) # Show the player's current path
        self.board.display_solution() # Show the solution grid
        print("\n*** Solution revealed. Game over. ***")
        # Pause to allow the player to see the solution
        input("\nPress Enter to continue...")

    def make_move(self, row, col):
        """Validates and performs a player's move."""
        if not (0 <= row < self.board.rows and 0 <= col < self.board.cols):
            self.status_message = "Coordinates are outside the board."; return

        is_valid, message = self.is_valid_move(row, col)
        if not is_valid:
            self.status_message = f"Invalid Move: {message}"; return
        
        if self.current_group_progress == self.current_group_target_size:
            self.group_start_indices.append(len(self.player_path))
        
        self.player_path.append((row, col))
        self.move_count += 1
        
        if self.current_group_progress == self.current_group_target_size:
            cell_value = self.board.puzzle_grid[row][col]
            self.current_group_target_size = cell_value + 1
            self.current_group_progress = 1
        else:
            self.current_group_progress += 1

        if len(self.player_path) == self.board.total_cells:
            self.game_over = True
            elapsed_seconds = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed_seconds, 60)
            self.status_message = f"Congratulations! Solved in {self.move_count} moves! Time: {minutes:02d}:{seconds:02d}"
            
            # --- MODIFICATION ---
            # Display the final win screen here and pause
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=============================="); print("===      PUZZLE SOLVED!      ==="); print("==============================")
            self.board.display(self.player_path)
            self.display_status()
            input("\nPress Enter to continue...")

    def reconstruct_path_from_solution_grid(self):
        """Converts the letter-based solution grid into a list of coordinates."""
        if not self.board.solution_grid: return []
        path_map, all_nodes, incoming_edges = {}, set(), set()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                all_nodes.add((r,c))
                direction = self.board.solution_grid[r][c]
                if direction in ['U', 'D', 'L', 'R']:
                    dr, dc = {'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}[direction]
                    next_node = (r + dr, c + dc)
                    path_map[(r,c)] = next_node; incoming_edges.add(next_node)
        start_node_set = all_nodes - incoming_edges
        if not start_node_set: return []
        start_node = start_node_set.pop()
        path = [start_node]; current = start_node
        while len(path) < self.board.total_cells:
            current = path_map.get(current)
            if current is None: return [] 
            path.append(current)
        return path
        
    def is_valid_move(self, row, col):
        """Checks if a move to (row, col) is valid based on Numari rules."""
        cell_value = self.board.puzzle_grid[row][col]
        is_cell_a_number = isinstance(cell_value, int)

        if (row, col) in self.player_path:
            return False, "That cell has already been selected."
        if not self.player_path:
            return (True, "") if is_cell_a_number else (False, "The first move must be on a numbered cell.")
        last_r, last_c = self.player_path[-1]
        if abs(row - last_r) + abs(col - last_c) != 1:
            return False, "You can only move to an adjacent (non-diagonal) cell."
        group_is_complete = self.current_group_progress == self.current_group_target_size
        if group_is_complete:
            if not is_cell_a_number:
                return False, "The previous group is complete. You must start a new group on a numbered cell."
        else:
            if is_cell_a_number:
                return False, "You cannot select another numbered cell until the current group is complete."
        return True, ""

# ==============================================================================
# ## Main Execution Block
# ==============================================================================
if __name__ == "__main__":
    while True:
        game = Game()
        game.start_new_game()
        
        if game.player_quit:
            break
            
        play_again = input("\nPlay another game? (y/n): ").lower().strip()
        if play_again != 'y':
            break
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Thanks for playing Numari!")