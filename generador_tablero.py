import random

class GeneradorPuzzleRuta:
    """
    Genera un puzzle de tamaño × tamaño con una ruta de solución y
    números que definen la longitud de los segmentos del camino.
    """
    def __init__(self, tamano=4):
        self.tamano = tamano
        self.total_casillas = tamano * tamano
        self.grid = [[0] * tamano for _ in range(tamano)]

    def _generar_ruta_completa(self):
        """
        Usa backtracking para encontrar un camino Hamiltoniano aleatorio
        en la cuadrícula (una ruta que visita cada casilla exactamente una vez).

        Devuelve un diccionario {número_de_paso: (x, y)} o None si no se
        encontró ningún camino desde la casilla inicial elegida.
        """
        mapa_ruta = {}
        visitadas = set()

        def backtrack(x, y, contador):
            if contador > self.total_casillas:
                return True
            if not (0 <= x < self.tamano and 0 <= y < self.tamano and (x, y) not in visitadas):
                return False

            visitadas.add((x, y))
            mapa_ruta[contador] = (x, y)
            direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(direcciones)

            for dx, dy in direcciones:
                if backtrack(x + dx, y + dy, contador + 1):
                    return True

            visitadas.remove((x, y))
            return False

        x_inicio, y_inicio = random.randint(0, self.tamano-1), random.randint(0, self.tamano-1)
        if backtrack(x_inicio, y_inicio, 1):
            return mapa_ruta
        else:
            return None

    def _particionar_ruta(self):
        """
        Genera una lista de longitudes aleatorias entre 1 y 5 cuya suma es
        el total de casillas del tablero (tamaño × tamaño).

        Cada longitud L se muestra en el tablero como el número L - 1.
        """
        particion = []
        suma_actual = 0
        while suma_actual < self.total_casillas:
            restante = self.total_casillas - suma_actual
            max_valor = min(5, restante)
            
            # Garantiza que cada longitud sea al menos 1
            if max_valor <= 0: break
            min_valor = 1
            
            longitud = random.randint(min_valor, max_valor)
            
            particion.append(longitud)
            suma_actual += longitud
        
        random.shuffle(particion)
        return particion

    def generar_puzzle(self):
        """
        Orquesta la generación del puzzle y su solución.

        Devuelve una tupla (puzzle_grid, solucion_grid), o (None, None) si no
        se pudo generar un camino Hamiltoniano.
        """
        mapa_ruta_solucion = self._generar_ruta_completa()
        if not mapa_ruta_solucion:
            # print("Error: No se pudo generar una ruta válida.")
            return None, None

        particion_longitudes = self._particionar_ruta()

        puzzle_grid = [[0] * self.tamano for _ in range(self.tamano)]
        indice_ruta = 1
        for longitud in particion_longitudes:
            x, y = mapa_ruta_solucion[indice_ruta]
            puzzle_grid[x][y] = longitud
            indice_ruta += longitud

        solucion_grid = [[0] * self.tamano for _ in range(self.tamano)]
        for numero_paso, coords in mapa_ruta_solucion.items():
            x, y = coords
            solucion_grid[x][y] = numero_paso
            
        return puzzle_grid, solucion_grid

    @staticmethod
    def imprimir_tablero(tablero, titulo=""):
        """Imprime un tablero de forma clara."""
        print(titulo)
        if not tablero:
            return
        for fila in tablero:
            print("  ".join(f"{str(celda):>2}" for celda in fila))
        print()

# --- Ejecución del código ---
if __name__ == "__main__":
    generador = GeneradorPuzzleRuta(tamano=4)
    puzzle, solucion = generador.generar_puzzle()
    
    if puzzle and solucion:
        puzzle_visual = [['X' if celda == 0 else str(celda - 1) for celda in fila] for fila in puzzle]
        
        GeneradorPuzzleRuta.imprimir_tablero(puzzle_visual, "\n--- PUZZLE GENERADO ---")
        GeneradorPuzzleRuta.imprimir_tablero(solucion, "--- RUTA ÚNICA DE SOLUCIÓN ---")
    
    
    
