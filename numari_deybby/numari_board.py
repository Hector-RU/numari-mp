from generador_tablero import GeneradorPuzzleRuta
from control import Control
import os
import time

class NumariBoard:
    
    def __init__(self, board:list=None, n:int=4):
        """
        board: List of lists of the board, None for generate a random board
        n: lenght of board n*n"""
        
        if not board:
            self.length = n
            board, solution = GeneradorPuzzleRuta(tamano=n).generar_puzzle()
            board = [[' ' if celda == 0 else celda - 1 for celda in fila] for fila in board]
        
        self.board = board
        self.length = len(board)
        self.positions = self._numbers_position()
    
    @staticmethod
    def _move_to(position, move):
        x,y = position
        movements = {'R':(x+1, y), 'L':(x-1, y), 'D': (x, y+1), 'U':(x, y-1)}
        return movements[move]    
    

    def _numbers_position(self):
        positions = []
        
        for y in range(self.length):
            for x in range(self.length):
                
                if isinstance(self.board[y][x], int):
                    positions.append((x, y))
        return positions
    
    
    def show_game(self, board, collected, problem=None):
        
        numbers_positions, movements = collected      
        orange_cells = []
        
       
        for i in range(len(movements)):
            orange_cells.append(movements[-(i+1)])
            if movements[-(i+1)] == numbers_positions[-1]:
                x, y = numbers_positions[-1]
                if i == board[y][x]:
                    orange_cells = []
                break
                    
        # 34: Azul
        # 32: Verde
        # 38;5;208: Naranja
        # 31: Rojo    
        
        for y in range(self.length):
            for x in range(self.length):
                
                # Naranja para celdas incompletas 
                if (x, y) in orange_cells:
                    print(f'| \033[38;5;208m{board[y][x]}\033[0m ', end='')  
                
                # Verde para celdas ya completadas      
                elif (x, y) in movements: 
                    print(f'| \033[32m{board[y][x]}\033[0m ', end='') 
                    
                # Rojo para celda a la que no se puede mover
                elif (x, y) == problem:
                    # # SI la celda esta vacia pinta el cuadro rojo vacio
                    # if board[y][x] == ' ':
                    #     print("\033[41m   \033[0m")
                    # # Si no esta vacia pinta el cuadro rojo con el numero
                    # else:
                    #     print(F"| \033[41m{print("\033[41m   \033[0m")}\033[0m |")  
                    
                    print(f'|\033[41m {board[y][x]} \033[0m', end='')
                    
                elif isinstance(board[y][x], int):
                    print(f'| \033[34m{board[y][x]}\033[0m ', end='')
                else:
                    print(f'| {board[y][x]} ', end='')
            print('|')
            print(f"{'-'* (self.length* 4)}-")
                
                
                
                
    def show_board(self, actual_position=None, board=None):
        if not board:
            board = self.board
        print(f"{'-'* (self.length* 4)}-")
        for y in range(self.length):
            for x in range(self.length):
                
                
                if actual_position and actual_position==(x,y):
                    
                    # \033[31mTexto rojo\033[0m
                    print(f'| \033[34m{board[y][x]}\033[0m ', end='')
                else:
                    print(f'| {board[y][x]} ', end='')

            print('|')
            print(f"{'-'* (self.length* 4)}-")
        
    def __select_begin_cell(self):
        
        begins_position = self._numbers_position()
        positions_quantity = len(begins_position)
        
        position = 0
        while True:
            os.system('cls')
            print('Selecciona la celda inicial: ')
            self.show_board(begins_position[position])
            print('[A] Anterior, [D] Siguiente, [ENTER] para seleccionar, [ESC] para salir')
            human_play = Control.select({'A':-1, 'D':1, 'ENTER':'ENTER', 'ESC':'ESC'})
            if isinstance(human_play, str):
                if human_play == 'ENTER':
                    return (begins_position[position])
                else: 
                    return None
            if position == 0 and human_play == -1:
                position = positions_quantity-1
            elif position == positions_quantity-1 and human_play == 1:
                position = 0
            else:
                position += human_play
            
        
    def play(self):
        
        while True:
            board =  [[cell for cell in row] for row in self.board]
            begin_position = self.__select_begin_cell()
            
            if begin_position:
                x, y = begin_position
            else:
                break
            
            collected_cells = [[False for _ in range(self.length)] for _ in range(self.length)]
            x_number, y_number = x, y
            movements = []
            numbers_positions = []
            i_position = 0
            collected_cells[y][x] = True
            
            while len(numbers_positions) <= self.length**2:
                
                while i_position <= board[y_number][x_number]:
                    os.system('cls')
                    temporal_movements = movements.copy()
                    temporal_numbers_positions = numbers_positions.copy()
                    temporal_movements.append((x, y))
                    temporal_numbers_positions.append((x_number, y_number))
                    
                    self.show_game(board, (temporal_numbers_positions, temporal_movements))            
                       
                    move = Control.select({'W':(0, -1), 'S':(0, 1), 'A':(-1, 0), 'D':(1, 0), 'C':'C', 'ESC':'ESC'})
                        
                    if isinstance(move, str):
                        if move == 'ESC':
                            break
                        else: # C
                            board =  [[cell for cell in row] for row in self.board]
                            begin_position = self.__select_begin_cell()
                            if begin_position:
                                x, y = begin_position
                            else: # Salir
                                break
                            movements = []
                            numbers_positions = []
                            i_position = 0
                            x, y = begin_position
                            collected_cells = [[False for _ in range(self.length)] for _ in range(self.length)]
                            collected_cells[y][x] = True
                            
                            continue
                        
                        
                    new_x, new_y = x + move[0], y + move[1]
                        
                    if not (0 <= new_x < self.length) or (not 0 <= new_y < self.length):
                        continue
                    if movements and movements[-1] == (new_x, new_y):
                        i_position -= 1
                        movements.pop()
                        collected_cells[y][x] = False
                        if i_position < 0 and numbers_positions:
                            x_number, y_number = numbers_positions.pop()
                            i_position = board[y_number][x_number]
                        else:
                            board[y][x] = " "
                        
                        x, y = new_x, new_y
                        continue
                    
                    if collected_cells[new_y][new_x]:                        
                        continue
                        
                    if board[new_y][new_x] != " " and i_position < board[y_number][x_number]:
                        os.system('cls')
                        self.show_game(board=board, collected=(temporal_numbers_positions, temporal_movements), problem=(new_x, new_y))
                        time.sleep(0.5) 
                        continue
                    
                    if i_position == board[y_number][x_number] and board[new_y][new_x] == " ":
                        os.system('cls')
                        self.show_game(board=board, collected=(temporal_numbers_positions, temporal_movements), problem=(new_x, new_y))
                        time.sleep(0.5) 
                        continue
                    
                    movements.append((x, y))
                    board[new_y][new_x] = 'X' if board[new_y][new_x] == ' ' else board[new_y][new_x]
                    x, y = new_x, new_y
                    collected_cells[y][x] = True
                    i_position += 1

                    if any(all(all(row) for row in collected_cells) for row in collected_cells):
                        print("Ganaste")
                        self.show_game(board, (temporal_numbers_positions, temporal_movements))
                        return

                    
                numbers_positions.append((x_number, y_number))
                
                x_number, y_number = x, y
                i_position = 0
            break
        
if __name__ == '__main__':
    # b = NumariBoard([
    #                 [3, " ", " ", " ", " "],
    #                 [" ", " ", " ", 3, " "],
    #                 [" ", " ", 3, " ", " "],
    #                 [" ", 3, " ", " ", " "],
    #                 [3, " ", " ", " ", 4]])
    # b.play()
    new_puzzle = NumariBoard(n=5)
    new_puzzle.play()
                    