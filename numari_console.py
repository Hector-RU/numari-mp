import os, sys, time, copy

# ---------- Entrada de una tecla (sin Enter) ----------
def _getch():
    try:
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            return {b'H':'w', b'P':'s', b'K':'a', b'M':'d'}.get(ch2, '')
        return ch.decode('utf-8', errors='ignore')
    except ImportError:
        import termios, tty
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd); ch = sys.stdin.read(1)
            if ch == '\x1b' and sys.stdin.read(1) == '[':
                return {'A':'w','B':'s','D':'a','C':'d'}.get(sys.stdin.read(1), '')
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

# ---------- Colores ----------
class Color:
    RESET='\033[0m'; DIM='\033[2m'; BOLD='\033[1m'
    CYAN='\033[36m'; GREEN='\033[32m'; RED='\033[31m'
    YELLOW='\033[33m'; MAGENTA='\033[35m'; GRAY='\033[90m'

VACIO_SIMBOLO = '□'; CHECK_SIMBOLO = '✓'; X_SIMBOLO = 'x'

# ======================================================
#                       TABLERO
# ======================================================
class Tablero:
    def __init__(self, grid_numeros):
        self.n = len(grid_numeros)
        self.grid_numeros = grid_numeros  # int|None
        self.grid_base_marca = [['EMPTY' for _ in range(self.n)] for _ in range(self.n)]
        self.grid_marca = copy.deepcopy(self.grid_base_marca)
        self.movimientos = 0
        self.caminos = {}

    # --------- Carga desde .txt ---------
    @staticmethod
    def cargar_desde_txt(path='tablero.txt'):
        if not os.path.exists(path):
            ejemplo = ["C 4 C C","C C C 2","3 C C C","C C C 3"]
            with open(path, 'w', encoding='utf-8') as f: f.write('\n'.join(ejemplo))
        grid = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'): continue
                fila=[]
                for tok in line.split():
                    fila.append(None if tok.upper()=='C' else int(tok))
                grid.append(fila)
        n=len(grid)
        if any(len(f)!=n for f in grid): raise ValueError("El tablero debe ser cuadrado.")
        return Tablero(grid)

    # --------- Validación de tablero básico ---------
    def validar(self):
        n=self.n; llenas=0; vacios=0
        for r in range(n):
            for c in range(n):
                v=self.grid_numeros[r][c]
                if v is None: vacios+=1
                else:
                    if v<0 or v>4: return (False,f"Valor fuera de [0..4] en ({r},{c}): {v}")
                    if v>0: llenas+=1
        if not (4<=llenas<=6): return (False, f"Celdas con número en [4..6], actual {llenas}.")
        dirs=[(1,0),(-1,0),(0,1),(0,-1)]
        for r in range(n):
            for c in range(n):
                v=self.grid_numeros[r][c]
                if v and v>0:
                    for dr,dc in dirs:
                        rr,cc=r+dr,c+dc
                        if 0<=rr<n and 0<=cc<n and self.grid_numeros[rr][cc] and self.grid_numeros[rr][cc]>0:
                            return (False,"Dos números adyacentes ortogonalmente no están permitidos.")
        suma = sum(self.grid_numeros[r][c] or 0 for r in range(n) for c in range(n))
        if suma != vacios: return (True, f"ADVERTENCIA: suma números {suma} != vacíos {vacios}.")
        return (True,"Tablero válido.")

    # --------- Estado ---------
    def esta_resuelto(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.grid_numeros[r][c] is None and self.grid_marca[r][c] != 'CHECK':
                    return False
        return True

    def reset_jugadas(self):
        self.grid_marca = copy.deepcopy(self.grid_base_marca)
        self.caminos.clear()

    def reset_total(self):
        self.reset_jugadas(); self.movimientos=0

    # --------- Utilidades ---------
    def vecinos_num(self, r, c, excluir=None):
        dirs=[(1,0),(-1,0),(0,1),(0,-1)]; res=[]
        for dr,dc in dirs:
            rr,cc=r+dr,c+dc
            if 0<=rr<self.n and 0<=cc<self.n:
                if self.grid_numeros[rr][cc] is not None and (excluir is None or (rr,cc)!=excluir):
                    res.append((rr,cc))
        return res

    def numero_tiene_jugada(self, rc_num):
        return rc_num in self.caminos

    def endpoints(self):
        pts=set()
        for rc, path in self.caminos.items():
            pts.add(path[-1] if len(path)>0 else rc)
        return pts

    def num_adyacente_a_endpoint(self, rc_num):
        r,c = rc_num
        for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            rr,cc=r+dr,c+dc
            if (rr,cc) in self.endpoints():
                return True
        return False

    # --------- Render ---------
    def render(self, cursor=(0,0), info="", en_seleccion=None, pasos_restantes=None):
        clear()
        print(f"{Color.BOLD}NUMARI (consola){Color.RESET}  —  Movimientos: {Color.MAGENTA}{self.movimientos}{Color.RESET}")
        print("W/A/S/D o Flechas • [Espacio/Enter]=iniciar/confirmar • c=cancelar • r=reestablecer ✓ • R=reiniciar todo • h=ayuda • q=salir")
        if info: print(info)
        print()
        for r in range(self.n):
            fila=[]
            for c in range(self.n):
                cur=(r==cursor[0] and c==cursor[1])
                num=self.grid_numeros[r][c]; marca=self.grid_marca[r][c]
                if num is not None:
                    text = str(num)
                    if self.numero_tiene_jugada((r, c)):
                        color = Color.GREEN + Color.BOLD
                    else:
                        color = Color.CYAN + Color.BOLD
                else:
                    if marca == 'CHECK':
                        text = CHECK_SIMBOLO; color = Color.GREEN + Color.BOLD
                    elif marca == 'PATH':
                        text = VACIO_SIMBOLO; color = Color.YELLOW + Color.BOLD
                    elif marca == 'X':
                        text = X_SIMBOLO; color = Color.RED + Color.BOLD
                    else:
                        text = VACIO_SIMBOLO; color = Color.DIM
                contenido=f"[{text}]" if cur else f" {text} "
                fila.append(color+contenido+Color.RESET)
            print("".join(fila))
        if en_seleccion is not None:
            print(f"\nSelección: número {en_seleccion} — pasos restantes: {pasos_restantes}")
        print()

# ======================================================
#                     MOVIMIENTO
# ======================================================
class Movimiento:
    """
    Intento/edición de un camino:
      - Soporta retroceso: mover a la casilla previa elimina el último paso (incluye volver al número).
      - Si se edita una jugada válida, se inicializa con camino existente (para 0 es lista vacía).
    """
    def __init__(self, tablero: Tablero, start_rc, initial_camino=None, committed_anterior=None):
        self.tablero = tablero
        self.start = start_rc
        self.n = tablero.grid_numeros[start_rc[0]][start_rc[1]]
        self.camino = list(initial_camino) if initial_camino else []
        self.committed_anterior = list(committed_anterior) if committed_anterior is not None else None
        for r,c in self.camino:
            self.tablero.grid_marca[r][c] = 'PATH'

    def pasos_pendientes(self):
        return self.n - len(self.camino)

    def _es_valida_siguiente(self, r, c):
        n=self.tablero.n
        if not (0<=r<n and 0<=c<n): return False, "Fuera del tablero."
        if self.tablero.grid_numeros[r][c] is not None: return False, "No puedes pisar números."
        if self.tablero.grid_marca[r][c] == 'CHECK': return False, "No puedes atravesar ✓ de otros caminos."
        if (r,c) in self.camino and (len(self.camino)<2 or (r,c)!=self.camino[-2]):
            return False, "No puedes formar bucles (solo puedes volver a la casilla anterior)."
        return True,""

    def _head(self):
        return self.camino[-1] if self.camino else self.start

    def intentar_paso(self, direccion):
        """Añade un paso o deshace el anterior si te mueves hacia atrás."""
        mov = {'w': (-1,0), 's': (1,0), 'a': (0,-1), 'd': (0,1)}.get(direccion)
        if not mov: return False, "Dirección inválida.", self._head()

        base_r, base_c = self._head()
        r, c = base_r + mov[0], base_c + mov[1]

        # --- Retroceso: a la casilla anterior ---
        if len(self.camino) >= 2 and (r,c) == self.camino[-2]:
            pr, pc = self.camino.pop()
            if self.tablero.grid_marca[pr][pc]=='PATH': self.tablero.grid_marca[pr][pc]='EMPTY'
            return True, "Paso deshecho.", self._head()

        # --- Retroceso del primer paso hacia el número inicial ---
        if len(self.camino) == 1 and (r,c) == self.start:
            pr, pc = self.camino.pop()
            if self.tablero.grid_marca[pr][pc]=='PATH': self.tablero.grid_marca[pr][pc]='EMPTY'
            return True, "Paso deshecho.", self._head()

        # --- Paso hacia adelante ---
        if self.pasos_pendientes() <= 0:
            return False, "Ya completaste la cantidad de pasos.", self._head()

        ok,msg = self._es_valida_siguiente(r, c)
        if not ok: return False, msg, self._head()

        self.camino.append((r,c))
        self.tablero.grid_marca[r][c] = 'PATH'
        return True, "", (r,c)

    def _validar_final(self):
        # ----- Caso especial: n == 0 (cero) -----
        if self.n == 0:
            vecinos = self.tablero.vecinos_num(self.start[0], self.start[1], excluir=self.start)
            if any(not self.tablero.numero_tiene_jugada(rc) for rc in vecinos):
                return True, ""

            # Excepción: permitir si al marcar 0 se completa la partida
            if self.tablero.esta_resuelto():
                return True, ""

            return False, "El 0 solo se puede marcar si toca un número sin jugada válida o si con ello se termina la partida."

        # ----- Resto de números (n > 0) -----
        if len(self.camino) != self.n:
            return False, f"Debes recorrer exactamente {self.n} casillas."
        fin = self.camino[-1]
        vecinos = self.tablero.vecinos_num(fin[0], fin[1], excluir=self.start)
        if not vecinos:
            return False, "La última casilla debe quedar adyacente a otro número."

        # Válido si toca al menos un número SIN jugada
        if any(not self.tablero.numero_tiene_jugada(rc) for rc in vecinos):
            return True, ""

        # Excepción: solo toca números con jugada, pero esta jugada completa el tablero
        total_vacios = sum(
            1 for r in range(self.tablero.n) for c in range(self.tablero.n)
            if self.tablero.grid_numeros[r][c] is None
        )
        check_ahora = sum(
            1 for r in range(self.tablero.n) for c in range(self.tablero.n)
            if self.tablero.grid_marca[r][c] == 'CHECK'
        )
        vacios_restantes_despues = total_vacios - (check_ahora + len(self.camino))
        if vacios_restantes_despues == 0:
            return True, ""

        return False, "Esta jugada solo conecta con números ya resueltos y no completa el tablero."

    def confirmar(self):
        self.tablero.movimientos += 1

        # Revertir jugada: si estoy editando y regresé al número (camino vacío)
        if self.committed_anterior is not None and len(self.camino) == 0:
            if self.start in self.tablero.caminos:
                del self.tablero.caminos[self.start]
            # Asegurar que cualquier PATH quede limpio
            for r in range(self.tablero.n):
                for c in range(self.tablero.n):
                    if self.tablero.grid_marca[r][c] == 'PATH':
                        self.tablero.grid_marca[r][c] = 'EMPTY'
            return True, "Jugada revertida."

        ok,msg = self._validar_final()
        if not ok: return self._flash_error(msg)

        if self.n == 0:
            self.tablero.caminos[self.start] = []
            return True, "Cero confirmado."
        else:
            for r,c in self.camino:
                self.tablero.grid_marca[r][c]='CHECK'
            self.tablero.caminos[self.start] = list(self.camino)
            return True, "Camino válido."

    def cancelar(self):
        for r,c in self.camino:
            if self.tablero.grid_marca[r][c]=='PATH': self.tablero.grid_marca[r][c]='EMPTY'
        if self.committed_anterior is not None:
            for r,c in self.committed_anterior:
                self.tablero.grid_marca[r][c]='CHECK'
        self.camino.clear()

    def _flash_error(self, mensaje):
        for r,c in self.camino:
            self.tablero.grid_marca[r][c]='X'
        self.tablero.render(info=f"{Color.RED}{mensaje}{Color.RESET}")
        time.sleep(0.8)
        for r,c in self.camino:
            self.tablero.grid_marca[r][c]='EMPTY'
        if self.committed_anterior is not None:
            for r,c in self.committed_anterior:
                self.tablero.grid_marca[r][c]='CHECK'
        self.camino.clear()
        return False, mensaje

# ======================================================
#                        JUEGO
# ======================================================
class Juego:
    def __init__(self, tablero: Tablero):
        self.tablero = tablero
        self.cursor = [0,0]
        self.mov_actual = None

    def dentro(self, r,c): return 0<=r<self.tablero.n and 0<=c<self.tablero.n
    def mover_cursor(self, dr,dc):
        r,c=self.cursor; r+=dr; c+=dc
        if self.dentro(r,c): self.cursor=[r,c]

    def _puedo_iniciar_en(self, rc_num):
        """Si ya hay caminos ✓, el nuevo número debe tocar algún endpoint (editar siempre permitido)."""
        if self.tablero.numero_tiene_jugada(rc_num):
            return True
        if not self.tablero.caminos:
            return True
        return self.tablero.num_adyacente_a_endpoint(rc_num)

    def run(self):
        ok,msg = self.tablero.validar()
        info = msg if ok else (Color.RED+msg+Color.RESET)
        while True:
            en_sel = self.mov_actual.n if self.mov_actual else None
            pasos_rest = self.mov_actual.pasos_pendientes() if self.mov_actual else None
            if self.mov_actual:
                head = self.mov_actual._head()
                self.cursor = [head[0], head[1]]
            self.tablero.render(tuple(self.cursor), info=info, en_seleccion=en_sel, pasos_restantes=pasos_rest)
            if self.tablero.esta_resuelto():
                print(f"{Color.GREEN}{Color.BOLD}¡Felicidades! Resolviste el tablero en {self.tablero.movimientos} movimientos.{Color.RESET}")
                print("Pulsa 'R' para reiniciar, o 'q' para salir.")
            info=""

            ch=_getch().lower()
            if ch in ('q','\x03','\x1b'): clear(); return
            if ch=='h':
                info=("Reglas: selecciona un número (incluye 0) y recorre EXACTAMENTE su cantidad de casillas vacías.\n"
                      "- Cero (0): se confirma solo si toca un número sin jugada válida,o si al confirmarlo se termina"
                      "la partida.\n"
                      "- Puedes retroceder pasos moviéndote a la casilla anterior; si vuelves al número y confirmas, revertirás la jugada.\n"
                      "- Si ya hay caminos ✓, el siguiente número debe estar pegado a algún endpoint.\n"
                      "- El final debe tocar algún número sin jugada; si solo toca resueltos, solo será válido si completa el tablero.")
                continue

            if ch=='r':
                if self.mov_actual: self.mov_actual.cancelar()
                self.tablero.reset_jugadas(); info="Jugadas reestablecidas."
                continue
            if ch=='r'.upper():
                if self.mov_actual: self.mov_actual.cancelar()
                self.tablero.reset_total(); info="Partida reiniciada."
                continue

            # Movimiento / Paso
            if ch in ('w','a','s','d'):
                if self.mov_actual:
                    ok,msg,_ = self.mov_actual.intentar_paso(ch)
                    if not ok: info = Color.RED+msg+Color.RESET
                else:
                    self.mover_cursor(*{'w':(-1,0),'s':(1,0),'a':(0,-1),'d':(0,1)}[ch])
                continue

            # Seleccionar o confirmar
            if ch in (' ','\r','\n'):
                r,c = self.cursor
                if self.mov_actual is None:
                    num = self.tablero.grid_numeros[r][c]
                    if num is None or num < 0:
                        info = Color.RED+"Debes colocarte sobre un número (0..4)."+Color.RESET
                        continue
                    if not self._puedo_iniciar_en((r,c)):
                        info = Color.RED+"Debes empezar en un número adyacente a la última casilla de algún camino ✓."+Color.RESET
                        continue
                    if self.tablero.numero_tiene_jugada((r,c)):
                        anterior = self.tablero.caminos[(r,c)]
                        for rr,cc in anterior:
                            self.tablero.grid_marca[rr][cc]='PATH'
                        self.mov_actual = Movimiento(self.tablero, (r,c),
                                                     initial_camino=anterior,
                                                     committed_anterior=anterior)
                        head = self.mov_actual._head()
                        self.cursor = [head[0], head[1]]
                        info = f"Editando jugada de {num} casillas (puedes retroceder pasos; confirmar en el número para revertir)."
                    else:
                        self.mov_actual = Movimiento(self.tablero, (r,c))
                        if num == 0:
                            info = "Seleccionaste 0: confirma para marcar 0✓ (no ocupa casillas vacías)."
                        else:
                            info = f"Iniciaste un camino de {num} casillas."
                else:
                    ok,msg = self.mov_actual.confirmar()
                    info = (Color.GREEN if ok else Color.RED)+msg+Color.RESET
                    self.mov_actual = None
                continue

            # Cancelar intento actual
            if ch=='c':
                if self.mov_actual:
                    self.mov_actual.cancelar()
                    self.mov_actual=None
                    info="Intento cancelado."
                continue

# ---------- Entrypoint ----------
def main():
    try:
        tablero = Tablero.cargar_desde_txt('tablero.txt')
    except Exception as e:
        print("Error cargando tablero:", e); return
    Juego(tablero).run()

if __name__ == "__main__":
    main()
