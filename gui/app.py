"""
Interfaz Gráfica — Búsqueda Ciega (DFS y BFS)
Tkinter + Canvas con animaciones paso a paso.
"""
import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional
import random

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.search import bfs, dfs
from problems.maze import generate_maze, solve_maze, get_start_goal
from problems.jugs import solve_jugs, format_jug_path
from problems.puzzle import (
    solve_puzzle, format_puzzle, is_solvable,
    EASY_PUZZLE, MEDIUM_PUZZLE, HARD_PUZZLE, GOAL_STATE,
    PuzzleState
)


# ══════════════════════════════════════════════
#  PALETA DE COLORES
# ══════════════════════════════════════════════
BG        = "#0D1117"
PANEL     = "#161B22"
ACCENT    = "#58A6FF"
ACCENT2   = "#3FB950"
WARN      = "#FF7B72"
TEXT      = "#E6EDF3"
MUTED     = "#8B949E"
WALL      = "#21262D"
PATH_DFS  = "#FF7B72"
PATH_BFS  = "#58A6FF"
VISITED   = "#2D333B"
START_C   = "#3FB950"
GOAL_C    = "#FFD60A"
BORDER    = "#30363D"


# ══════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Búsqueda a ciegas — DFS & BFS")
        self.configure(bg=BG)
        self.geometry("1200x800")
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        # ── Barra lateral ──────────────────────
        sidebar = tk.Frame(self, bg=PANEL, width=260)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="🔍 BÚSQUEDA A\nCIEGAS",
            font=("Courier", 16, "bold"),
            fg=ACCENT, bg=PANEL, justify="center"
        ).pack(pady=(24, 4))

        tk.Label(
            sidebar, text="DFS  ·  BFS",
            font=("Courier", 9),
            fg=MUTED, bg=PANEL
        ).pack(pady=(0, 20))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=16)

        # Botones de sección
        self._nav_buttons = {}
        sections = [
            ("🧩  Laberinto",  "maze"),
            ("🫙  Jarras",     "jugs"),
            ("🔢  8-Puzzle",  "puzzle"),
        ]
        for label, key in sections:
            btn = tk.Button(
                sidebar, text=label,
                font=("Courier", 11),
                fg=TEXT, bg=PANEL,
                activebackground=ACCENT,
                activeforeground=BG,
                relief="flat", anchor="w",
                padx=20, pady=10,
                cursor="hand2",
                command=lambda k=key: self._show_tab(k)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._nav_buttons[key] = btn

        # ── Área principal ──────────────────────
        self._main = tk.Frame(self, bg=BG)
        self._main.pack(side="right", fill="both", expand=True)

        self._tabs = {}
        self._tabs["maze"]   = MazeTab(self._main)
        self._tabs["jugs"]   = JugsTab(self._main)
        self._tabs["puzzle"] = PuzzleTab(self._main)

        self._show_tab("maze")

    def _show_tab(self, key: str):
        for k, frame in self._tabs.items():
            frame.pack_forget()
            self._nav_buttons[k].configure(
                bg=PANEL, fg=TEXT
            )
        self._tabs[key].pack(fill="both", expand=True)
        self._nav_buttons[key].configure(
            bg=ACCENT, fg=BG
        )


# ══════════════════════════════════════════════
#  PESTAÑA: LABERINTO
# ══════════════════════════════════════════════
class MazeTab(tk.Frame):
    SIZES = {"10×10": 10, "20×20": 20, "50×50": 50}

    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._maze = None
        self._cell = 24
        self._anim_speed = 10  # ms por frame
        self._build()

    def _build(self):
        # Controles
        ctrl = tk.Frame(self, bg=PANEL)
        ctrl.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(ctrl, text="Laberinto", font=("Courier", 14, "bold"),
                 fg=ACCENT, bg=PANEL).pack(side="left", padx=12)

        # Tamaño
        tk.Label(ctrl, text="Tamaño:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(20, 4))
        self._size_var = tk.StringVar(value="10×10")
        size_menu = ttk.Combobox(ctrl, textvariable=self._size_var,
                                 values=list(self.SIZES.keys()),
                                 width=7, state="readonly")
        size_menu.pack(side="left")

        # Algoritmo
        tk.Label(ctrl, text="Algoritmo:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(16, 4))
        self._algo_var = tk.StringVar(value="Ambos")
        algo_menu = ttk.Combobox(ctrl, textvariable=self._algo_var,
                                 values=["BFS", "DFS", "Ambos"],
                                 width=7, state="readonly")
        algo_menu.pack(side="left")

        # Velocidad
        tk.Label(ctrl, text="Velocidad:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(16, 4))
        self._speed_var = tk.IntVar(value=20)
        tk.Scale(ctrl, from_=1, to=100, orient="horizontal",
                 variable=self._speed_var, bg=PANEL, fg=TEXT,
                 troughcolor=BG, highlightthickness=0,
                 length=100).pack(side="left")

        # Seed
        self._seed_var = tk.IntVar(value=42)
        tk.Label(ctrl, text="Seed:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(16, 4))
        tk.Entry(ctrl, textvariable=self._seed_var, width=5,
                 bg=WALL, fg=TEXT, insertbackground=TEXT,
                 font=("Courier", 10), relief="flat").pack(side="left")

        tk.Button(ctrl, text="▶  Generar & Resolver",
                  font=("Courier", 10, "bold"),
                  fg=BG, bg=ACCENT, activebackground=ACCENT2,
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self._run).pack(side="right", padx=12)

        # Canvas area
        canvas_frame = tk.Frame(self, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self._canvas_bfs = LabeledCanvas(canvas_frame, "BFS", PATH_BFS)
        self._canvas_bfs.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self._canvas_dfs = LabeledCanvas(canvas_frame, "DFS", PATH_DFS)
        self._canvas_dfs.pack(side="left", fill="both", expand=True)

        # Stats bar
        self._stats = StatsBar(self)
        self._stats.pack(fill="x", padx=16, pady=(0, 12))

    def _run(self):
        size = self.SIZES[self._size_var.get()]
        seed = self._seed_var.get()
        algo = self._algo_var.get()
        speed = max(1, 110 - self._speed_var.get())

        maze = generate_maze(size, size, seed)
        self._maze = maze
        start, goal = get_start_goal(maze)

        cell = max(4, min(30, 480 // size))
        self._cell = cell

        for lc in [self._canvas_bfs, self._canvas_dfs]:
            lc.canvas.config(
                width=size * cell,
                height=size * cell
            )
            lc.draw_maze(maze, cell)

        if algo in ("BFS", "Ambos"):
            res_bfs = solve_maze(maze, "bfs")
        if algo in ("DFS", "Ambos"):
            res_dfs = solve_maze(maze, "dfs")

        def animate_both():
            t1 = threading.Thread(
                target=self._animate,
                args=(self._canvas_bfs, maze, res_bfs.path if algo in ("BFS","Ambos") else [], cell, speed, PATH_BFS),
                daemon=True
            )
            t2 = threading.Thread(
                target=self._animate,
                args=(self._canvas_dfs, maze, res_dfs.path if algo in ("DFS","Ambos") else [], cell, speed, PATH_DFS),
                daemon=True
            )
            if algo in ("BFS", "Ambos"): t1.start()
            if algo in ("DFS", "Ambos"): t2.start()
            if algo in ("BFS", "Ambos"): t1.join()
            if algo in ("DFS", "Ambos"): t2.join()

            stats = {}
            if algo in ("BFS", "Ambos"):
                stats["BFS"] = res_bfs
            if algo in ("DFS", "Ambos"):
                stats["DFS"] = res_dfs
            self.after(0, lambda: self._stats.update(stats))

        threading.Thread(target=animate_both, daemon=True).start()

    def _animate(self, lc, maze, path, cell, speed_ms, color):
        if not path:
            return
        for i, (r, c) in enumerate(path):
            if i == 0 or i == len(path) - 1:
                continue
            self.after(0, lambda r=r, c=c: lc.draw_cell(r, c, cell, color))
            time.sleep(speed_ms / 1000)


class LabeledCanvas(tk.Frame):
    def __init__(self, master, label: str, color: str):
        super().__init__(master, bg=PANEL, relief="flat")
        tk.Label(self, text=label, font=("Courier", 11, "bold"),
                 fg=color, bg=PANEL).pack(pady=6)
        self.canvas = tk.Canvas(self, bg=BG, bd=0,
                                highlightthickness=0)
        self.canvas.pack(padx=8, pady=(0, 8))

    def draw_maze(self, maze, cell):
        self.canvas.delete("all")
        rows, cols = len(maze), len(maze[0])
        start, goal = get_start_goal(maze)
        for r in range(rows):
            for c in range(cols):
                x0, y0 = c * cell, r * cell
                x1, y1 = x0 + cell, y0 + cell
                if (r, c) == start:
                    color = START_C
                elif (r, c) == goal:
                    color = GOAL_C
                elif maze[r][c] == 1:
                    color = WALL
                else:
                    color = BG
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=color, outline=BG, width=1)

    def draw_cell(self, r, c, cell, color):
        x0, y0 = c * cell, r * cell
        x1, y1 = x0 + cell, y0 + cell
        self.canvas.create_rectangle(x0, y0, x1, y1,
                                     fill=color, outline=BG, width=1)


# ══════════════════════════════════════════════
#  PESTAÑA: JARRAS
# ══════════════════════════════════════════════
class JugsTab(tk.Frame):
    PRESETS = {
        "Clásico (3L, 5L → 4L)":  (3, 5, 4),
        "Fácil   (2L, 5L → 1L)":  (2, 5, 1),
        "Difícil (3L, 7L → 5L)":  (3, 7, 5),
        "Grande  (4L, 9L → 6L)":  (4, 9, 6),
    }

    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        ctrl = tk.Frame(self, bg=PANEL)
        ctrl.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(ctrl, text="Problema de las Jarras",
                 font=("Courier", 14, "bold"),
                 fg=ACCENT, bg=PANEL).pack(side="left", padx=12)

        # Preset
        tk.Label(ctrl, text="Preset:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(20, 4))
        self._preset_var = tk.StringVar(value=list(self.PRESETS)[0])
        preset_menu = ttk.Combobox(ctrl, textvariable=self._preset_var,
                                   values=list(self.PRESETS.keys()),
                                   width=24, state="readonly")
        preset_menu.pack(side="left")
        preset_menu.bind("<<ComboboxSelected>>", self._load_preset)

        # Campos manuales
        for lbl, var_name, default in [
            ("Cap A:", "_cap_a", 3),
            ("Cap B:", "_cap_b", 5),
            ("Meta:", "_target", 4),
        ]:
            tk.Label(ctrl, text=lbl, fg=MUTED, bg=PANEL,
                     font=("Courier", 10)).pack(side="left", padx=(12, 2))
            var = tk.IntVar(value=default)
            setattr(self, var_name, var)
            tk.Entry(ctrl, textvariable=var, width=4,
                     bg=WALL, fg=TEXT, insertbackground=TEXT,
                     font=("Courier", 10), relief="flat").pack(side="left")

        tk.Button(ctrl, text="▶  Resolver",
                  font=("Courier", 10, "bold"),
                  fg=BG, bg=ACCENT, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=self._run).pack(side="right", padx=12)

        # Área visual
        vis_frame = tk.Frame(self, bg=BG)
        vis_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # Panel BFS
        self._jug_bfs = JugVisual(vis_frame, "BFS", PATH_BFS)
        self._jug_bfs.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Panel DFS
        self._jug_dfs = JugVisual(vis_frame, "DFS", PATH_DFS)
        self._jug_dfs.pack(side="left", fill="both", expand=True)

        self._stats = StatsBar(self)
        self._stats.pack(fill="x", padx=16, pady=(0, 12))

    def _load_preset(self, _=None):
        ca, cb, t = self.PRESETS[self._preset_var.get()]
        self._cap_a.set(ca)
        self._cap_b.set(cb)
        self._target.set(t)

    def _run(self):
        ca, cb, t = self._cap_a.get(), self._cap_b.get(), self._target.get()
        res_bfs = solve_jugs(ca, cb, t, "bfs")
        res_dfs = solve_jugs(ca, cb, t, "dfs")

        self._jug_bfs.show(res_bfs.path, ca, cb, t)
        self._jug_dfs.show(res_dfs.path, ca, cb, t)
        self._stats.update({"BFS": res_bfs, "DFS": res_dfs})


class JugVisual(tk.Frame):
    def __init__(self, master, label, color):
        super().__init__(master, bg=PANEL)
        self._color = color
        tk.Label(self, text=label, font=("Courier", 12, "bold"),
                 fg=color, bg=PANEL).pack(pady=8)

        self._canvas = tk.Canvas(self, bg=BG, bd=0,
                                 highlightthickness=0, height=300)
        self._canvas.pack(fill="x", padx=12, pady=4)

        # Lista de pasos
        list_frame = tk.Frame(self, bg=PANEL)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        sb = ttk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            list_frame, bg=BG, fg=TEXT,
            font=("Courier", 9), relief="flat",
            selectbackground=color, yscrollcommand=sb.set,
            borderwidth=0, highlightthickness=0
        )
        self._listbox.pack(side="left", fill="both", expand=True)
        sb.config(command=self._listbox.yview)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        self._cap_a = 0
        self._cap_b = 0
        self._path = []

    def show(self, path, cap_a, cap_b, target):
        self._cap_a = cap_a
        self._cap_b = cap_b
        self._path = path
        self._listbox.delete(0, "end")

        if not path:
            self._listbox.insert("end", "  ✗  Sin solución")
            self._draw_jugs(0, 0)
            return

        for i, (a, b) in enumerate(path):
            self._listbox.insert("end",
                f"  {'→' if i > 0 else '·'}  Paso {i}: A={a}L  B={b}L")

        self._listbox.selection_set(0)
        self._draw_jugs(*path[0])

    def _on_select(self, _=None):
        sel = self._listbox.curselection()
        if sel and self._path:
            idx = sel[0]
            if idx < len(self._path):
                self._draw_jugs(*self._path[idx])

    def _draw_jugs(self, a, b):
        cv = self._canvas
        cv.delete("all")
        W = cv.winfo_width() or 300
        H = 260
        jug_w = 70
        jug_h = 160
        pad = 40

        for i, (val, cap, label, x_offset) in enumerate([
            (a, self._cap_a, f"A ({self._cap_a}L)", W // 3),
            (b, self._cap_b, f"B ({self._cap_b}L)", 2 * W // 3),
        ]):
            x = x_offset
            bottom = H - 20
            top = bottom - jug_h

            # Sombra
            cv.create_rectangle(x - jug_w//2 + 4, top + 4,
                                 x + jug_w//2 + 4, bottom + 4,
                                 fill="#000000", outline="")

            # Fondo jarra
            cv.create_rectangle(x - jug_w//2, top, x + jug_w//2, bottom,
                                 fill=WALL, outline=BORDER, width=2)

            # Nivel de agua
            if cap > 0:
                fill_h = int(jug_h * val / cap)
                cv.create_rectangle(
                    x - jug_w//2 + 2, bottom - fill_h,
                    x + jug_w//2 - 2, bottom - 2,
                    fill=self._color, outline=""
                )

            # Texto litros
            cv.create_text(x, bottom - fill_h // 2 if cap > 0 and val > 0 else bottom - 20,
                           text=f"{val}L", fill=BG if val > 0 else MUTED,
                           font=("Courier", 12, "bold"))

            # Etiqueta
            cv.create_text(x, bottom + 18, text=label,
                           fill=MUTED, font=("Courier", 9))


# ══════════════════════════════════════════════
#  PESTAÑA: 8-PUZZLE
# ══════════════════════════════════════════════
class PuzzleTab(tk.Frame):
    PRESETS = {
        "Fácil":  EASY_PUZZLE,
        "Medio":  MEDIUM_PUZZLE,
        "Difícil": HARD_PUZZLE,
    }

    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._current_state = EASY_PUZZLE
        self._build()

    def _build(self):
        ctrl = tk.Frame(self, bg=PANEL)
        ctrl.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(ctrl, text="8-Puzzle", font=("Courier", 14, "bold"),
                 fg=ACCENT, bg=PANEL).pack(side="left", padx=12)

        tk.Label(ctrl, text="Configuración:", fg=MUTED, bg=PANEL,
                 font=("Courier", 10)).pack(side="left", padx=(20, 4))
        self._preset_var = tk.StringVar(value="Fácil")
        preset_menu = ttk.Combobox(ctrl, textvariable=self._preset_var,
                                   values=list(self.PRESETS.keys()),
                                   width=10, state="readonly")
        preset_menu.pack(side="left")
        preset_menu.bind("<<ComboboxSelected>>", self._load_preset)

        tk.Button(ctrl, text="🎲 Aleatorio",
                  font=("Courier", 10),
                  fg=TEXT, bg=WALL, relief="flat",
                  padx=10, pady=6, cursor="hand2",
                  command=self._random_puzzle).pack(side="left", padx=8)

        tk.Button(ctrl, text="▶  Resolver",
                  font=("Courier", 10, "bold"),
                  fg=BG, bg=ACCENT, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=self._run).pack(side="right", padx=12)

        # Área visual
        vis_frame = tk.Frame(self, bg=BG)
        vis_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # Estado inicial
        init_frame = tk.Frame(vis_frame, bg=PANEL)
        init_frame.pack(side="left", padx=(0, 16))
        tk.Label(init_frame, text="Estado Inicial",
                 font=("Courier", 11, "bold"),
                 fg=MUTED, bg=PANEL).pack(pady=8)
        self._init_grid = PuzzleGrid(init_frame, editable=True)
        self._init_grid.pack(padx=20, pady=8)
        self._init_grid.set_state(self._current_state)

        # Panel BFS
        self._puzzle_bfs = PuzzlePanel(vis_frame, "BFS", PATH_BFS)
        self._puzzle_bfs.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Panel DFS
        self._puzzle_dfs = PuzzlePanel(vis_frame, "DFS", PATH_DFS)
        self._puzzle_dfs.pack(side="left", fill="both", expand=True)

        self._stats = StatsBar(self)
        self._stats.pack(fill="x", padx=16, pady=(0, 12))

    def _load_preset(self, _=None):
        state = self.PRESETS[self._preset_var.get()]
        self._current_state = state
        self._init_grid.set_state(state)

    def _random_puzzle(self):
        tiles = list(range(9))
        while True:
            random.shuffle(tiles)
            state = tuple(tiles)
            if is_solvable(state):
                break
        self._current_state = state
        self._init_grid.set_state(state)

    def _run(self):
        state = self._init_grid.get_state()
        if not is_solvable(state):
            messagebox.showwarning("8-Puzzle",
                "Este estado no tiene solución.\nEl número de inversiones es impar.")
            return

        def solve_and_update():
            res_bfs = solve_puzzle(state, algorithm="bfs")
            res_dfs = solve_puzzle(state, algorithm="dfs")
            self.after(0, lambda: self._puzzle_bfs.show(res_bfs.path))
            self.after(0, lambda: self._puzzle_dfs.show(res_dfs.path))
            self.after(0, lambda: self._stats.update({"BFS": res_bfs, "DFS": res_dfs}))

        threading.Thread(target=solve_and_update, daemon=True).start()


class PuzzleGrid(tk.Frame):
    CELL = 72

    def __init__(self, master, editable=False):
        super().__init__(master, bg=PANEL)
        self._editable = editable
        self._vars = []
        self._entries = []
        self._state = EASY_PUZZLE

        for i in range(9):
            var = tk.StringVar(value=str(EASY_PUZZLE[i] or " "))
            self._vars.append(var)
            row, col = divmod(i, 3)
            e = tk.Label(
                self,
                textvariable=var,
                font=("Courier", 22, "bold"),
                fg=TEXT if EASY_PUZZLE[i] != 0 else BG,
                bg=WALL if EASY_PUZZLE[i] != 0 else ACCENT,
                width=2, relief="flat",
                padx=10, pady=14
            )
            e.grid(row=row, column=col, padx=3, pady=3)
            self._entries.append(e)

    def set_state(self, state):
        self._state = state
        for i, v in enumerate(state):
            self._vars[i].set(str(v) if v != 0 else " ")
            self._entries[i].configure(
                fg=TEXT if v != 0 else BG,
                bg=WALL if v != 0 else ACCENT
            )

    def get_state(self):
        return self._state


class PuzzlePanel(tk.Frame):
    def __init__(self, master, label, color):
        super().__init__(master, bg=PANEL)
        self._color = color
        tk.Label(self, text=label, font=("Courier", 12, "bold"),
                 fg=color, bg=PANEL).pack(pady=8)

        self._grid = PuzzleGrid(self)
        self._grid.pack(padx=16, pady=4)

        nav_frame = tk.Frame(self, bg=PANEL)
        nav_frame.pack(pady=8)

        tk.Button(nav_frame, text="◀", font=("Courier", 12),
                  fg=TEXT, bg=WALL, relief="flat", width=3,
                  cursor="hand2",
                  command=self._prev).pack(side="left", padx=4)

        self._step_label = tk.Label(nav_frame, text="Paso 0 / 0",
                                    font=("Courier", 9), fg=MUTED, bg=PANEL)
        self._step_label.pack(side="left", padx=8)

        tk.Button(nav_frame, text="▶", font=("Courier", 12),
                  fg=TEXT, bg=WALL, relief="flat", width=3,
                  cursor="hand2",
                  command=self._next).pack(side="left", padx=4)

        tk.Button(nav_frame, text="▶▶", font=("Courier", 9),
                  fg=BG, bg=color, relief="flat",
                  cursor="hand2",
                  command=self._auto_play).pack(side="left", padx=4)

        self._path = []
        self._step = 0

    def show(self, path):
        self._path = path
        self._step = 0
        if path:
            self._grid.set_state(path[0])
            self._step_label.configure(
                text=f"Paso 0 / {len(path) - 1}")

    def _prev(self):
        if self._step > 0:
            self._step -= 1
            self._grid.set_state(self._path[self._step])
            self._step_label.configure(
                text=f"Paso {self._step} / {len(self._path) - 1}")

    def _next(self):
        if self._path and self._step < len(self._path) - 1:
            self._step += 1
            self._grid.set_state(self._path[self._step])
            self._step_label.configure(
                text=f"Paso {self._step} / {len(self._path) - 1}")

    def _auto_play(self):
        if not self._path:
            return
        self._step = 0
        self._grid.set_state(self._path[0])

        def step():
            if self._step < len(self._path) - 1:
                self._step += 1
                self._grid.set_state(self._path[self._step])
                self._step_label.configure(
                    text=f"Paso {self._step} / {len(self._path) - 1}")
                self.after(400, step)
        self.after(400, step)


# ══════════════════════════════════════════════
#  BARRA DE ESTADÍSTICAS
# ══════════════════════════════════════════════
class StatsBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=PANEL, height=56)
        self.pack_propagate(False)

        self._labels = {}
        tk.Label(self, text="Métricas:", font=("Courier", 9, "bold"),
                 fg=MUTED, bg=PANEL).pack(side="left", padx=12)

        for algo, color in [("BFS", PATH_BFS), ("DFS", PATH_DFS)]:
            lbl = tk.Label(self, text=f"{algo}: —",
                           font=("Courier", 9), fg=color, bg=PANEL)
            lbl.pack(side="left", padx=16)
            self._labels[algo] = lbl

    def update(self, results: dict):
        for algo, res in results.items():
            if algo in self._labels:
                if res.found:
                    txt = (
                        f"{algo}:  {len(res.path)} pasos  │  "
                        f"{res.nodes_visited} nodos  │  "
                        f"{res.time_ms} ms  │  "
                        f"{res.memory_kb} KB"
                    )
                else:
                    txt = f"{algo}:  ✗ Sin solución"
                self._labels[algo].configure(text=txt)


# ══════════════════════════════════════════════
#  ENTRYPOINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    # Centrar ventana
    app.update_idletasks()
    w, h = app.winfo_width(), app.winfo_height()
    sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
    app.geometry(f"1200x800+{(sw-1200)//2}+{(sh-800)//2}")
    app.mainloop()
