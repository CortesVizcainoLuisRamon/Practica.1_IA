"""
Tests unitarios para DFS, BFS y los tres problemas.
Ejecutar con: python -m pytest tests/test_algorithms.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from algorithms.search import bfs, dfs
from problems.maze import generate_maze, solve_maze, get_start_goal
from problems.jugs import solve_jugs
from problems.puzzle import (
    solve_puzzle, is_solvable,
    EASY_PUZZLE, MEDIUM_PUZZLE, HARD_PUZZLE, GOAL_STATE
)


# ─── Tests de Laberinto ───────────────────────
class TestMaze:
    @pytest.mark.parametrize("size", [10, 20])
    @pytest.mark.parametrize("algo", ["bfs", "dfs"])
    def test_maze_finds_path(self, size, algo):
        maze = generate_maze(size, size, seed=7)
        result = solve_maze(maze, algo)
        assert result.found, f"{algo.upper()} no encontró solución en {size}x{size}"

    @pytest.mark.parametrize("algo", ["bfs", "dfs"])
    def test_path_is_valid(self, algo):
        size = 10
        maze = generate_maze(size, size, seed=1)
        result = solve_maze(maze, algo)
        start, goal = get_start_goal(maze)
        assert result.path[0] == start
        assert result.path[-1] == goal

    def test_bfs_optimal_path(self):
        """BFS debe encontrar el camino más corto."""
        maze = generate_maze(10, 10, seed=42)
        res_bfs = solve_maze(maze, "bfs")
        res_dfs = solve_maze(maze, "dfs")
        # BFS siempre <= DFS en longitud de camino
        assert len(res_bfs.path) <= len(res_dfs.path)

    def test_metrics_recorded(self):
        maze = generate_maze(10, 10)
        result = solve_maze(maze, "bfs")
        assert result.time_ms >= 0
        assert result.memory_kb >= 0
        assert result.nodes_visited > 0


# ─── Tests de Jarras ─────────────────────────
class TestJugs:
    @pytest.mark.parametrize("cap_a,cap_b,target", [
        (3, 5, 4),
        (2, 5, 1),
        (3, 7, 5),
    ])
    @pytest.mark.parametrize("algo", ["bfs", "dfs"])
    def test_jugs_classic(self, cap_a, cap_b, target, algo):
        result = solve_jugs(cap_a, cap_b, target, algo)
        assert result.found
        last = result.path[-1]
        assert last[0] == target or last[1] == target

    def test_jugs_impossible(self):
        """Si el target no es alcanzable, no debe encontrar solución."""
        # 6L con jarras de 4 y 2 → posible (múltiplo de gcd)
        # Jarras de 4 y 6, target 3 → imposible (gcd=2)
        result = solve_jugs(4, 6, 3, "bfs")
        assert not result.found

    def test_jugs_start_is_zero(self):
        result = solve_jugs(3, 5, 4, "bfs")
        assert result.path[0] == (0, 0)


# ─── Tests de 8-Puzzle ───────────────────────
class TestPuzzle:
    def test_easy_puzzle_bfs(self):
        result = solve_puzzle(EASY_PUZZLE, algorithm="bfs")
        assert result.found
        assert result.path[-1] == GOAL_STATE

    def test_easy_puzzle_dfs(self):
        result = solve_puzzle(EASY_PUZZLE, algorithm="dfs")
        assert result.found

    def test_medium_puzzle_bfs(self):
        result = solve_puzzle(MEDIUM_PUZZLE, algorithm="bfs")
        assert result.found

    def test_unsolvable_puzzle(self):
        unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        assert not is_solvable(unsolvable)
        result = solve_puzzle(unsolvable, algorithm="bfs")
        assert not result.found

    def test_is_solvable(self):
        assert is_solvable(EASY_PUZZLE)
        assert is_solvable(MEDIUM_PUZZLE)

    def test_bfs_finds_optimal(self):
        """BFS garantiza el camino más corto."""
        result = solve_puzzle(EASY_PUZZLE, algorithm="bfs")
        # EASY_PUZZLE está a 2 pasos del goal
        assert len(result.path) <= 5


# ─── Tests de Algoritmos Base ─────────────────
class TestAlgorithms:
    """Prueba DFS y BFS con un grafo simple."""

    def setup_method(self):
        # Grafo: 0-1-2-3-4 (lineal)
        self.graph = {i: [i+1] for i in range(4)}
        self.graph[4] = []
        self.expand = lambda n: self.graph.get(n, [])

    def test_bfs_finds_goal(self):
        result = bfs(0, lambda n: n == 4, self.expand)
        assert result.found
        assert result.path == [0, 1, 2, 3, 4]

    def test_dfs_finds_goal(self):
        result = dfs(0, lambda n: n == 4, self.expand)
        assert result.found
        assert result.path[-1] == 4

    def test_bfs_no_path(self):
        result = bfs(0, lambda n: n == 99, self.expand)
        assert not result.found

    def test_dfs_no_path(self):
        result = dfs(0, lambda n: n == 99, self.expand)
        assert not result.found
