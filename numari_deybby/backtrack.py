import random
class Backtrack:
    
    def __valid_edges(board):

        board = [[cell for cell in row] for row in board]
        length = len(board)
        
        # En la fila superior no puedes ir hacia arriba.
        # En la fila inferior no puedes ir hacia abajo.
        # En la primera columna no puedes ir a la izquierda.
        # En la última columna no puedes ir a la derecha.

        for position in [0, length-1]:
            
            letter_1, letter_2 = ('U', 'L') if position == 0 else ('D', 'R')
            for i in range(length):
                board[position][i] = board[position][i].replace(letter_1, '')
                board[i][position] = board[i][position].replace(letter_2, '')
        
        return board
    
    def __unique_final(board):
        "Ensure that only has a final"
        
        find_final = False
        
        for row in board:
            for cell in row:
                
                if not cell == 'F': continue
                
                # If the actual cell is F and F is finded it means there are two F
                if find_final: return False
                
                find_final = True
                
        return True
    
    def __clean_movements(board, position):
    
        board = [[cell for cell in row] for row in board]
        length = len(board)
        
        x, y = position
        
        invalid_move = {'R':(x-1, y), 'L':(x+1, y), 'D': (x, y-1), 'U':(x, y+1)}
        
        for letter, new_position in invalid_move.items():
            
            if any(value >= length for value in new_position): continue
            new_x, new_y = new_position
            
            if len(board[new_y][new_x]) == 1:
                continue
            board[new_y][new_x] = board[new_y][new_x].replace(letter, '')
        
        return board
    
    def __move_to(position, move):
        x,y = position
        movements = {'R':(x+1, y), 'L':(x-1, y), 'D': (x, y+1), 'U':(x, y-1)}
        return movements[move]
    
    
    def solve(board, position:tuple=None, cells_explored:int=0):
    
        board = [[cell for cell in row] for row in board]
        length = len(board)
        
        # If no cell explored, clean edges
        if cells_explored == 0:
            board = Backtrack.__valid_edges(board=board)
        
        # If there are more than a Final, Can't solve the board
        if not Backtrack.__unique_final(board): 
            return None
        
        # Validate that board is not full
        if cells_explored == length**2 -1:
            return board, position
        
        if not position:
            x = random.randint(0, length-1)
            y = random.randint(0, length-1)
        else:
            x, y = position
    
        move = board[y][x].replace('F', '')
        
        all_move = [letter for letter in move]
        random.shuffle(all_move)
        
        move = board[y][x]
        
        for letter in all_move:
            
            new_board = Backtrack.__clean_movements(board=board, position=(x, y))
            new_x, new_y = Backtrack.__move_to(position=(x, y), move=letter)
            
            new_board[y][x] = letter
            
            value_return = Backtrack.solve(board=new_board, position=(new_x, new_y), cells_explored=cells_explored+1)
            
            if value_return: 
                new_board, _ = value_return
                return new_board, (x, y)