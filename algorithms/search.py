"""
Algoritmos de Búsqueda Ciega: DFS y BFS
Incluye medición de tiempo y memoria.
"""
import time
import tracemalloc
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple


@dataclass
class SearchResult:
    """Resultado de una búsqueda."""
    path: List[Any]
    nodes_visited: int
    time_ms: float
    memory_kb: float
    found: bool
    algorithm: str


def measure(func):
    """Decorador para medir tiempo y memoria."""
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # Adjuntar métricas al resultado si es SearchResult
        if isinstance(result, SearchResult):
            result.time_ms = round(elapsed, 3)
            result.memory_kb = round(peak / 1024, 2)
        return result
    return wrapper


# ─────────────────────────────────────────────
#  BFS  — Búsqueda en Amplitud
# ─────────────────────────────────────────────
@measure
def bfs(
    start: Any,
    goal_fn: Callable[[Any], bool],
    expand_fn: Callable[[Any], List[Any]],
    state_key: Callable[[Any], Any] = lambda s: s,
) -> SearchResult:
    """
    Búsqueda en Amplitud (BFS).
    Garantiza el camino más corto en grafos sin peso.

    Args:
        start:      Estado inicial.
        goal_fn:    Función que retorna True si el estado es meta.
        expand_fn:  Función que retorna los estados sucesores.
        state_key:  Función para obtener una clave hashable del estado.
    """
    queue: deque = deque()
    queue.append((start, [start]))
    visited = {state_key(start)}
    nodes_visited = 0

    while queue:
        state, path = queue.popleft()
        nodes_visited += 1

        if goal_fn(state):
            return SearchResult(
                path=path,
                nodes_visited=nodes_visited,
                time_ms=0, memory_kb=0,
                found=True, algorithm="BFS"
            )

        for neighbor in expand_fn(state):
            key = state_key(neighbor)
            if key not in visited:
                visited.add(key)
                queue.append((neighbor, path + [neighbor]))

    return SearchResult(
        path=[], nodes_visited=nodes_visited,
        time_ms=0, memory_kb=0,
        found=False, algorithm="BFS"
    )


# ─────────────────────────────────────────────
#  DFS  — Búsqueda en Profundidad
# ─────────────────────────────────────────────
@measure
def dfs(
    start: Any,
    goal_fn: Callable[[Any], bool],
    expand_fn: Callable[[Any], List[Any]],
    state_key: Callable[[Any], Any] = lambda s: s,
    max_depth: int = 10_000,
) -> SearchResult:
    """
    Búsqueda en Profundidad (DFS) iterativa.
    Usa pila explícita para evitar recursión profunda.

    Args:
        start:      Estado inicial.
        goal_fn:    Función que retorna True si el estado es meta.
        expand_fn:  Función que retorna los estados sucesores.
        state_key:  Función para obtener una clave hashable del estado.
        max_depth:  Profundidad máxima de búsqueda.
    """
    stack: List = [(start, [start], 0)]
    visited = {state_key(start)}
    nodes_visited = 0

    while stack:
        state, path, depth = stack.pop()
        nodes_visited += 1

        if goal_fn(state):
            return SearchResult(
                path=path,
                nodes_visited=nodes_visited,
                time_ms=0, memory_kb=0,
                found=True, algorithm="DFS"
            )

        if depth < max_depth:
            for neighbor in expand_fn(state):
                key = state_key(neighbor)
                if key not in visited:
                    visited.add(key)
                    stack.append((neighbor, path + [neighbor], depth + 1))

    return SearchResult(
        path=[], nodes_visited=nodes_visited,
        time_ms=0, memory_kb=0,
        found=False, algorithm="DFS"
    )
