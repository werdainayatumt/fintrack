"""Budgets & Categories screen: create/remove categories and set
per-category monthly spending limits with live progress bars."""
import tkinter as tk
from tkinter import messagebox, ttk

from components import MonthNav
from theme import COLORS, FONTS


class BudgetsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app
        self.db = app.db
        self._bcat_map = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Budgets & Categories", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        MonthNav(header, self.app.current_month, self.refresh).grid(
            row=0, column=1, sticky="e")

        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        body.columnconfigure(0, weight=0, minsize=320)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=COLORS["surface"])
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        self._build_category_panel(left)

        right = tk.Frame(body, bg=COLORS["surface"])
        right.grid(row=0, column=1, sticky="nsew")
        self._build_budget_panel(right)

    def _build_category_panel(self, parent):
        ttk.Label(parent, text="Categories", style="Heading.TLabel").pack(
            anchor="w", padx=18, pady=(16, 10))
        form = tk.Frame(parent, bg=COLORS["surface"])
        form.pack(fill="x", padx=18)
        ttk.Label(form, text="Name", style="SurfaceMuted.TLabel",
                  font=FONTS["small"]).pack(anchor="w")
        self.var_catname = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_catname).pack(fill="x", pady=(2, 8))
        ttk.Label(form, text="Type", style="SurfaceMuted.TLabel",
                  font=FONTS["small"]).pack(anchor="w")
        self.var_cattype = tk.StringVar(value="expense")
        trow = tk.Frame(form, bg=COLORS["surface"])
        trow.pack(fill="x", pady=(2, 8))
        ttk.Radiobutton(trow, text="Expense", value="expense",
                        variable=self.var_cattype).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(trow, text="Income", value="income",
                        variable=self.var_cattype).pack(side="left")
        ttk.Button(form, text="Add Category", style="Accent.TButton",
                   command=self._add_category).pack(anchor="w", pady=(4, 12))

        self.cat_list = tk.Frame(parent, bg=COLORS["surface"])
        self.cat_list.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    def _build_budget_panel(self, parent):
        ttk.Label(parent, text="Monthly Budgets", style="Heading.TLabel").pack(
            anchor="w", padx=18, pady=(16, 10))
        form = tk.Frame(parent, bg=COLORS["surface"])
        form.pack(fill="x", padx=18)
        ttk.Label(form, text="Category", style="SurfaceMuted.TLabel",
                  font=FONTS["small"]).grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(form, text="Limit", style="SurfaceMuted.TLabel",
                  font=FONTS["small"]).grid(row=0, column=1, sticky="w")
        self.var_bcat = tk.StringVar()
        self.cmb_bcat = ttk.Combobox(form, textvariable=self.var_bcat,
                                     state="readonly", width=18)
        self.cmb_bcat.grid(row=1, column=0, padx=(0, 8), pady=(2, 8))
        self.var_blimit = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_blimit, width=12).grid(
            row=1, column=1, pady=(2, 8))
        ttk.Button(form, text="Set Budget", style="Accent.TButton",
                   command=self._set_budget).grid(row=1, column=2, padx=8, pady=(2, 8))

        self.budget_list = tk.Frame(parent, bg=COLORS["surface"])
        self.budget_list.pack(fill="both", expand=True, padx=18, pady=(8, 16))

    # -------------------------------------------------------------- behaviour
    def _add_category(self):
        name = self.var_catname.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Enter a category name.")
            return
        try:
            self.db.add_category(name, self.var_cattype.get())
        except Exception:
            messagebox.showerror("Duplicate", f"Category '{name}' already exists.")
            return
        self.var_catname.set("")
        self.app.refresh_all()

    def _delete_category(self, cat_id, name):
        if messagebox.askyesno(
            "Delete category",
            f"Delete '{name}'?\nIts transactions are kept but become "
            "uncategorised, and related budgets are removed."):
            self.db.delete_category(cat_id)
            self.app.refresh_all()

    def _set_budget(self):
        cat_id = self._bcat_map.get(self.var_bcat.get())
        if cat_id is None:
            messagebox.showerror("No category", "Choose a category.")
            return
        try:
            limit = float(self.var_blimit.get())
            if limit <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid limit", "Enter a positive number.")
            return
        self.db.set_budget(cat_id, self.app.current_month.get(), limit)
        self.var_blimit.set("")
        self.app.refresh_all()

    def _remove_budget(self, budget_id):
        self.db.delete_budget(budget_id)
        self.app.refresh_all()

    def refresh(self):
        # category list
        for widget in self.cat_list.winfo_children():
            widget.destroy()
        for c in self.db.get_categories():
            row = tk.Frame(self.cat_list, bg=COLORS["surface"])
            row.pack(fill="x", pady=3)
            tk.Frame(row, bg=c["color"] or COLORS["primary"], width=10,
                     height=10).pack(side="left", pady=4)
            ttk.Label(row, text="  " + c["name"], style="Surface.TLabel").pack(
                side="left")
            ttk.Label(row, text=c["type"], style="SurfaceMuted.TLabel",
                      font=FONTS["small"]).pack(side="left", padx=8)
            ttk.Button(row, text="\u2715", width=3,
                       command=lambda i=c["id"], n=c["name"]:
                       self._delete_category(i, n)).pack(side="right")

        # budget category options (expense only)
        expense_cats = self.db.get_categories("expense")
        self._bcat_map = {c["name"]: c["id"] for c in expense_cats}
        self.cmb_bcat["values"] = list(self._bcat_map)
        if self._bcat_map and self.var_bcat.get() not in self._bcat_map:
            self.var_bcat.set(next(iter(self._bcat_map)))

        # budget rows
        for widget in self.budget_list.winfo_children():
            widget.destroy()
        budgets = self.db.get_budgets(self.app.current_month.get())
        if not budgets:
            ttk.Label(self.budget_list, text="No budgets set for this month.",
                      style="SurfaceMuted.TLabel").pack(anchor="w", pady=6)
            return
        for b in budgets:
            self._budget_row(b)

    def _budget_row(self, b):
        spent, limit = b["spent"], b["amount"]
        over = spent > limit
        pct = min(1.0, spent / limit) if limit else 0
        row = tk.Frame(self.budget_list, bg=COLORS["surface"])
        row.pack(fill="x", pady=7)
        top = tk.Frame(row, bg=COLORS["surface"])
        top.pack(fill="x")
        ttk.Label(top, text=b["name"], style="Surface.TLabel",
                  font=FONTS["subhead"]).pack(side="left")
        ttk.Button(top, text="Remove", command=lambda i=b["id"]:
                   self._remove_budget(i)).pack(side="right")
        ttk.Label(top, text=f"{spent:,.0f} / {limit:,.0f}",
                  style="SurfaceMuted.TLabel", font=FONTS["small"],
                  foreground=COLORS["danger"] if over else COLORS["text_muted"]).pack(
            side="right", padx=8)
        track = tk.Frame(row, bg=COLORS["surface_alt"], height=8)
        track.pack(fill="x", pady=(5, 0))
        tk.Frame(track, bg=COLORS["danger"] if over else COLORS["success"],
                 height=8).place(relwidth=max(0.02, pct), relheight=1)
