"""Reports screen: monthly summary figures, a category breakdown
table, and CSV export of the selected month's transactions."""
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from components import MonthNav
from theme import COLORS, FONTS


class ReportsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app
        self.db = app.db
        self._summary = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Reports", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        right = ttk.Frame(header)
        right.grid(row=0, column=1, sticky="e")
        MonthNav(right, self.app.current_month, self.refresh).pack(
            side="left", padx=(0, 12))
        ttk.Button(right, text="Export CSV", style="Accent.TButton",
                   command=self._export).pack(side="left")

        strip = tk.Frame(self, bg=COLORS["surface"])
        strip.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        for i, key in enumerate(("Income", "Expenses", "Balance", "Savings Rate")):
            strip.columnconfigure(i, weight=1)
            cell = tk.Frame(strip, bg=COLORS["surface"])
            cell.grid(row=0, column=i, sticky="ew", padx=20, pady=16)
            ttk.Label(cell, text=key, style="SurfaceMuted.TLabel",
                      font=FONTS["small"]).pack(anchor="w")
            value = ttk.Label(cell, text="\u2014", style="Surface.TLabel",
                              font=FONTS["heading"])
            value.pack(anchor="w")
            self._summary[key] = value

        table_card = tk.Frame(self, bg=COLORS["surface"])
        table_card.grid(row=2, column=0, sticky="nsew", padx=24, pady=8)
        ttk.Label(table_card, text="Category Breakdown", style="Heading.TLabel").pack(
            anchor="w", padx=18, pady=(16, 8))
        cols = ("category", "amount", "share")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")
        for col, text, width in (("category", "Category", 220),
                                 ("amount", "Amount", 150),
                                 ("share", "Share", 100)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width,
                             anchor="w" if col == "category" else "e")
        self.tree.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    def refresh(self):
        month = self.app.current_month.get()
        income, expense = self.db.totals_for_month(month)
        balance = income - expense
        rate = (balance / income * 100) if income > 0 else 0
        self._summary["Income"].configure(text=f"{income:,.2f}",
                                          foreground=COLORS["success"])
        self._summary["Expenses"].configure(text=f"{expense:,.2f}",
                                            foreground=COLORS["danger"])
        self._summary["Balance"].configure(
            text=f"{balance:,.2f}",
            foreground=COLORS["success"] if balance >= 0 else COLORS["danger"])
        self._summary["Savings Rate"].configure(text=f"{rate:.1f}%",
                                                foreground=COLORS["primary"])

        cats = self.db.spend_by_category(month)
        total = sum(c["total"] for c in cats) or 1
        self.tree.delete(*self.tree.get_children())
        for c in cats:
            self.tree.insert("", "end", values=(
                c["name"], f"{c['total']:,.2f}", f"{c['total'] / total * 100:.1f}%"))

    def _export(self):
        month = self.app.current_month.get()
        rows = self.db.get_transactions(month=month)
        if not rows:
            messagebox.showinfo("Nothing to export",
                                "No transactions for this month.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"fintrack_{month}.csv",
            filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Date", "Type", "Category", "Amount", "Note"])
            for r in rows:
                writer.writerow([r["date"], r["type"], r["category_name"] or "",
                                 f"{r['amount']:.2f}", r["note"] or ""])
        messagebox.showinfo("Exported",
                            f"Saved {len(rows)} transactions to:\n{path}")
