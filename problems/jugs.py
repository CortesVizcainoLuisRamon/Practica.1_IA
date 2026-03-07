"""
Problema B: El Problema de las Jarras
Estado = (jarra_a, jarra_b), capacidades configurables.
"""
from typing import List, Tuple
from algorithms.search import bfs, dfs, SearchResult


JugState = Tuple[int, int]   # (litros_en_a, litros_en_b)


def jug_expand(cap_a: int, cap_b: int):
    """Genera los 6 movimientos posibles desde un estado de jarras."""
    def expand(state: JugState) -> List[JugState]:
        a, b = state
        succs = []

        # 1. Llenar A
        if a < cap_a:
            succs.append((cap_a, b))
        # 2. Llenar B
        if b < cap_b:
            succs.append((a, cap_b))
        # 3. Vaciar A
        if a > 0:
            succs.append((0, b))
        # 4. Vaciar B
        if b > 0:
            succs.append((a, 0))
        # 5. Verter A → B
        if a > 0 and b < cap_b:
            pour = min(a, cap_b - b)
            succs.append((a - pour, b + pour))
        # 6. Verter B → A
        if b > 0 and a < cap_a:
            pour = min(b, cap_a - a)
            succs.append((a + pour, b - pour))

        return succs
    return expand


def solve_jugs(
    cap_a: int,
    cap_b: int,
    target: int,
    algorithm: str = "bfs",
) -> SearchResult:
    """
    Resuelve el problema de las jarras.

    Args:
        cap_a:    Capacidad de la jarra A.
        cap_b:    Capacidad de la jarra B.
        target:   Cantidad de agua que se desea medir.
        algorithm: 'bfs' o 'dfs'.
    """
    start: JugState = (0, 0)
    goal_fn = lambda s: s[0] == target or s[1] == target
    expand = jug_expand(cap_a, cap_b)

    if algorithm == "bfs":
        return bfs(start, goal_fn, expand)
    else:
        return dfs(start, goal_fn, expand)


# ─── Formatea el camino de solución ───────────
def format_jug_path(path: List[JugState], cap_a: int, cap_b: int) -> str:
    lines = [f"  {'Paso':>5}  │  Jarra A ({cap_a}L)  │  Jarra B ({cap_b}L)"]
    lines.append("  " + "─" * 38)
    for i, (a, b) in enumerate(path):
        lines.append(f"  {i:>5}  │  {a:>13}  │  {b:>10}")
    return "\n".join(lines)
