import random
import os
import time

# ==============================================================================
# ## Class 1: MapGenerator (NO CHANGE)
# ==============================================================================
class MapGenerator:
    def __init__(self, rows=4, cols=4):
        self.rows = rows
        self.cols = cols
        self.total_cells = rows * cols

    def generate_map(self):
        while True:
            path = self._find_hamiltonian_path()
            if not path:
                continue 
            solution_grid = self._convert_path_to_solution_grid(path)
            puzzle_grid = self._convert_path_to_puzzle_grid(path)
            if self._is_puzzle_valid(puzzle_grid):
                return puzzle_grid, solution_grid
    
    def _find_hamiltonian_path(self):
        path = []
        visited = set()
        start_row, start_col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
        start_node = (start_row, start_col)

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
        while True:
            nums = [0] * k
            current_sum = 0
            for _ in range(target_sum):
                valid_indices = [i for i, val in enumerate(nums) if val < max_val]
                if not valid_indices: break
                chosen_index = random.choice(valid_indices)
                nums[chosen_index] += 1
                current_sum += 1
            if current_sum == target_sum:
                random.shuffle(nums); return nums
                
    def _is_puzzle_valid(self, puzzle_grid):
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
# ## Class 2: Board (NO CHANGE)
# ==============================================================================
class Board:
    def __init__(self, puzzle_grid, solution_grid=None):
        if not puzzle_grid:
            raise ValueError("A puzzle grid must be provided.")
        self.puzzle_grid = puzzle_grid
        self.solution_grid = solution_grid
        self.rows = len(puzzle_grid)
        self.cols = len(puzzle_grid[0]) if self.rows > 0 else 0
        self.total_cells = self.rows * self.cols

    def display(self, player_path=None):
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

# ==============================================================================
# ## Class 3: Game (MODIFIED FOR HINT SYSTEM)
# ==============================================================================
class Game:
    def __init__(self):
        self.board = None
        self.game_over = False
        self.player_path = []
        self.move_count = 0
        self.start_time = None
        self.status_message = ""
        self.player_quit = False
        # Group tracking
        self.current_group_target_size = 0
        self.current_group_progress = 0
        self.group_start_indices = []
        # Hint tracking
        self.hint_limit = 0
        self.hints_used = 0
        self.hint_move_penalty = 0
        self.hint_time_penalty = 0

    def start_new_game(self):
        """Lets the player select difficulty and starts a new game session."""
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
        """Displays a menu and returns the selected grid size and difficulty name."""
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
        """Sets game parameters based on the chosen difficulty."""
        if difficulty_name == "Easy":
            self.hint_limit = 3
            self.hint_move_penalty = 3
            self.hint_time_penalty = 30
        elif difficulty_name == "Medium":
            self.hint_limit = 2
            self.hint_move_penalty = 5
            self.hint_time_penalty = 45
        elif difficulty_name == "Hard":
            self.hint_limit = 1
            self.hint_move_penalty = 7
            self.hint_time_penalty = 60

    def reset_game_state(self, new_game=False):
        """Resets the current level's state."""
        self.player_path = []
        self.move_count = 0
        self.current_group_target_size = 0
        self.current_group_progress = 0
        self.group_start_indices = []
        self.status_message = "Level restarted. Good luck!"
        if new_game:
            self.hints_used = 0

    def run_game_loop(self):
        """The main loop that runs until the game is over."""
        while not self.game_over:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("==============================")
            print("===      NUMARI CONSOLE      ===")
            print("==============================")
            self.board.display(self.player_path)
            self.display_status()
            self.process_player_input()
        
        # Display final screen
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=============================="); print("===        GAME OVER         ==="); print("==============================")
        self.board.display(self.player_path)
        self.display_status()

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
        prompt = "\nEnter 'row col' | 'reset' | 'hint' | 'new' | 'quit': "
        user_input = input(prompt).lower().strip()

        if user_input == 'quit': self.game_over = True; self.player_quit = True; self.status_message = "You have quit the game."; return
        if user_input == 'reset': self.reset_game_state(); return
        if user_input == 'new': self.game_over = True; return
        if user_input == 'hint': self.provide_hint(); return

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
        """Provides a hint to the player based on difficulty and applies penalties."""
        if self.hints_used >= self.hint_limit:
            self.status_message = "No hints left!"
            return

        solution_path = self.reconstruct_path_from_solution_grid()
        if not solution_path:
            self.status_message = "Could not generate a hint."; return

        current_pos_index = len(self.player_path)
        if current_pos_index >= len(solution_path):
            self.status_message = "You are at the end! No more hints needed."
            return
        
        # Determine hint length based on difficulty
        hint_length = 0
        if self.hint_limit == 3: # Easy
            # Find the start of the next group
            next_group_start = -1
            for i, coord in enumerate(solution_path):
                if i >= current_pos_index and isinstance(self.board.puzzle_grid[coord[0]][coord[1]], int):
                    next_group_start = i
                    break
            if next_group_start != -1:
                group_num = self.board.puzzle_grid[solution_path[next_group_start][0]][solution_path[next_group_start][1]]
                hint_length = group_num + 1
        elif self.hint_limit == 2: # Medium
             # Find the start of the next group and give half
            next_group_start = -1
            for i, coord in enumerate(solution_path):
                if i >= current_pos_index and isinstance(self.board.puzzle_grid[coord[0]][coord[1]], int):
                    next_group_start = i
                    break
            if next_group_start != -1:
                group_num = self.board.puzzle_grid[solution_path[next_group_start][0]][solution_path[next_group_start][1]]
                hint_length = (group_num + 1) // 2
        else: # Hard
            hint_length = 2
        
        if hint_length == 0: hint_length = 1 # Ensure at least one step is given

        # Apply penalties and give hint
        self.hints_used += 1
        self.move_count += self.hint_move_penalty
        self.start_time -= self.hint_time_penalty # Subtracting from start time adds to elapsed time
        
        hint_path = solution_path[current_pos_index : current_pos_index + hint_length]
        self.status_message = f"Hint: Next step(s) are {hint_path}. Penalties applied."

    def undo_last_move(self):
        """Reverts the last move."""
        if not self.player_path: return
        
        undone_move = self.player_path.pop()
        self.move_count -= 1; self.current_group_progress -= 1
        self.status_message = f"Undid move to {undone_move}."

        if self.current_group_progress == 0:
            self.current_group_target_size = 0
            self.group_start_indices.pop()
            if self.group_start_indices:
                prev_group_start_index = self.group_start_indices[-1]
                prev_group_start_coords = self.player_path[prev_group_start_index]
                prev_group_num = self.board.puzzle_grid[prev_group_start_coords[0]][prev_group_start_coords[1]]
                self.current_group_target_size = prev_group_num + 1
                self.current_group_progress = len(self.player_path) - prev_group_start_index

    def make_move(self, row, col):
        """Attempts to make a move and updates the game state if valid."""
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

    def reconstruct_path_from_solution_grid(self):
        """Converts the letter-based solution grid into a list of coordinates."""
        if not self.board.solution_grid: return []
        path_map, all_nodes, incoming_edges = {}, set(), set()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                all_nodes.add((r,c))
                direction = self.board.solution_grid[r][c]
                if direction in ['U', 'D', 'L', 'R']:
                    dr, dc = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}[direction]
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