from menu import Menu
from numari_board import NumariBoard
import os
from color import Color
from control import Control

class NumariGame:

    __MENU = Menu(["Reanudar Juego", "Juego aleatorio", "Salir"], "Numari")
    __MENU_DIFICULTY = Menu(["4 x 4", "5 x 5", "6 x 6", "Salir"], "Numari\nSelecciona la dificultad")
    __NUMARI_BOARD = None
    
    @classmethod
    def app(cls):
        while True:
            selection = cls.__MENU.select()
            
            match selection:
                case 0: 
                    cls.__current_play()
                    pass
                case 1:
                    cls.__select_dificulty()
                case 2: 
                    return
        
    @classmethod        
    def __current_play(cls):
        os.system('cls')
        if not cls.__NUMARI_BOARD:
            print(f"{Color.BLUE}No hay jugada activa{Color.RESET}")
        else:
            cls.__NUMARI_BOARD.play()
        print('Presiona Enter para salir')
        Control.select({'ENTER':None})
        os.system('cls')
        
    
    @classmethod   
    def __select_dificulty(cls):
        selection = cls.__MENU_DIFICULTY.select()
       
        if selection == 0:
            cls.__random_game(n=4)
        elif selection == 1:
            cls.__random_game(n=5)
        elif selection == 2:
            cls.__random_game(n=6)
        else:
            return
    
        
    @classmethod        
    def __random_game(cls, n):
        cls.__NUMARI_BOARD = NumariBoard(n=n)
    

if __name__ == "__main__":
    NumariGame().app()