"""
=============================================================
  LABORATÓRIO DE PROGRAMAÇÃO AVANÇADA — BACKTRACKING
  Visualizador Gráfico Interactivo (tkinter)

  Dois problemas com animação passo a passo:
    1. N-Rainhas
    2. Sudoku Solver

  Autores: Dário Puíssa João | Félix Bongue
  Curso: Ciência da Computação — 3.º Ano
  Disciplina: Laboratório de Programação Avançada

  Como executar:
    python backtracking_visual.py
  Requisitos:
    Python 3.x  (tkinter já vem incluído)
=============================================================
"""

import tkinter as tk
from tkinter import font as tkfont
import time
import threading

# ─────────────────────────────────────────────
#  PALETA DE CORES
# ─────────────────────────────────────────────
BG          = "#0f1117"   # fundo geral
PANEL       = "#1a1d27"   # painéis
BORDER      = "#2a2d3a"   # bordas
WHITE       = "#e8eaf0"
GREY        = "#6b7080"
GREEN       = "#00e676"   # colocação válida
RED         = "#ff3d57"   # conflito / backtrack
YELLOW      = "#ffd740"   # célula activa
BLUE        = "#448aff"   # solução encontrada
PURPLE      = "#ce93d8"   # número fixo (Sudoku)
DARK_GREEN  = "#1b3a2a"
DARK_RED    = "#3a1b20"
DARK_YELLOW = "#3a3010"
DARK_BLUE   = "#1a2a4a"


# ═══════════════════════════════════════════════════════════════
#  ECRÃ PRINCIPAL — menu de escolha
# ═══════════════════════════════════════════════════════════════
class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backtracking — Visualizador")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        pad = dict(padx=30, pady=10)

        tk.Label(self.root, text="BACKTRACKING",
                 bg=BG, fg=GREEN,
                 font=("Courier", 28, "bold")).pack(pady=(40, 4))
        tk.Label(self.root, text="Visualizador Interactivo",
                 bg=BG, fg=GREY,
                 font=("Courier", 11)).pack(pady=(0, 30))

        tk.Button(self.root, text="♛  N-Rainhas",
                  bg=PANEL, fg=WHITE, activebackground=GREEN,
                  activeforeground=BG, relief="flat",
                  font=("Courier", 13, "bold"),
                  cursor="hand2", width=22,
                  command=self._open_queens
                  ).pack(**pad)

        tk.Button(self.root, text="⊞  Sudoku Solver",
                  bg=PANEL, fg=WHITE, activebackground=BLUE,
                  activeforeground=BG, relief="flat",
                  font=("Courier", 13, "bold"),
                  cursor="hand2", width=22,
                  command=self._open_sudoku
                  ).pack(**pad)

        tk.Label(self.root, text="LPA · 3.º Ano · 2026",
                 bg=BG, fg=BORDER,
                 font=("Courier", 9)).pack(pady=(30, 20))

    def _open_queens(self):
        win = tk.Toplevel(self.root)
        NQueensApp(win)

    def _open_sudoku(self):
        win = tk.Toplevel(self.root)
        SudokuApp(win)


# ═══════════════════════════════════════════════════════════════
#  PROBLEMA 1 — N-RAINHAS
# ═══════════════════════════════════════════════════════════════
class NQueensApp:
    CELL = 62          # tamanho da célula em px
    MIN_N, MAX_N = 4, 10

    def __init__(self, root):
        self.root = root
        self.root.title("N-Rainhas — Backtracking")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.n         = tk.IntVar(value=6)
        self.speed     = tk.IntVar(value=5)   # 1=lento … 10=rápido
        self.running   = False
        self.paused    = False
        self.steps     = 0
        self.backtracks= 0
        self.solutions = []

        self._build_ui()
        self._draw_board()

    # ── Layout ──────────────────────────────────────────────────
    def _build_ui(self):
        # título
        tk.Label(self.root, text="♛  N-RAINHAS",
                 bg=BG, fg=GREEN,
                 font=("Courier", 16, "bold")).pack(pady=(18, 2))
        tk.Label(self.root,
                 text="Cada rainha é colocada linha a linha.\n"
                      "Vermelho = conflito → backtrack.  Verde = posição válida.",
                 bg=BG, fg=GREY, font=("Courier", 9),
                 justify="center").pack(pady=(0, 10))

        # canvas
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=20)

        # controlos
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(pady=10, fill="x", padx=20)

        tk.Label(ctrl, text="N:", bg=BG, fg=WHITE,
                 font=("Courier", 11)).grid(row=0, column=0, padx=4)
        self.n_spin = tk.Spinbox(ctrl, from_=self.MIN_N, to=self.MAX_N,
                                 textvariable=self.n, width=4,
                                 bg=PANEL, fg=GREEN, insertbackground=GREEN,
                                 font=("Courier", 12, "bold"),
                                 relief="flat", command=self._reset)
        self.n_spin.grid(row=0, column=1, padx=4)

        tk.Label(ctrl, text="  Velocidade:", bg=BG, fg=WHITE,
                 font=("Courier", 11)).grid(row=0, column=2, padx=4)
        tk.Scale(ctrl, from_=1, to=10, orient="horizontal",
                 variable=self.speed, length=110,
                 bg=BG, fg=WHITE, troughcolor=PANEL,
                 highlightthickness=0, showvalue=False
                 ).grid(row=0, column=3, padx=4)

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=6)

        self.btn_start = self._btn(btn_frame, "▶  Iniciar",  GREEN, self._start, 0)
        self.btn_pause = self._btn(btn_frame, "⏸  Pausar",  YELLOW, self._toggle_pause, 1)
        self.btn_reset = self._btn(btn_frame, "↺  Reiniciar", RED,   self._reset, 2)
        self.btn_pause.config(state="disabled")

        # estatísticas
        stats = tk.Frame(self.root, bg=PANEL)
        stats.pack(padx=20, pady=(4, 16), fill="x")

        self.lbl_steps = self._stat(stats, "Passos",       "0", 0)
        self.lbl_back  = self._stat(stats, "Backtracks",   "0", 1)
        self.lbl_sols  = self._stat(stats, "Soluções",     "0", 2)
        self.lbl_info  = self._stat(stats, "Estado", "Em espera", 3)

    def _btn(self, parent, text, color, cmd, col):
        b = tk.Button(parent, text=text, bg=PANEL, fg=color,
                      activebackground=color, activeforeground=BG,
                      relief="flat", font=("Courier", 10, "bold"),
                      cursor="hand2", width=13, command=cmd)
        b.grid(row=0, column=col, padx=5)
        return b

    def _stat(self, parent, label, val, col):
        f = tk.Frame(parent, bg=PANEL)
        f.grid(row=0, column=col, padx=12, pady=8, sticky="w")
        tk.Label(f, text=label, bg=PANEL, fg=GREY,
                 font=("Courier", 8)).pack(anchor="w")
        lbl = tk.Label(f, text=val, bg=PANEL, fg=WHITE,
                       font=("Courier", 13, "bold"))
        lbl.pack(anchor="w")
        return lbl

    # ── Tabuleiro ───────────────────────────────────────────────
    def _draw_board(self):
        n = self.n.get()
        C = self.CELL
        size = n * C
        self.canvas.config(width=size, height=size)
        self.canvas.delete("all")
        self.board_state = [None] * n   # coluna da rainha por linha, ou None

        for r in range(n):
            for c in range(n):
                x0, y0 = c * C, r * C
                fill = "#1e2130" if (r + c) % 2 == 0 else "#252838"
                self.canvas.create_rectangle(x0, y0, x0+C, y0+C,
                                             fill=fill, outline=BORDER,
                                             tags=f"cell_{r}_{c}")

    def _color_cell(self, row, col, state):
        """state: 'try' | 'conflict' | 'queen' | 'solution' | 'clear'"""
        C = self.CELL
        base = "#1e2130" if (row + col) % 2 == 0 else "#252838"
        fills = {
            "try":      (DARK_YELLOW, YELLOW),
            "conflict": (DARK_RED,    RED),
            "queen":    (DARK_GREEN,  GREEN),
            "solution": (DARK_BLUE,   BLUE),
            "clear":    (base,        None),
        }
        bg_fill, fg = fills[state]
        C = self.CELL
        x0, y0 = col * C, row * C
        self.canvas.delete(f"piece_{row}_{col}")
        self.canvas.itemconfig(f"cell_{row}_{col}", fill=bg_fill)
        if fg:
            symbol = "♛" if state in ("queen", "solution") else ("✕" if state == "conflict" else "·")
            self.canvas.create_text(
                x0 + C//2, y0 + C//2,
                text=symbol, fill=fg,
                font=("Courier", int(C * 0.48), "bold"),
                tags=f"piece_{row}_{col}"
            )

    def _update_stats(self, info=None):
        self.lbl_steps.config(text=str(self.steps))
        self.lbl_back.config(text=str(self.backtracks))
        self.lbl_sols.config(text=str(len(self.solutions)))
        if info:
            self.lbl_info.config(text=info)

    # ── Algoritmo ───────────────────────────────────────────────
    def _start(self):
        if self.running:
            return
        self._reset_state()
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.n_spin.config(state="disabled")
        t = threading.Thread(target=self._run_backtrack, daemon=True)
        t.start()

    def _toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.config(text="▶  Continuar" if self.paused else "⏸  Pausar")

    def _reset(self):
        self.running = False
        self.paused  = False
        self._reset_state()
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸  Pausar")
        self.n_spin.config(state="normal")
        self._draw_board()
        self._update_stats("Em espera")

    def _reset_state(self):
        self.steps      = 0
        self.backtracks = 0
        self.solutions  = []
        self.board_state = [None] * self.n.get()

    def _delay(self):
        s = self.speed.get()
        # velocidade 1=300ms … 10=10ms
        ms = max(10, 310 - s * 30)
        time.sleep(ms / 1000)
        while self.paused and self.running:
            time.sleep(0.05)

    def _run_backtrack(self):
        n = self.n.get()
        queens = []   # queens[linha] = coluna

        def valid(row, col):
            for r, c in enumerate(queens):
                if c == col or abs(c - col) == abs(r - row):
                    return False
            return True

        def bt(row):
            if not self.running:
                return
            if row == n:
                self.solutions.append(list(queens))
                # pintar solução
                for r, c in enumerate(queens):
                    self.canvas.after(0, self._color_cell, r, c, "solution")
                self.canvas.after(0, self._update_stats, f"Solução #{len(self.solutions)}!")
                self._delay()
                self._delay()
                # repintar como rainha normal para continuar
                for r, c in enumerate(queens):
                    self.canvas.after(0, self._color_cell, r, c, "queen")
                return

            for col in range(n):
                if not self.running:
                    return
                self.steps += 1
                self.canvas.after(0, self._color_cell, row, col, "try")
                self.canvas.after(0, self._update_stats, f"Testando linha {row}, col {col}")
                self._delay()

                if valid(row, col):
                    queens.append(col)
                    self.canvas.after(0, self._color_cell, row, col, "queen")
                    self._delay()
                    bt(row + 1)
                    if not self.running:
                        return
                    queens.pop()
                    # backtrack visual
                    self.backtracks += 1
                    self.canvas.after(0, self._color_cell, row, col, "conflict")
                    self.canvas.after(0, self._update_stats, f"Backtrack na linha {row}")
                    self._delay()
                    self.canvas.after(0, self._color_cell, row, col, "clear")
                else:
                    self.canvas.after(0, self._color_cell, row, col, "conflict")
                    self._delay()
                    self.canvas.after(0, self._color_cell, row, col, "clear")

        bt(0)
        if self.running:
            total = len(self.solutions)
            msg = f"Concluído! {total} soluções"
            self.canvas.after(0, self._update_stats, msg)
            self.running = False
            self.canvas.after(0, lambda: self.btn_start.config(state="normal"))
            self.canvas.after(0, lambda: self.btn_pause.config(state="disabled"))
            self.canvas.after(0, lambda: self.n_spin.config(state="normal"))


# ═══════════════════════════════════════════════════════════════
#  PROBLEMA 2 — SUDOKU
# ═══════════════════════════════════════════════════════════════
SUDOKU_PUZZLES = {
    "Fácil": [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ],
    "Médio": [
        [0,0,0, 2,6,0, 7,0,1],
        [6,8,0, 0,7,0, 0,9,0],
        [1,9,0, 0,0,4, 5,0,0],
        [8,2,0, 1,0,0, 0,4,0],
        [0,0,4, 6,0,2, 9,0,0],
        [0,5,0, 0,0,3, 0,2,8],
        [0,0,9, 3,0,0, 0,7,4],
        [0,4,0, 0,5,0, 0,3,6],
        [7,0,3, 0,1,8, 0,0,0],
    ],
    "Difícil": [
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,3, 0,8,5],
        [0,0,1, 0,2,0, 0,0,0],
        [0,0,0, 5,0,7, 0,0,0],
        [0,0,4, 0,0,0, 1,0,0],
        [0,9,0, 0,0,0, 0,0,0],
        [5,0,0, 0,0,0, 0,7,3],
        [0,0,2, 0,1,0, 0,0,0],
        [0,0,0, 0,4,0, 0,0,9],
    ],
}

class SudokuApp:
    CELL = 58

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver — Backtracking")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.running  = False
        self.paused   = False
        self.steps    = 0
        self.backtracks = 0
        self.speed    = tk.IntVar(value=6)
        self.puzzle_choice = tk.StringVar(value="Fácil")

        self.fixed    = set()   # células com valor original
        self.board    = []

        self._build_ui()
        self._load_puzzle()

    # ── Layout ──────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self.root, text="⊞  SUDOKU SOLVER",
                 bg=BG, fg=BLUE,
                 font=("Courier", 16, "bold")).pack(pady=(18, 2))
        tk.Label(self.root,
                 text="Células azuis = números fixos.  Verde = tentativa válida.\n"
                      "Vermelho = conflito → o algoritmo apaga e tenta outro número.",
                 bg=BG, fg=GREY, font=("Courier", 9),
                 justify="center").pack(pady=(0, 10))

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=20)

        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(pady=8, fill="x", padx=20)

        tk.Label(ctrl, text="Puzzle:", bg=BG, fg=WHITE,
                 font=("Courier", 11)).grid(row=0, column=0, padx=4)
        for i, name in enumerate(SUDOKU_PUZZLES):
            tk.Radiobutton(ctrl, text=name, variable=self.puzzle_choice,
                           value=name, command=self._reset,
                           bg=BG, fg=WHITE, selectcolor=PANEL,
                           activebackground=BG, font=("Courier", 10)
                           ).grid(row=0, column=i+1, padx=4)

        tk.Label(ctrl, text="  Vel:", bg=BG, fg=WHITE,
                 font=("Courier", 11)).grid(row=0, column=5, padx=4)
        tk.Scale(ctrl, from_=1, to=10, orient="horizontal",
                 variable=self.speed, length=100,
                 bg=BG, fg=WHITE, troughcolor=PANEL,
                 highlightthickness=0, showvalue=False
                 ).grid(row=0, column=6, padx=4)

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=6)
        self.btn_start = self._btn(btn_frame, "▶  Resolver",  BLUE,   self._start, 0)
        self.btn_pause = self._btn(btn_frame, "⏸  Pausar",   YELLOW, self._toggle_pause, 1)
        self.btn_reset = self._btn(btn_frame, "↺  Reiniciar", RED,    self._reset, 2)
        self.btn_pause.config(state="disabled")

        stats = tk.Frame(self.root, bg=PANEL)
        stats.pack(padx=20, pady=(4, 16), fill="x")
        self.lbl_steps = self._stat(stats, "Passos",     "0", 0)
        self.lbl_back  = self._stat(stats, "Backtracks", "0", 1)
        self.lbl_info  = self._stat(stats, "Estado", "Em espera", 2)

    def _btn(self, parent, text, color, cmd, col):
        b = tk.Button(parent, text=text, bg=PANEL, fg=color,
                      activebackground=color, activeforeground=BG,
                      relief="flat", font=("Courier", 10, "bold"),
                      cursor="hand2", width=14, command=cmd)
        b.grid(row=0, column=col, padx=5)
        return b

    def _stat(self, parent, label, val, col):
        f = tk.Frame(parent, bg=PANEL)
        f.grid(row=0, column=col, padx=16, pady=8, sticky="w")
        tk.Label(f, text=label, bg=PANEL, fg=GREY,
                 font=("Courier", 8)).pack(anchor="w")
        lbl = tk.Label(f, text=val, bg=PANEL, fg=WHITE,
                       font=("Courier", 13, "bold"))
        lbl.pack(anchor="w")
        return lbl

    # ── Tabuleiro ───────────────────────────────────────────────
    def _load_puzzle(self):
        import copy
        name = self.puzzle_choice.get()
        self.board = copy.deepcopy(SUDOKU_PUZZLES[name])
        self.fixed = {(r, c) for r in range(9) for c in range(9)
                      if self.board[r][c] != 0}
        self._draw_board()

    def _draw_board(self):
        C = self.CELL
        size = 9 * C
        self.canvas.config(width=size, height=size)
        self.canvas.delete("all")

        for r in range(9):
            for c in range(9):
                self._draw_cell(r, c, self.board[r][c], "fixed" if (r,c) in self.fixed else "empty")

        # linhas de bloco 3×3
        for i in range(0, 10):
            lw = 3 if i % 3 == 0 else 1
            col = BORDER if lw == 1 else WHITE
            self.canvas.create_line(i*C, 0, i*C, size, fill=col, width=lw)
            self.canvas.create_line(0, i*C, size, i*C, fill=col, width=lw)

    def _draw_cell(self, r, c, val, state):
        C = self.CELL
        x0, y0 = c * C, r * C

        bg_map = {
            "fixed":    "#1a2540",
            "empty":    "#1a1d27",
            "try":      DARK_YELLOW,
            "conflict": DARK_RED,
            "solved":   DARK_GREEN,
            "done":     DARK_BLUE,
        }
        fg_map = {
            "fixed":    PURPLE,
            "empty":    GREY,
            "try":      YELLOW,
            "conflict": RED,
            "solved":   GREEN,
            "done":     BLUE,
        }

        self.canvas.delete(f"cell_{r}_{c}")
        self.canvas.create_rectangle(x0+1, y0+1, x0+C-1, y0+C-1,
                                     fill=bg_map.get(state, PANEL),
                                     outline="", tags=f"cell_{r}_{c}")
        if val != 0:
            self.canvas.delete(f"num_{r}_{c}")
            self.canvas.create_text(
                x0 + C//2, y0 + C//2,
                text=str(val),
                fill=fg_map.get(state, WHITE),
                font=("Courier", int(C * 0.42), "bold"),
                tags=f"num_{r}_{c}"
            )
        else:
            self.canvas.delete(f"num_{r}_{c}")

        # redesenhar linhas de bloco por cima
        self.canvas.after(0, self._redraw_grid_lines)

    def _redraw_grid_lines(self):
        C = self.CELL
        size = 9 * C
        for i in range(0, 10, 3):
            self.canvas.create_line(i*C, 0, i*C, size, fill=WHITE, width=3)
            self.canvas.create_line(0, i*C, size, i*C, fill=WHITE, width=3)

    def _update_stats(self, info=None):
        self.lbl_steps.config(text=str(self.steps))
        self.lbl_back.config(text=str(self.backtracks))
        if info:
            self.lbl_info.config(text=info)

    # ── Algoritmo ───────────────────────────────────────────────
    def _start(self):
        if self.running:
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        t = threading.Thread(target=self._run_backtrack, daemon=True)
        t.start()

    def _toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.config(text="▶  Continuar" if self.paused else "⏸  Pausar")

    def _reset(self):
        self.running  = False
        self.paused   = False
        self.steps    = 0
        self.backtracks = 0
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸  Pausar")
        self._load_puzzle()
        self._update_stats("Em espera")
        self.lbl_steps.config(text="0")
        self.lbl_back.config(text="0")

    def _delay(self):
        s = self.speed.get()
        ms = max(8, 320 - s * 30)
        time.sleep(ms / 1000)
        while self.paused and self.running:
            time.sleep(0.05)

    def _run_backtrack(self):
        board = self.board

        def find_empty():
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        return r, c
            return None

        def valid(r, c, num):
            if num in board[r]:
                return False
            if num in [board[i][c] for i in range(9)]:
                return False
            br, bc = (r//3)*3, (c//3)*3
            for i in range(br, br+3):
                for j in range(bc, bc+3):
                    if board[i][j] == num:
                        return False
            return True

        def bt():
            if not self.running:
                return False
            cell = find_empty()
            if cell is None:
                return True   # solução!

            r, c = cell
            for num in range(1, 10):
                if not self.running:
                    return False
                self.steps += 1

                # mostrar tentativa
                self.canvas.after(0, self._draw_cell, r, c, num, "try")
                self.canvas.after(0, self._update_stats, f"({r},{c}) ← {num}?")
                self._delay()

                if valid(r, c, num):
                    board[r][c] = num
                    self.canvas.after(0, self._draw_cell, r, c, num, "solved")
                    self._delay()

                    if bt():
                        return True

                    if not self.running:
                        return False

                    # backtrack
                    self.backtracks += 1
                    board[r][c] = 0
                    self.canvas.after(0, self._draw_cell, r, c, num, "conflict")
                    self.canvas.after(0, self._update_stats, f"({r},{c}) ← {num} falhou")
                    self._delay()
                    self.canvas.after(0, self._draw_cell, r, c, 0, "empty")
                else:
                    self.canvas.after(0, self._draw_cell, r, c, num, "conflict")
                    self._delay()
                    self.canvas.after(0, self._draw_cell, r, c, 0, "empty")

            return False

        result = bt()

        if self.running:
            if result:
                # pintar tudo de azul (solução completa)
                for r in range(9):
                    for c in range(9):
                        if (r, c) not in self.fixed:
                            self.canvas.after(0, self._draw_cell, r, c, board[r][c], "done")
                self.canvas.after(0, self._update_stats, "✓ Resolvido!")
            else:
                self.canvas.after(0, self._update_stats, "Sem solução.")
            self.running = False
            self.canvas.after(0, lambda: self.btn_start.config(state="normal"))
            self.canvas.after(0, lambda: self.btn_pause.config(state="disabled"))


# ═══════════════════════════════════════════════════════════════
#  ENTRADA
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.eval("tk::PlaceWindow . center")
    app = MenuApp(root)
    root.mainloop()
