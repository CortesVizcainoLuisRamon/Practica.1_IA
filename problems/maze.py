"""
Problema A: Laberintos
Generación aleatoria y resolución con DFS/BFS.
"""
import random
from typing import List, Tuple
from algorithms.search import bfs, dfs, SearchResult


# ─── Tipos ───────────────────────────────────
Cell = Tuple[int, int]   # (fila, columna)
Maze = List[List[int]]   # 0=libre, 1=pared


# ─── Generación de Laberintos ─────────────────
def generate_maze(rows: int, cols: int, seed: int = 42) -> Maze:
    """
    Genera un laberinto usando el algoritmo de Recursive Backtracker.
    Garantiza que siempre haya solución.
    """
    rng = random.Random(seed)
    # Empezar todo como paredes
    maze = [[1] * cols for _ in range(rows)]

    def carve(r: int, c: int):
        maze[r][c] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        rng.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1:
                maze[r + dr // 2][c + dc // 2] = 0  # eliminar pared entre celdas
                carve(nr, nc)

    import sys
    sys.setrecursionlimit(rows * cols * 2 + 1000)
    carve(1, 1)

    # Asegurar entrada y salida
    maze[1][0] = 0           # entrada izquierda
    maze[rows - 2][cols - 1] = 0   # salida derecha
    return maze


def get_start_goal(maze: Maze) -> Tuple[Cell, Cell]:
    rows = len(maze)
    cols = len(maze[0])
    return (1, 0), (rows - 2, cols - 1)


# ─── Funciones de Expansión ───────────────────
def maze_expand(maze: Maze):
    rows = len(maze)
    cols = len(maze[0])
    def expand(cell: Cell):
        r, c = cell
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                neighbors.append((nr, nc))
        return neighbors
    return expand


# ─── Resolver Laberinto ───────────────────────
def solve_maze(maze: Maze, algorithm: str = "bfs") -> SearchResult:
    start, goal = get_start_goal(maze)
    expand = maze_expand(maze)
    goal_fn = lambda cell: cell == goal

    if algorithm == "bfs":
        return bfs(start, goal_fn, expand)
    else:
        return dfs(start, goal_fn, expand)


# ─── Helper: imprimir laberinto en consola ────
def print_maze(maze: Maze, path: List[Cell] = None):
    path_set = set(path) if path else set()
    for r, row in enumerate(maze):
        line = ""
        for c, cell in enumerate(row):
            if (r, c) in path_set:
                line += "· "
            elif cell == 1:
                line += "█ "
            else:
                line += "  "
        print(line)
