"""
Explorador interactivo del Taller Entregable 2 - Cálculo 1 (Segundo Corte).
Aplicación Python con interfaz oscura, controles numéricos y gráficas.
Preparada para ejecutarse localmente y adaptarse después a Streamlit.

Instalación:
    pip install numpy matplotlib sympy

Ejecución:
    python calculadora_taller_calculo.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp


BG = "#f3f5f8"
PANEL = "#ffffff"
PANEL_2 = "#e7ebf2"
TEXT = "#202735"
MUTED = "#667085"
ACCENT = "#d94841"
CYAN = "#d94841"
PINK = "#2563eb"
GREEN = "#16805d"
RED = "#b42318"

x_sym = sp.symbols("x")


def safe_float(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Valor no válido para {name}.")
    if not math.isfinite(number):
        raise ValueError(f"{name} debe ser un número finito.")
    return number


def fmt(value):
    if isinstance(value, (int, np.integer)):
        return str(value)
    if not np.isfinite(value):
        return str(value)
    return f"{float(value):.8g}"


class TallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Taller Cálculo I")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 740)
        self.root.configure(bg=BG)

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("TNotebook", background=BG, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=PANEL_2, foreground=TEXT,
                             padding=(18, 10), font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                       foreground=[("selected", "#ffffff")])
        self.style.configure("TScale", background=PANEL)
        self.style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2,
                             foreground=TEXT, arrowcolor=TEXT)
        self.style.configure("TButton", background=ACCENT, foreground="#ffffff",
                             padding=(10, 6), font=("Segoe UI", 9, "bold"))
        self.style.map("TButton", background=[("active", "#927bff")])

        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 12))
        tk.Label(header, text="TALLER", bg=BG, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(side="left")
        tk.Label(header, text="CÁLCULO I  SEGUNDO CORTE", bg=BG, fg=CYAN,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=18, pady=(8, 0))

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.frames = []
        for title in ("Punto 1", "Punto 2", "Punto 3"):
            frame = tk.Frame(self.tabs, bg=BG)
            self.tabs.add(frame, text=title)
            self.frames.append(frame)

        self.build_point1(self.frames[0])
        self.build_point2(self.frames[1])
        self.build_point3(self.frames[2])

    def section(self, parent, title, subtitle=None):
        box = tk.Frame(parent, bg=PANEL, padx=16, pady=14)
        box.pack(fill="x", padx=8, pady=8)
        tk.Label(box, text=title, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(box, text=subtitle, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
        return box

    def math_label(self, parent, latex, color=TEXT, size=15):
        # Renderiza fórmulas LaTeX reales como imagen mediante Matplotlib.
        fig = Figure(figsize=(7.5, 0.7), dpi=100, facecolor=PANEL)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PANEL)
        ax.axis("off")
        ax.text(0.01, 0.5, f"${latex}$", color=color, fontsize=size,
                va="center", ha="left")
        fig.tight_layout(pad=0.05)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", anchor="w")
        return canvas

    def control(self, parent, label, default, low, high, step, callback):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, bg=PANEL, fg=MUTED, width=17, anchor="w",
                 font=("Segoe UI", 9)).pack(side="left")
        var = tk.StringVar(value=str(default))
        entry = tk.Entry(row, textvariable=var, bg=PANEL_2, fg=TEXT, insertbackground=TEXT,
                         relief="flat", width=11, font=("Consolas", 10))
        entry.pack(side="left", padx=(0, 12), ipady=5)
        scale_var = tk.DoubleVar(value=float(default))
        scale = tk.Scale(row, variable=scale_var, from_=low, to=high, resolution=step,
                         orient="horizontal", showvalue=False, length=220,
                         bg=PANEL, fg=TEXT, troughcolor=PANEL_2, activebackground=ACCENT,
                         highlightthickness=0, command=lambda v: self._slider_update(
                             v, var, callback))
        scale.pack(side="left", fill="x", expand=True)

        def typed(*_):
            try:
                value = safe_float(var.get(), label)
                scale_var.set(min(high, max(low, value)))
                callback()
            except ValueError:
                pass

        var.trace_add("write", typed)
        return var, scale_var

    def _slider_update(self, value, text_var, callback):
        text_var.set(fmt(float(value)))
        callback()

    def graph_area(self, parent):
        frame = tk.Frame(parent, bg=PANEL, padx=8, pady=8)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        fig = Figure(figsize=(8.5, 5.5), dpi=110, facecolor=PANEL)
        ax = fig.add_subplot(111)
        ax.set_facecolor("#fbfcfe")
        ax.tick_params(colors=MUTED)
        for spine in ax.spines.values():
            spine.set_color("#46516b")
        ax.minorticks_on()
        ax.grid(True, which="major", color="#b8c1d1", alpha=0.8, linestyle="-", linewidth=0.7)
        ax.grid(True, which="minor", color="#e1e6ee", alpha=0.9, linestyle=":", linewidth=0.45)
        ax.axhline(0, color="#475467", linewidth=0.9, zorder=0)
        ax.axvline(0, color="#475467", linewidth=0.9, zorder=0)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return fig, ax, canvas

    def build_point1(self, parent):
        left = tk.Frame(parent, bg=BG, width=360)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        box = self.section(left, "Límite trigonométrico")
        self.math_label(box, r"\lim_{x\to 0}\frac{1-\cos(2x)}{x\sin(3x)}", CYAN, 17)
        self.p1 = {}
        self.p1["a"], _ = self.control(box, r"a (cos(ax))", 2, 0.1, 20, 0.1, self.update_p1)
        self.p1["b"], _ = self.control(box, r"b (sin(bx))", 3, 0.1, 20, 0.1, self.update_p1)
        self.p1["c"], _ = self.control(box, "Factor x", 1, 0.1, 20, 0.1, self.update_p1)
        self.p1["eps"], _ = self.control(box, "Excluir |x| <", 0.02, 0.001, 0.2, 0.001, self.update_p1)
        self.p1_formula = tk.Label(box, text="", bg=PANEL, fg=TEXT,
                                   font=("Consolas", 10), justify="left", wraplength=320)
        self.p1_formula.pack(anchor="w", pady=(8, 0))
        self.p1_result = tk.Label(box, text="", bg=PANEL, fg=GREEN,
                                  font=("Consolas", 11, "bold"), justify="left")
        self.p1_result.pack(anchor="w", pady=(6, 0))
        self.fig1, self.ax1, self.can1 = self.graph_area(right)
        self.update_p1()

    def update_p1(self):
        try:
            a, b, c, eps = [safe_float(self.p1[k].get(), k) for k in ("a", "b", "c", "eps")]
            if c == 0 or eps <= 0:
                raise ValueError("El factor x y el corte deben ser positivos.")
            self.ax1.clear()
            xs1 = np.linspace(-1, -eps, 700)
            xs2 = np.linspace(eps, 1, 700)
            xs = np.concatenate((xs1, xs2))
            den = c * xs * np.sin(b * xs)
            ys = np.divide(1 - np.cos(a * xs), den,
                           out=np.full_like(xs, np.nan), where=np.abs(den) > 1e-12)
            ys[~np.isfinite(ys)] = np.nan
            self.ax1.plot(xs, ys, color="#d94841", lw=2, label="f(x)")
            limit = (a*a)/(2*c*b) if b != 0 else np.nan
            self.ax1.axhline(limit, color="#2563eb", ls="--", lw=1.8, label=f"Asíntota: y = {fmt(limit)}")
            self.ax1.set_xlim(-10, 10)
            self.ax1.set_ylim(-2, 8)
            self._style_axes(self.ax1, "Punto 1")
            self.ax1.legend(facecolor=PANEL, labelcolor=TEXT)
            self.can1.draw_idle()
            self.p1_result.config(text=f"Límite esperado: {fmt(limit)}\n"
                                       f"f(0) no está definida en la expresión.")
        except (ValueError, ZeroDivisionError) as exc:
            if hasattr(self, "p1_result"):
                self.p1_result.config(text=str(exc), fg=RED)

    def build_point2(self, parent):
        left = tk.Frame(parent, bg=BG, width=390)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        box = self.section(left, "Continuidad en x = 0")
        self.math_label(box, r"f(x)=\frac{\sqrt{x+p}-q}{x}\ (x<0),\quad f(0)=a,\quad f(x)=\frac{1-\cos(bx)}{d x^2}\ (x>0)", CYAN, 13)
        self.p2 = {}
        self.p2["p"], _ = self.control(box, "p (radicando)", 4, 0.5, 25, 0.1, self.update_p2)
        self.p2["q"], _ = self.control(box, "q (resta)", 2, 0.1, 5, 0.1, self.update_p2)
        self.p2["a"], _ = self.control(box, "a = f(0)", 0.25, -2, 2, 0.01, self.update_p2)
        self.p2["b"], _ = self.control(box, "b (coseno)", 1, 0.1, 20, 0.1, self.update_p2)
        self.p2["d"], _ = self.control(box, "d (denominador)", 2, 0.1, 8, 0.1, self.update_p2)
        self.p2_formula = tk.Label(box, text="", bg=PANEL, fg=TEXT,
                                   font=("Consolas", 9), justify="left", wraplength=350)
        self.p2_formula.pack(anchor="w", pady=(6, 0))
        self.p2_result = tk.Label(box, text="", bg=PANEL, fg=GREEN,
                                  font=("Consolas", 10, "bold"), justify="left")
        self.p2_result.pack(anchor="w", pady=(6, 0))
        self.fig2, self.ax2, self.can2 = self.graph_area(right)
        self.update_p2()

    def update_p2(self):
        try:
            p, q, a, b, d = [safe_float(self.p2[k].get(), k) for k in ("p", "q", "a", "b", "d")]
            if p <= 0 or d == 0:
                raise ValueError("p debe ser positivo y d distinto de cero.")
            left_limit = (1/(2*q) if q > 0 and np.isclose(p, q*q) else (0.0 if np.isclose(p, q*q) and np.isclose(q, 0) else np.nan))
            right_limit = b*b/(2*d)
            self.ax2.clear()
            xs_left = np.linspace(-min(1.5, p*0.4), -0.003, 600)
            rad = xs_left + p
            valid = rad >= 0
            xs_left = xs_left[valid]
            yl = (np.sqrt(xs_left + p) - q) / xs_left
            xs_right = np.linspace(0.003, 1.5, 600)
            yr = (1 - np.cos(b*xs_right))/(d*xs_right**2)
            self.ax2.plot(xs_left, yl, color="#d94841", lw=2, label="x < 0")
            self.ax2.plot(xs_right, yr, color="#2563eb", lw=2, label="x > 0")
            self.ax2.scatter([0], [a], color=PINK, s=70, zorder=5, label=f"(0, a={fmt(a)})")
            self.ax2.axhline(left_limit, color="#16805d", ls=":", label=f"Límite izquierdo: y = {fmt(left_limit)}")
            self.ax2.axhline(right_limit, color="#7c3aed", ls="--", label=f"Límite derecho: y = {fmt(right_limit)}")
            self.ax2.set_xlim(-2, 2)
            self.ax2.set_ylim(-2, 4)
            self._style_axes(self.ax2, "Punto 2")
            self.ax2.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8)
            self.can2.draw_idle()
            continuous = np.isfinite(left_limit) and np.isclose(left_limit, right_limit) and np.isclose(a, left_limit)
            self.p2_formula.config(text=f"x<0: (√(x+{fmt(p)})−{fmt(q)})/x   |   f(0)={fmt(a)}\n"
                                        f"x>0: (1−cos({fmt(b)}x))/({fmt(d)}x²)")
            self.p2_result.config(
                text=f"Límite izquierdo: {fmt(left_limit)}\nLímite derecho: {fmt(right_limit)}\n"
                     f"a: {fmt(a)}\nContinuidad: {'sí' if continuous else 'no'}",
                fg=GREEN if continuous else RED)
        except (ValueError, ZeroDivisionError) as exc:
            if hasattr(self, "p2_result"):
                self.p2_result.config(text=str(exc), fg=RED)

    def build_point3(self, parent):
        left = tk.Frame(parent, bg=BG, width=360)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        box = self.section(left, "Límite al infinito")
        self.math_label(box, r"\lim_{x\to\infty}\left(\sqrt{4x^2+3x}-2x\right)", CYAN, 15)
        self.p3 = {}
        self.p3["A"], _ = self.control(box, "Coef. x²", 4, 0.1, 25, 0.1, self.update_p3)
        self.p3["B"], _ = self.control(box, "Coef. x", 3, -25, 25, 0.1, self.update_p3)
        self.p3["C"], _ = self.control(box, "Término exterior", 2, -20, 20, 0.1, self.update_p3)
        self.p3["xmin"], _ = self.control(box, "x mínimo", 0.01, 0.001, 2, 0.001, self.update_p3)
        self.p3["xmax"], _ = self.control(box, "x máximo", 50, 5, 200, 1, self.update_p3)
        self.p3_formula = tk.Label(box, text="", bg=PANEL, fg=TEXT,
                                   font=("Consolas", 10), justify="left", wraplength=320)
        self.p3_formula.pack(anchor="w", pady=(8, 0))
        self.p3_result = tk.Label(box, text="", bg=PANEL, fg=GREEN,
                                  font=("Consolas", 11, "bold"), justify="left")
        self.p3_result.pack(anchor="w", pady=(6, 0))
        self.fig3, self.ax3, self.can3 = self.graph_area(right)
        self.update_p3()

    def update_p3(self):
        try:
            A, B, C, xmin, xmax = [safe_float(self.p3[k].get(), k) for k in ("A", "B", "C", "xmin", "xmax")]
            if A <= 0 or xmin <= 0 or xmax <= xmin:
                raise ValueError("Se requiere A > 0 y 0 < x mínimo < x máximo.")
            xs = np.linspace(xmin, xmax, 1000)
            rad = A*xs**2 + B*xs
            ys = np.sqrt(np.maximum(rad, 0)) - C*xs
            # Límite para x -> +infinito: (sqrt(A) - C) x; si coincide, término constante B/(2 sqrt(A)).
            if np.isclose(math.sqrt(A), C):
                limit = B/(2*math.sqrt(A))
                horizontal = True
            else:
                limit = np.inf if math.sqrt(A) > C else -np.inf
                horizontal = False
            self.ax3.clear()
            self.ax3.plot(xs, ys, color="#d94841", lw=2, label=r"$f(x)=\sqrt{Ax^2+Bx}-Cx$")
            if horizontal:
                self.ax3.axhline(limit, color="#2563eb", ls="--", lw=1.8, label=f"Asíntota: y = {fmt(limit)}")
            self.ax3.set_xlim(-max(20, xmax), max(20, xmax))
            yfinite = ys[np.isfinite(ys)]
            if yfinite.size:
                self.ax3.set_ylim(-max(20, abs(float(np.min(yfinite))) + 1, abs(float(np.max(yfinite))) + 1), max(20, abs(float(np.min(yfinite))) + 1, abs(float(np.max(yfinite))) + 1))
            self._style_axes(self.ax3, "Punto 3")
            self.ax3.legend(facecolor=PANEL, labelcolor=TEXT)
            self.can3.draw_idle()
            self.p3_formula.config(text=f"f(x) = √({fmt(A)}x² + {fmt(B)}x) − {fmt(C)}x")
            self.p3_result.config(text=f"Límite cuando x → ∞: {fmt(limit)}\n"
                                       f"Asíntota horizontal: {'y = ' + fmt(limit) if horizontal else 'no existe'}",
                                  fg=GREEN if horizontal else MUTED)
        except (ValueError, ZeroDivisionError) as exc:
            if hasattr(self, "p3_result"):
                self.p3_result.config(text=str(exc), fg=RED)

    @staticmethod
    def _style_axes(ax, title):
        ax.set_title(title, color=TEXT, fontsize=12, pad=10)
        ax.set_xlabel("x", color=MUTED)
        ax.set_ylabel("y", color=MUTED)
        ax.tick_params(colors=MUTED)
        from matplotlib.ticker import MultipleLocator
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.yaxis.set_major_locator(MultipleLocator(10))
        ax.xaxis.set_minor_locator(MultipleLocator(2))
        ax.yaxis.set_minor_locator(MultipleLocator(2))
        ax.grid(True, which="major", color="#b8c1d1", alpha=0.85, linestyle="-", linewidth=0.75)
        ax.grid(True, which="minor", color="#e1e6ee", alpha=0.95, linestyle=":", linewidth=0.45)
        # Plano cartesiano centrado: los ejes pasan por el origen.
        ax.spines["left"].set_position(("data", 0))
        ax.spines["bottom"].set_position(("data", 0))
        ax.spines["right"].set_color("none")
        ax.spines["top"].set_color("none")
        ax.spines["left"].set_color("#475467")
        ax.spines["bottom"].set_color("#475467")
        ax.spines["left"].set_linewidth(1.2)
        ax.spines["bottom"].set_linewidth(1.2)
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")


def main():
    root = tk.Tk()
    app = TallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
