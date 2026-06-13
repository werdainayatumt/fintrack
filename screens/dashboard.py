"""Dashboard screen: at-a-glance metrics, a 6-month income/expense
bar chart drawn natively on a Canvas, and a category breakdown."""
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from components import MonthNav
from theme import COLORS, FONTS


class BarChart(tk.Canvas):
    """Grouped (income vs expense) bar chart drawn on a Tkinter Canvas.

    Redraws on resize so it stays responsive with the window.
    """

    def __init__(self, parent, height=220):
        super().__init__(parent, bg=COLORS["surface"], highlightthickness=0,
                         height=height)
        self.data = []  # list of (label, income, expense)
        self.bind("<Configure>", lambda _e: self._draw())

    def set_data(self, data):
        self.data = data
        self._draw()

    @staticmethod
    def _fmt(v):
        return f"{v / 1000:.0f}k" if v >= 1000 else f"{v:.0f}"

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20 or h < 20:
            return
        if not self.data:
            self.create_text(w // 2, h // 2, text="No data for this period",
                             fill=COLORS["text_muted"], font=FONTS["body"])
            return

        pad_l, pad_r, pad_t, pad_b = 46, 16, 14, 30
        plot_w, plot_h = w - pad_l - pad_r, h - pad_t - pad_b
        max_val = max((max(i, e) for _, i, e in self.data), default=0) or 1

        steps = 4
        for s in range(steps + 1):
            y = pad_t + plot_h * s / steps
            self.create_line(pad_l, y, w - pad_r, y, fill=COLORS["border"])
            self.create_text(pad_l - 8, y, anchor="e", font=FONTS["small"],
                             fill=COLORS["text_muted"],
                             text=self._fmt(max_val * (steps - s) / steps))

        group_w = plot_w / len(self.data)
        bar_w = min(16, group_w / 3)
        base_y = pad_t + plot_h
        for idx, (label, income, expense) in enumerate(self.data):
            cx = pad_l + group_w * (idx + 0.5)
            for j, (val, color) in enumerate(
                ((income, COLORS["success"]), (expense, COLORS["danger"]))
            ):
                x0 = cx - bar_w + j * (bar_w + 2)
                y0 = base_y - plot_h * (val / max_val)
                self.create_rectangle(x0, y0, x0 + bar_w, base_y, fill=color, width=0)
            self.create_text(cx, base_y + 14, anchor="n", text=label,
                             fill=COLORS["text_muted"], font=FONTS["small"])


class DashboardScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app
        self.db = app.db
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Dashboard", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        MonthNav(header, self.app.current_month, self.refresh).grid(
            row=0, column=1, sticky="e")

        # metric cards
        cards = ttk.Frame(self)
        cards.grid(row=1, column=0, sticky="ew", padx=18, pady=8)
        for i in range(3):
            cards.columnconfigure(i, weight=1, uniform="metric")
        self.m_income = self._metric_card(cards, 0, "Income", COLORS["success"])
        self.m_expense = self._metric_card(cards, 1, "Expenses", COLORS["danger"])
        self.m_balance = self._metric_card(cards, 2, "Balance", COLORS["primary"])

        # chart + breakdown
        body = ttk.Frame(self)
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=8)
        body.columnconfigure(0, weight=3, uniform="body")
        body.columnconfigure(1, weight=2, uniform="body")
        body.rowconfigure(0, weight=1)

        chart_card = tk.Frame(body, bg=COLORS["surface"])
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(chart_card, text="Income vs Expenses \u00b7 last 6 months",
                  style="Heading.TLabel").pack(anchor="w", padx=18, pady=(16, 2))
        legend = tk.Frame(chart_card, bg=COLORS["surface"])
        legend.pack(anchor="w", padx=18)
        self._legend(legend, COLORS["success"], "Income")
        self._legend(legend, COLORS["danger"], "Expense")
        self.chart = BarChart(chart_card)
        self.chart.pack(fill="both", expand=True, padx=10, pady=10)

        bd_card = tk.Frame(body, bg=COLORS["surface"])
        bd_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(bd_card, text="Spending by Category", style="Heading.TLabel").pack(
            anchor="w", padx=18, pady=(16, 8))
        self.breakdown = tk.Frame(bd_card, bg=COLORS["surface"])
        self.breakdown.pack(fill="both", expand=True, padx=18, pady=(0, 14))

    def _metric_card(self, parent, col, title, color):
        card = tk.Frame(parent, bg=COLORS["surface"])
        card.grid(row=0, column=col, sticky="ew", padx=6)
        tk.Frame(card, bg=color, height=3).pack(fill="x")
        ttk.Label(card, text=title, style="SurfaceMuted.TLabel",
                  font=FONTS["subhead"]).pack(anchor="w", padx=18, pady=(16, 2))
        value = ttk.Label(card, text="0.00", style="Metric.TLabel",
                          foreground=color, background=COLORS["surface"])
        value.pack(anchor="w", padx=18, pady=(0, 18))
        return value

    def _legend(self, parent, color, text):
        box = tk.Frame(parent, bg=COLORS["surface"])
        box.pack(side="left", padx=(0, 14))
        tk.Frame(box, bg=color, width=10, height=10).pack(side="left", pady=3)
        ttk.Label(box, text=" " + text, style="SurfaceMuted.TLabel",
                  font=FONTS["small"]).pack(side="left")

    def refresh(self):
        month = self.app.current_month.get()
        income, expense = self.db.totals_for_month(month)
        balance = income - expense
        self.m_income.configure(text=f"{income:,.2f}")
        self.m_expense.configure(text=f"{expense:,.2f}")
        self.m_balance.configure(
            text=f"{balance:,.2f}",
            foreground=COLORS["success"] if balance >= 0 else COLORS["danger"])

        rows = list(self.db.monthly_series(6))[::-1]
        self.chart.set_data([
            (datetime.strptime(r["month"], "%Y-%m").strftime("%b"),
             r["income"], r["expense"])
            for r in rows
        ])

        for widget in self.breakdown.winfo_children():
            widget.destroy()
        cats = self.db.spend_by_category(month)
        if not cats:
            ttk.Label(self.breakdown, text="No expenses recorded yet.",
                      style="SurfaceMuted.TLabel").pack(anchor="w")
            return
        total = sum(c["total"] for c in cats) or 1
        for c in cats[:6]:
            row = tk.Frame(self.breakdown, bg=COLORS["surface"])
            row.pack(fill="x", pady=5)
            top = tk.Frame(row, bg=COLORS["surface"])
            top.pack(fill="x")
            ttk.Label(top, text=c["name"], style="Surface.TLabel").pack(side="left")
            ttk.Label(top, text=f"{c['total']:,.0f}", style="SurfaceMuted.TLabel",
                      font=FONTS["small"]).pack(side="right")
            track = tk.Frame(row, bg=COLORS["surface_alt"], height=6)
            track.pack(fill="x", pady=(4, 0))
            tk.Frame(track, bg=c["color"] or COLORS["primary"], height=6).place(
                relwidth=max(0.02, c["total"] / total), relheight=1)
