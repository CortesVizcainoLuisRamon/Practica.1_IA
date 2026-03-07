"""
Problema C: El 8-Puzzle
Estado = tupla de 9 enteros (0 = espacio vacío).
"""
from typing import List, Tuple, Optional
from algorithms.search import bfs, dfs, SearchResult


PuzzleState = Tuple[int, ...]

GOAL_STATE: PuzzleState = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Movimientos del hueco: arriba, abajo, izquierda, derecha
MOVES = {
    "up":    -3,
    "down":  +3,
    "left":  -1,
    "right": +1,
}


def is_solvable(state: PuzzleState) -> bool:
    """
    Un 8-puzzle es resoluble si el número de inversiones es par.
    (Inversión: par (i,j) donde i<j pero state[i]>state[j], ignorando el 0)
    """
    tiles = [x for x in state if x != 0]
    inversions = sum(
        1
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )
    return inversions % 2 == 0


def puzzle_expand(state: PuzzleState) -> List[PuzzleState]:
    """Genera los estados sucesores moviendo el hueco."""
    blank = state.index(0)
    row, col = divmod(blank, 3)
    neighbors = []

    if row > 0:  # mover arriba
        new = list(state); new[blank], new[blank - 3] = new[blank - 3], new[blank]
        neighbors.append(tuple(new))
    if row < 2:  # mover abajo
        new = list(state); new[blank], new[blank + 3] = new[blank + 3], new[blank]
        neighbors.append(tuple(new))
    if col > 0:  # mover izquierda
        new = list(state); new[blank], new[blank - 1] = new[blank - 1], new[blank]
        neighbors.append(tuple(new))
    if col < 2:  # mover derecha
        new = list(state); new[blank], new[blank + 1] = new[blank + 1], new[blank]
        neighbors.append(tuple(new))

    return neighbors


def solve_puzzle(
    initial: PuzzleState,
    goal: PuzzleState = GOAL_STATE,
    algorithm: str = "bfs",
) -> SearchResult:
    """
    Resuelve el 8-puzzle con DFS o BFS.
    DFS tiene límite de profundidad de 50 para evitar bucles.
    """
    if not is_solvable(initial):
        from algorithms.search import SearchResult
        return SearchResult(
            path=[], nodes_visited=0,
            time_ms=0, memory_kb=0,
            found=False, algorithm=algorithm.upper()
        )

    goal_fn = lambda s: s == goal

    if algorithm == "bfs":
        return bfs(initial, goal_fn, puzzle_expand)
    else:
        return dfs(initial, goal_fn, puzzle_expand, max_depth=50)


# ─── Utilidades de visualización ─────────────
def format_puzzle(state: PuzzleState) -> str:
    lines = ["┌───┬───┬───┐"]
    for row in range(3):
        cells = []
        for col in range(3):
            v = state[row * 3 + col]
            cells.append(f" {v if v != 0 else ' '} ")
        lines.append("│" + "│".join(cells) + "│")
        if row < 2:
            lines.append("├───┼───┼───┤")
    lines.append("└───┴───┴───┘")
    return "\n".join(lines)


# ─── Configuraciones de ejemplo ───────────────
EASY_PUZZLE:   PuzzleState = (1, 2, 3, 4, 5, 6, 0, 7, 8)
MEDIUM_PUZZLE: PuzzleState = (1, 2, 3, 4, 0, 6, 7, 5, 8)
HARD_PUZZLE:   PuzzleState = (8, 6, 7, 2, 5, 4, 3, 0, 1)
