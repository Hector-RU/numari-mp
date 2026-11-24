# Numari

Numari es un rompecabezas de terminal escrito en Python. El objetivo es recorrer todas las casillas del tablero con una ruta continua, sin repetir casillas. Empiezas en una casilla numerada. Su número indica cuántas casillas vacías debes atravesar antes de llegar a otra casilla numerada. Si ves un 0, la siguiente casilla debe estar numerada.

## Instalación y ejecución

Necesitas Windows y Python 3.10 o posterior. Abre una terminal en la raíz del proyecto y ejecuta:

```powershell
python -m pip install keyboard
python numari.py
```

## Cómo jugar

1. En el menú principal, elige **Juego aleatorio** y selecciona un tablero de **4 × 4**, **5 × 5** o **6 × 6**.
2. Vuelve al menú principal y elige **Reanudar Juego** para abrir el tablero generado.
3. Selecciona una casilla numerada para empezar. Recorre el tablero hasta visitar todas las casillas.

| Pantalla | Teclas |
| --- | --- |
| Menús | `W` y `S` para subir y bajar. `Enter` para confirmar. |
| Casilla inicial | `A` y `D` para cambiar de casilla. `Enter` para empezar. `Esc` para salir. |
| Partida | `W`, `A`, `S` y `D` para moverte. Para deshacer un paso, vuelve a la casilla anterior. `C` para reiniciar el recorrido y elegir otra casilla inicial. `Esc` para salir del tablero. |

## Archivos principales

- `numari.py` abre el menú principal y gestiona la selección del tablero.
- `numari_board.py` muestra el tablero y valida los movimientos.
- `generador_tablero.py` genera los rompecabezas aleatorios.
- `menu.py`, `control.py` y `color.py` gestionan los menús, la lectura del teclado y los colores de la terminal.
