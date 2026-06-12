"""Optional helper: fill the database with realistic sample data so the
charts and reports have something to show (handy for screenshots).

Run once:  python seed.py
"""
import random
from datetime import datetime, timedelta

from database import Database


def run():
    db = Database()
    cats = {c["name"]: c["id"] for c in db.get_categories()}
    today = datetime.now()

    for offset in range(60, -1, -1):
        day = today - timedelta(days=offset)
        date = day.strftime("%Y-%m-%d")
        if day.day in (1, 15):
            db.add_transaction(date, random.choice([120000, 135000]), "income",
                               cats.get("Salary"), "Monthly salary")
        if random.random() < 0.55:
            name = random.choice(["Groceries", "Transport",
                                  "Entertainment", "Utilities"])
            db.add_transaction(date, round(random.uniform(500, 6000), -1),
                               "expense", cats.get(name), "")

    months = {today.strftime("%Y-%m"),
              (today - timedelta(days=40)).strftime("%Y-%m")}
    for month in months:
        db.add_transaction(f"{month}-03", 45000, "expense",
                           cats.get("Rent"), "Apartment rent")

    current = today.strftime("%Y-%m")
    for name, limit in (("Groceries", 20000), ("Transport", 12000),
                        ("Entertainment", 8000), ("Utilities", 10000)):
        if cats.get(name):
            db.set_budget(cats[name], current, limit)

    db.close()
    print("Sample data inserted. Launch the app with: python main.py")


if __name__ == "__main__":
    run()
