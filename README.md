# FinTrack — Personal Finance Manager

A desktop personal-finance tracker built with **Python Tkinter** and **SQLite**.
Add income and expenses, set monthly category budgets, visualise spending trends,
and export data to CSV — all from a dark-themed, responsive GUI that runs on
Windows, macOS, and Linux with zero third-party dependencies.

> **OSSD Final-Term Project** — Collaborative Tkinter GUI App with GitHub-Based Version Control

---

## Features

| Module | What it does |
|---|---|
| **Dashboard** | Month-at-a-glance metric cards (income / expenses / balance), a native 6-month bar chart, and a category spending breakdown |
| **Transactions** | Add, edit, and delete income or expense entries with date, category, amount, and notes; filterable history table |
| **Budgets & Categories** | Create / remove categories (income or expense); set per-category monthly spending limits with live progress bars |
| **Reports** | Monthly summary strip, category breakdown table, and one-click CSV export |

### Additional highlights

- Shared month selector — changing the month on any screen updates all others
- Responsive layouts using `grid` weights and `pack` fill/expand
- Dark theme with a centralised design-token system (`theme.py`)
- Modular architecture: each screen is an independent file, ideal for branch-per-feature collaboration

---

## Tools & Technologies

| Layer | Technology |
|---|---|
| Frontend / GUI | Python 3 + Tkinter (standard library) |
| Backend / Storage | SQLite 3 via `sqlite3` (standard library) |
| Version Control | Git + GitHub |
| Export | CSV (standard library `csv` module) |

No external packages are needed — `requirements.txt` is included for clarity.

---

## Setup & Running

### Prerequisites

- **Python 3.8+** (Windows / macOS installers bundle Tkinter)
- On Debian / Ubuntu, install Tkinter if missing:
  ```bash
  sudo apt install python3-tk
  ```

### Quick start

```bash
# 1. Clone the repository
git clone https://github.com/werdainayatumt/fintrack.git
cd fintrack

# 2. (Optional) Populate sample data for demo / screenshots
python seed.py

# 3. Launch the app
python main.py
```

The SQLite database (`fintrack.db`) is created automatically on first run.

---

## Screenshots

> _Replace these placeholders with actual screenshots of the running app._

| Dashboard | Transactions | Budgets | Reports |
|---|---|---|---|
| ![Dashboard](screenshots/dashboard.png) | ![Transactions](screenshots/transactions.png) | ![Budgets](screenshots/budgets.png) | ![Reports](screenshots/reports.png) |

---

## Project Structure

```
fintrack/
├── main.py              # Entry point — window shell & sidebar navigation
├── database.py          # SQLite data-access layer (all CRUD + aggregates)
├── theme.py             # Centralised palette, fonts, and ttk style config
├── components.py        # Reusable widgets (MonthNav selector)
├── seed.py              # Optional: populate sample data for demos
├── screens/
│   ├── __init__.py
│   ├── dashboard.py     # Dashboard screen (metrics, bar chart, breakdown)
│   ├── transactions.py  # Transactions screen (form + history table)
│   ├── budgets.py       # Budgets & Categories screen
│   └── reports.py       # Reports screen (summary, table, CSV export)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Contribution Credits

| Member | GitHub | Role | Key Contributions |
|---|---|---|---|
| **Werda Inayat** (Group Lead) | [@werdainayatumt](https://github.com/werdainayatumt) | Project coordination, main shell | `main.py`, `theme.py`, `components.py`, `seed.py`, README |
| **Abdul Manan** | [@abdulmananumt](https://github.com/abdulmananumt) | Backend & Transactions | `database.py` (full SQLite layer), `screens/transactions.py`, form validation |
| **Arzo Fatima** | [@arzoo12341191](https://github.com/arzoo12341191) | UI Screens | `screens/dashboard.py` (BarChart widget), `screens/budgets.py`, `screens/reports.py`, CSV export |

---

## Key Pull Requests

| # | Title | Author |
|---|---|---|
| #1 | Initial project scaffold: main window, theme system, sidebar nav | Werda Inayat |
| #2 | SQLite data-access layer | Abdul Manan |
| #3 | Dashboard screen with bar chart | Arzo Fatima |
| #4 | Transactions CRUD screen | Abdul Manan |
| #5 | Budgets & Categories screen | Arzo Fatima |
| #6 | Reports screen with CSV export | Arzo Fatima |
| #7 | README polish and final cleanup | Werda Inayat |

---

## Backend / Database

FinTrack uses **SQLite 3** through Python's built-in `sqlite3` module.
The database file (`fintrack.db`) is created beside `main.py` on first launch.

### Schema

- **categories** — id, name (unique), type (income | expense), color
- **transactions** — id, date, amount, type, category_id (FK), note
- **budgets** — id, category_id (FK), month, amount (unique per category+month)

Foreign keys are enforced (`PRAGMA foreign_keys = ON`).
Default categories are seeded on first run; users can add or remove them freely.

---

## License

This project is released for academic purposes under the [MIT License](LICENSE).
