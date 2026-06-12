"""Reusable UI components shared by multiple screens."""
from datetime import datetime
from tkinter import ttk

from theme import FONTS


class MonthNav(ttk.Frame):
    """A '< Month Year >' selector bound to a shared StringVar (YYYY-MM).

    All instances trace the same variable, so changing the month on one
    screen keeps every other screen's selector label in sync.
    """

    def __init__(self, parent, month_var, on_change=None):
        super().__init__(parent, style="TFrame")
        self.month_var = month_var
        self.on_change = on_change

        ttk.Button(self, text="\u2039", width=3, command=self._prev).pack(side="left")
        self.label = ttk.Label(self, text="", style="TLabel", width=16,
                               anchor="center", font=FONTS["subhead"])
        self.label.pack(side="left", padx=6)
        ttk.Button(self, text="\u203a", width=3, command=self._next).pack(side="left")

        self.month_var.trace_add("write", lambda *_: self._render())
        self._render()

    def _render(self):
        try:
            dt = datetime.strptime(self.month_var.get(), "%Y-%m")
            self.label.configure(text=dt.strftime("%B %Y"))
        except ValueError:
            self.label.configure(text=self.month_var.get())

    def _shift(self, delta):
        dt = datetime.strptime(self.month_var.get(), "%Y-%m")
        index = dt.year * 12 + (dt.month - 1) + delta
        self.month_var.set(f"{index // 12:04d}-{index % 12 + 1:02d}")
        if self.on_change:
            self.on_change()

    def _prev(self):
        self._shift(-1)

    def _next(self):
        self._shift(1)
