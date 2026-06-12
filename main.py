"""FinTrack - a personal finance manager built with Tkinter + SQLite.

Run with:  python main.py

This module builds the main window, the sidebar navigation, and hosts
the four feature screens. Each screen is an independent module so team
members can work on them in parallel on separate branches.
"""
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from database import Database
from theme import COLORS, FONTS, apply_theme
from screens.dashboard import DashboardScreen
from screens.transactions import TransactionsScreen
from screens.budgets import BudgetsScreen
from screens.reports import ReportsScreen


class FinTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FinTrack \u2014 Personal Finance Manager")
        self.geometry("1080x680")
        self.minsize(920, 600)

        self.db = Database()
        apply_theme(self)

        # Shared application state: the month every screen reads from.
        self.current_month = tk.StringVar(value=datetime.now().strftime("%Y-%m"))

        self._build_layout()
        self.show_screen("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=210)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ttk.Label(sidebar, text="  \u25c6 FinTrack", style="Sidebar.TLabel",
                  font=FONTS["title"], foreground=COLORS["primary"]).pack(
            fill="x", pady=(22, 26), padx=4)

        self.nav_buttons = {}
        nav_items = (("dashboard", "  Dashboard"),
                     ("transactions", "  Transactions"),
                     ("budgets", "  Budgets"),
                     ("reports", "  Reports"))
        for key, label in nav_items:
            btn = ttk.Button(sidebar, text=label, style="Nav.TButton",
                             command=lambda k=key: self.show_screen(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        ttk.Label(sidebar, text="OSSD Final Project\nTkinter + SQLite",
                  style="Sidebar.TLabel", foreground=COLORS["text_muted"],
                  font=FONTS["small"], justify="left").pack(
            side="bottom", fill="x", padx=18, pady=16)

        container = ttk.Frame(self)
        container.grid(row=0, column=1, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.screens = {}
        screen_classes = {"dashboard": DashboardScreen,
                          "transactions": TransactionsScreen,
                          "budgets": BudgetsScreen,
                          "reports": ReportsScreen}
        for key, cls in screen_classes.items():
            screen = cls(container, self)
            screen.grid(row=0, column=0, sticky="nsew")
            self.screens[key] = screen

    def show_screen(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(style="NavActive.TButton" if k == key else "Nav.TButton")
        screen = self.screens[key]
        screen.tkraise()
        screen.refresh()

    def refresh_all(self):
        for screen in self.screens.values():
            screen.refresh()

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    FinTrackApp().mainloop()
