import keyboard
import time
class Control:
    
    
    @staticmethod
    def select(selections:dict):
        buttons = [k.upper() for k in selections.keys()] # Al presionar una tecla, el programa la lee en mayúsculas
        
        while True:
            key = keyboard.read_key(suppress=True).upper()
            time.sleep(0.2)
            
            if key not in buttons: continue

            return selections[key]
        

if __name__ == '__main__':
   if Control.select({'W':'UP', 'S':'DOWN', 'A':'LEFT', 'ESC':'SALIR'}) == 'SALIR':
        print('Salir')
   else:
        print('Continuar')
    
    
    