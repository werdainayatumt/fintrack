"""Transactions screen: a form to add or edit entries and a
Treeview history of the selected month with delete support."""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from components import MonthNav
from theme import COLORS, FONTS


class TransactionsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app
        self.db = app.db
        self.editing_id = None
        self._rows = []
        self._cat_map = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Transactions", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        MonthNav(header, self.app.current_month, self.refresh).grid(
            row=0, column=1, sticky="e")

        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        form = tk.Frame(body, bg=COLORS["surface"])
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        self._build_form(form)

        listcard = tk.Frame(body, bg=COLORS["surface"])
        listcard.grid(row=0, column=1, sticky="nsew")
        self._build_list(listcard)

    def _build_form(self, parent):
        self.form_title = ttk.Label(parent, text="Add Transaction",
                                    style="Heading.TLabel")
        self.form_title.pack(anchor="w", padx=18, pady=(16, 12))
        wrap = tk.Frame(parent, bg=COLORS["surface"])
        wrap.pack(fill="x", padx=18)

        def label(text):
            ttk.Label(wrap, text=text, style="SurfaceMuted.TLabel",
                      font=FONTS["small"]).pack(anchor="w", pady=(8, 2))

        label("Date (YYYY-MM-DD)")
        self.var_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(wrap, textvariable=self.var_date).pack(fill="x")

        label("Type")
        self.var_type = tk.StringVar(value="expense")
        type_row = tk.Frame(wrap, bg=COLORS["surface"])
        type_row.pack(fill="x")
        ttk.Radiobutton(type_row, text="Expense", value="expense",
                        variable=self.var_type,
                        command=self._reload_categories).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(type_row, text="Income", value="income",
                        variable=self.var_type,
                        command=self._reload_categories).pack(side="left")

        label("Category")
        self.var_category = tk.StringVar()
        self.cmb_category = ttk.Combobox(wrap, textvariable=self.var_category,
                                         state="readonly")
        self.cmb_category.pack(fill="x")

        label("Amount")
        self.var_amount = tk.StringVar()
        ttk.Entry(wrap, textvariable=self.var_amount).pack(fill="x")

        label("Note (optional)")
        self.var_note = tk.StringVar()
        ttk.Entry(wrap, textvariable=self.var_note).pack(fill="x")

        btns = tk.Frame(parent, bg=COLORS["surface"])
        btns.pack(fill="x", padx=18, pady=16)
        self.btn_save = ttk.Button(btns, text="Add", style="Accent.TButton",
                                   command=self._save)
        self.btn_save.pack(side="left")
        ttk.Button(btns, text="Clear", command=self._reset_form).pack(
            side="left", padx=8)

    def _build_list(self, parent):
        bar = tk.Frame(parent, bg=COLORS["surface"])
        bar.pack(fill="x", padx=18, pady=(16, 8))
        ttk.Label(bar, text="History", style="Heading.TLabel").pack(side="left")
        ttk.Button(bar, text="Delete", style="Danger.TButton",
                   command=self._delete).pack(side="right")
        ttk.Button(bar, text="Edit", command=self._load_for_edit).pack(
            side="right", padx=8)

        cols = ("date", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings",
                                 selectmode="browse")
        headings = {"date": "Date", "type": "Type", "category": "Category",
                    "amount": "Amount", "note": "Note"}
        widths = {"date": 100, "type": 80, "category": 130, "amount": 110, "note": 180}
        for col in cols:
            self.tree.heading(col, text=headings[col])
            anchor = "w" if col in ("category", "note") else "center"
            self.tree.column(col, width=widths[col], anchor=anchor)
        self.tree.column("amount", anchor="e")
        self.tree.tag_configure("income", foreground=COLORS["success"])
        self.tree.tag_configure("expense", foreground=COLORS["text"])

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(18, 0),
                       pady=(0, 16))
        vsb.pack(side="right", fill="y", padx=(0, 18), pady=(0, 16))

    # -------------------------------------------------------------- behaviour
    def _reload_categories(self):
        cats = self.db.get_categories(self.var_type.get())
        self._cat_map = {c["name"]: c["id"] for c in cats}
        self.cmb_category["values"] = list(self._cat_map)
        if self._cat_map and self.var_category.get() not in self._cat_map:
            self.var_category.set(next(iter(self._cat_map)))
        elif not self._cat_map:
            self.var_category.set("")

    def _save(self):
        date = self.var_date.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Use the format YYYY-MM-DD.")
            return
        try:
            amount = float(self.var_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a positive number.")
            return
        cat_id = self._cat_map.get(self.var_category.get())
        if cat_id is None:
            messagebox.showerror("No category",
                                 "Add a category first on the Budgets tab.")
            return

        note = self.var_note.get().strip()
        type_ = self.var_type.get()
        if self.editing_id:
            self.db.update_transaction(self.editing_id, date, amount, type_,
                                       cat_id, note)
        else:
            self.db.add_transaction(date, amount, type_, cat_id, note)

        self.app.current_month.set(date[:7])  # jump view to the entry's month
        self._reset_form()
        self.app.refresh_all()

    def _reset_form(self):
        self.editing_id = None
        self.form_title.configure(text="Add Transaction")
        self.btn_save.configure(text="Add")
        self.var_amount.set("")
        self.var_note.set("")
        self.var_date.set(datetime.now().strftime("%Y-%m-%d"))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _load_for_edit(self):
        tx_id = self._selected_id()
        if tx_id is None:
            return
        row = next((r for r in self._rows if r["id"] == tx_id), None)
        if row is None:
            return
        self.editing_id = tx_id
        self.var_type.set(row["type"])
        self._reload_categories()
        self.var_date.set(row["date"])
        self.var_amount.set(f"{row['amount']:.2f}")
        self.var_note.set(row["note"] or "")
        if row["category_name"]:
            self.var_category.set(row["category_name"])
        self.form_title.configure(text="Edit Transaction")
        self.btn_save.configure(text="Update")

    def _delete(self):
        tx_id = self._selected_id()
        if tx_id is None:
            return
        if messagebox.askyesno("Delete", "Delete the selected transaction?"):
            self.db.delete_transaction(tx_id)
            if self.editing_id == tx_id:
                self._reset_form()
            self.app.refresh_all()

    def refresh(self):
        self._reload_categories()
        self._rows = self.db.get_transactions(month=self.app.current_month.get())
        self.tree.delete(*self.tree.get_children())
        for r in self._rows:
            self.tree.insert(
                "", "end", iid=str(r["id"]),
                values=(r["date"], r["type"].capitalize(),
                        r["category_name"] or "\u2014", f"{r['amount']:,.2f}",
                        r["note"] or ""),
                tags=(r["type"],))
