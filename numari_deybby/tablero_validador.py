import os

class ValidadorPuzzleRuta:
    """
    Validar si un archivo de solución es correcto
    """
    def __init__(self, tamano=4):
        self.tamano = tamano
        self.total_casillas = tamano * tamano
        self.puzzle_grid = None
        self.solucion_grid = None
        self.mapa_pasos = {}

    def _cargar_grid_desde_txt(self, filepath):
        if not os.path.exists(filepath):
            print(f"Error: El archivo no se contró")
            return None
        
        grid = []
        with open(filepath, 'r') as f:
            for linea in f:
                try:
                    fila = [int(val) if val.strip().upper() != 'X' else 0 for val in linea.split()]
                    grid.append(fila)
                except ValueError:
                    print(f"Error: El archivo '{filepath}' contiene valores no numéricos")
                    return None
        return grid

    def _validar_integridad_ruta(self):
        """
        Verifica si la solución es una ruta continua y completa (1-16)
        """
        # 1. Verificar que contiene todos los números de 1 a 16
        numeros_planos = [num for fila in self.solucion_grid for num in fila]
        if sorted(numeros_planos) != list(range(1, self.total_casillas + 1)):
            print("Error de validación: La solución no contiene todos los números del 1 al 16")
            return False

        # 2. Crear un mapa de número -> coordenadas para fácil acceso
        for fila_idx, fila in enumerate(self.solucion_grid):
            for col_idx, num in enumerate(fila):
                if num != 0:
                    self.mapa_pasos[num] = (fila_idx, col_idx)
        
        # 3. Verificar que la ruta es continua
        for i in range(1, self.total_casillas):
            y1, x1 = self.mapa_pasos[i]
            y2, x2 = self.mapa_pasos[i+1]
            if abs(y1 - y2) + abs(x1 - x2) != 1:
                print(f"Error de validación: La ruta no es continua entre el paso {i} y el {i+1}")
                return False
        
        return True

    def _validar_restricciones_puzzle(self):
        """
        Verifica si la ruta de la solución sigue las reglas del puzzle
        """
        for fila_idx, fila in enumerate(self.puzzle_grid):
            for col_idx, longitud_segmento in enumerate(fila):
                # Si la casilla tiene un número de restricción
                if longitud_segmento > 0:
                    
                    paso_inicio = self.solucion_grid[fila_idx][col_idx]
                    
                    # El segmento debe tener al menos 2 pasos para tener una dirección
                    if longitud_segmento < 2:
                        continue 

                    # Asegurarse de que el segmento no se salga del tablero
                    if paso_inicio + longitud_segmento -1 > self.total_casillas:
                        print(f"Error de validación: La restricción de longitud {longitud_segmento} en ({fila_idx}, {col_idx}) hace que la ruta se salga del tablero")
                        return False

                    # Dirección del segmento (dx, dy)
                    y_actual, x_actual = self.mapa_pasos[paso_inicio]
                    y_siguiente, x_siguiente = self.mapa_pasos[paso_inicio + 1]
                    dy, dx = y_siguiente - y_actual, x_siguiente - x_actual

                    # Verificar que el resto del segmento siga en línea recta
                    for i in range(1, longitud_segmento - 1):
                        y_esperado = y_siguiente + i * dy
                        x_esperado = x_siguiente + i * dx
                        
                        paso_verificar = paso_inicio + 1 + i
                        y_real, x_real = self.mapa_pasos[paso_verificar]

                        if (y_real, x_real) != (y_esperado, x_esperado):
                            print(f"Error de validación: El segmento que inicia en el paso {paso_inicio} en ({fila_idx}, {col_idx}) debía ser recto por {longitud_segmento} casillas, pero se desvía.")
                            return False
        return True


    def validar(self, puzzle_filepath, solucion_filepath):
        """
        Orquesta el proceso completo de validación.
        """
        self.puzzle_grid = self._cargar_grid_desde_txt(puzzle_filepath)
        self.solucion_grid = self._cargar_grid_desde_txt(solucion_filepath)

        if not self.puzzle_grid or not self.solucion_grid:
            return False
        
        # --- Paso 1: Validar la ruta por sí misma ---
        if not self._validar_integridad_ruta():
            return False
        
        # --- Paso 2: Validar la ruta contra las reglas del puzzle ---
        if not self._validar_restricciones_puzzle():
            return False

        print("La solución es válida para el puzzle proporcionado")
        return True

# --- Ejecución del código ---
if __name__ == "__main__":
    validador_dos = ValidadorPuzzleRuta(tamano=4)
    # validador_dos.validar("puzzle.txt", "solucion_invalida.txt")
    validador_dos.validar("tablero.txt", "solucion.txt")
