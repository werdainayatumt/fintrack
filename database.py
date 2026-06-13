"""SQLite data-access layer for FinTrack.

Every read/write to storage lives here so the UI modules stay
storage-agnostic. Swapping SQLite for another backend would only
require changing this file.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fintrack.db")


class Database:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_schema()
        self._seed_defaults()

    # ------------------------------------------------------------------ schema
    def _create_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL UNIQUE,
                type  TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                color TEXT NOT NULL DEFAULT '#4f9eff'
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                amount      REAL NOT NULL,
                type        TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category_id INTEGER,
                note        TEXT DEFAULT '',
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                month       TEXT NOT NULL,
                amount      REAL NOT NULL,
                UNIQUE (category_id, month),
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def _seed_defaults(self):
        cur = self.conn.execute("SELECT COUNT(*) AS n FROM categories")
        if cur.fetchone()["n"] == 0:
            defaults = [
                ("Salary",        "income",  "#3ecf8e"),
                ("Freelance",     "income",  "#4f9eff"),
                ("Groceries",     "expense", "#f5b945"),
                ("Rent",          "expense", "#ff5d5d"),
                ("Utilities",     "expense", "#9d7bff"),
                ("Transport",     "expense", "#5dd3ff"),
                ("Entertainment", "expense", "#ff8fb3"),
            ]
            self.conn.executemany(
                "INSERT INTO categories (name, type, color) VALUES (?, ?, ?)", defaults
            )
            self.conn.commit()

    # -------------------------------------------------------------- categories
    def get_categories(self, type_=None):
        q = "SELECT * FROM categories"
        params = ()
        if type_:
            q += " WHERE type = ?"
            params = (type_,)
        q += " ORDER BY name"
        return self.conn.execute(q, params).fetchall()

    def add_category(self, name, type_, color="#4f9eff"):
        self.conn.execute(
            "INSERT INTO categories (name, type, color) VALUES (?, ?, ?)",
            (name, type_, color),
        )
        self.conn.commit()

    def delete_category(self, cat_id):
        self.conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        self.conn.commit()

    # ------------------------------------------------------------ transactions
    def add_transaction(self, date, amount, type_, category_id, note=""):
        self.conn.execute(
            "INSERT INTO transactions (date, amount, type, category_id, note) "
            "VALUES (?, ?, ?, ?, ?)",
            (date, amount, type_, category_id, note),
        )
        self.conn.commit()

    def update_transaction(self, tx_id, date, amount, type_, category_id, note=""):
        self.conn.execute(
            "UPDATE transactions SET date = ?, amount = ?, type = ?, "
            "category_id = ?, note = ? WHERE id = ?",
            (date, amount, type_, category_id, note, tx_id),
        )
        self.conn.commit()

    def delete_transaction(self, tx_id):
        self.conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        self.conn.commit()

    def get_transactions(self, month=None, type_=None, category_id=None):
        q = """
            SELECT t.*, c.name AS category_name, c.color AS category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1 = 1
        """
        params = []
        if month:
            q += " AND substr(t.date, 1, 7) = ?"
            params.append(month)
        if type_:
            q += " AND t.type = ?"
            params.append(type_)
        if category_id:
            q += " AND t.category_id = ?"
            params.append(category_id)
        q += " ORDER BY t.date DESC, t.id DESC"
        return self.conn.execute(q, params).fetchall()

    # --------------------------------------------------------------- aggregates
    def totals_for_month(self, month):
        row = self.conn.execute(
            """
            SELECT
              COALESCE(SUM(CASE WHEN type = 'income'  THEN amount END), 0) AS income,
              COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) AS expense
            FROM transactions
            WHERE substr(date, 1, 7) = ?
            """,
            (month,),
        ).fetchone()
        return row["income"], row["expense"]

    def spend_by_category(self, month):
        return self.conn.execute(
            """
            SELECT c.name AS name, c.color AS color, SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense' AND substr(t.date, 1, 7) = ?
            GROUP BY c.id
            ORDER BY total DESC
            """,
            (month,),
        ).fetchall()

    def monthly_series(self, n=6):
        return self.conn.execute(
            """
            SELECT substr(date, 1, 7) AS month,
                   COALESCE(SUM(CASE WHEN type = 'income'  THEN amount END), 0) AS income,
                   COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) AS expense
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
            """,
            (n,),
        ).fetchall()

    # ------------------------------------------------------------------ budgets
    def set_budget(self, category_id, month, amount):
        self.conn.execute(
            """
            INSERT INTO budgets (category_id, month, amount) VALUES (?, ?, ?)
            ON CONFLICT(category_id, month) DO UPDATE SET amount = excluded.amount
            """,
            (category_id, month, amount),
        )
        self.conn.commit()

    def get_budgets(self, month):
        return self.conn.execute(
            """
            SELECT b.id, b.amount, b.month, c.id AS category_id, c.name, c.color,
                   COALESCE((
                     SELECT SUM(t.amount) FROM transactions t
                     WHERE t.category_id = c.id AND t.type = 'expense'
                       AND substr(t.date, 1, 7) = b.month
                   ), 0) AS spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.month = ?
            ORDER BY c.name
            """,
            (month,),
        ).fetchall()

    def delete_budget(self, budget_id):
        self.conn.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
