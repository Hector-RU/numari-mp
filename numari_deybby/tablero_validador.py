import os
from backtrack import Backtrack

class ValidadorPuzzleRuta:
    """
    Validar si un archivo de solución es correcto y, opcionalmente,
    reportar si el tablero tiene al menos una solución mediante backtracking.
    """
    def __init__(self, tamano=4):
        self.tamano = tamano
        self.total_casillas = tamano * tamano
        self.puzzle_grid = None
        self.solucion_grid = None
        self.mapa_pasos = {}

    def _cargar_grid_desde_txt(self, filepath):
        if not os.path.exists(filepath):
            print(f"Error: El archivo '{filepath}' no se encontró")
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
        Verifica si la solución es una ruta continua y completa (1..N)
        """
        numeros_planos = [num for fila in self.solucion_grid for num in fila]
        if sorted(numeros_planos) != list(range(1, self.total_casillas + 1)):
            print(f"Error de validación: La solución no contiene todos los números del 1 al {self.total_casillas}")
            return False

        # mapa número -> coordenadas
        self.mapa_pasos.clear()
        for fila_idx, fila in enumerate(self.solucion_grid):
            for col_idx, num in enumerate(fila):
                if num != 0:
                    self.mapa_pasos[num] = (fila_idx, col_idx)
        
        # Continuidad
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
                if longitud_segmento > 0:
                    paso_inicio = self.solucion_grid[fila_idx][col_idx]

                    # Segmentos de longitud 1 no imponen dirección
                    if longitud_segmento < 2:
                        continue

                    # No salirse del tablero
                    if paso_inicio + longitud_segmento - 1 > self.total_casillas:
                        print(f"Error de validación: La restricción {longitud_segmento} en ({fila_idx}, {col_idx}) se sale del tablero")
                        return False

                    # Dirección del segmento (dx, dy)
                    y_actual, x_actual = self.mapa_pasos[paso_inicio]
                    y_siguiente, x_siguiente = self.mapa_pasos[paso_inicio + 1]
                    dy, dx = y_siguiente - y_actual, x_siguiente - x_actual

                    # Rectitud del segmento
                    for i in range(1, longitud_segmento - 1):
                        y_esperado = y_siguiente + i * dy
                        x_esperado = x_siguiente + i * dx
                        paso_verificar = paso_inicio + 1 + i
                        y_real, x_real = self.mapa_pasos[paso_verificar]
                        if (y_real, x_real) != (y_esperado, x_esperado):
                            print(f"Error de validación: El segmento que inicia en el paso {paso_inicio} en ({fila_idx}, {col_idx}) debía ser recto por {longitud_segmento} casillas, pero se desvía.")
                            return False
        return True

    def _convertir_a_formato_backtrack(self):
        """Convierte el tablero Numari al formato que acepta Backtrack"""
        board = [['UDLRF' for _ in range(self.tamano)] for _ in range(self.tamano)]
        # Marcar la última casilla como Final
        board[self.tamano - 1][self.tamano - 1] = 'F'
        return board

    def tiene_solucion(self, puzzle_filepath):
        """
        Verifica si el puzzle tiene al menos una solución válida
        """
        self.puzzle_grid = self._cargar_grid_desde_txt(puzzle_filepath)
        if not self.puzzle_grid:
            return False

        board_backtrack = self._convertir_a_formato_backtrack()
        resultado = Backtrack.solve(board_backtrack)
        if resultado:
            board_solucion, _ = resultado
            return True
        return False

    def validar(self, puzzle_filepath, solucion_filepath, verificar_existencia=True):
        """
        Orquesta el proceso completo de validación de la solución y,
        además, informa si el tablero tiene al menos una solución válida.
        Retorna True si la solución proporcionada es válida, False en caso contrario.
        """
        self.puzzle_grid = self._cargar_grid_desde_txt(puzzle_filepath)
        self.solucion_grid = self._cargar_grid_desde_txt(solucion_filepath)

        es_valida = False
        if self.puzzle_grid and self.solucion_grid:
            if self._validar_integridad_ruta() and self._validar_restricciones_puzzle():
                print("La solución es válida para el puzzle proporcionado")
                es_valida = True

        # Siempre reportar si el tablero tiene al menos una solución (vía backtracking)
        if verificar_existencia:
            if self.tiene_solucion(puzzle_filepath):
                print("El tablero tiene al menos una solución válida")
            else:
                print("El tablero no tiene solución válida")

        return es_valida

if __name__ == "__main__":
    validador = ValidadorPuzzleRuta(tamano=4)
    validador.validar("numari_deybby/tablero.txt", "numari_deybby/solucion.txt")
