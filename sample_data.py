"""Load fictional sample data so the program can be demonstrated.

    python sample_data.py            loads 14 days (17-10-2026 to 30-10-2026)
    python sample_data.py --today    loads the 14 days ending today instead

All names and numbers are made up. Existing meals and workouts are kept,
so delete fitness_tracker.db first if you want a clean start.
"""

import os
import sys
from datetime import date, timedelta

from database import Database
from tracker import FitnessTracker

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness_tracker.db")
LAST_DAY = date(2026, 10, 30)

PROFILE = ("Sample Student", "19", "Female", "162", "60",
           "Lightly active (1-3 days a week)", "Lose weight")

# One entry per day, oldest first: (meals, workouts).
# meals = [(meal type, food, servings)], workouts = [(activity, minutes)]
DAYS = [
    ([("Breakfast", "Poha", 1), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Dal (cooked)", 1),
      ("Snack", "Banana", 1), ("Snack", "Tea with sugar", 1), ("Dinner", "Roti (chapati)", 2),
      ("Dinner", "Paneer curry", 1)],
     [("Walking (brisk)", 30)]),
    ([("Breakfast", "Idli", 3), ("Lunch", "Boiled rice", 1), ("Lunch", "Rajma", 1),
      ("Snack", "Apple", 1), ("Dinner", "Roti (chapati)", 2), ("Dinner", "Mixed vegetable curry", 1)],
     [("Yoga", 40)]),
    ([("Breakfast", "Oats porridge", 1), ("Lunch", "Veg sandwich", 1), ("Snack", "Almonds", 1),
      ("Dinner", "Roti (chapati)", 2), ("Dinner", "Dal (cooked)", 1)],
     [("Jogging", 30)]),
    ([("Breakfast", "Aloo paratha", 1), ("Lunch", "Boiled rice", 1), ("Lunch", "Chicken curry", 1),
      ("Snack", "Samosa", 1), ("Dinner", "Pizza slice", 2)],
     []),
    ([("Breakfast", "Omelette", 1), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Mixed vegetable curry", 1),
      ("Snack", "Banana", 1), ("Dinner", "Roti (chapati)", 1), ("Dinner", "Dal (cooked)", 1)],
     [("Cycling", 30)]),
    ([("Breakfast", "Idli", 2), ("Lunch", "Boiled rice", 1), ("Lunch", "Dal (cooked)", 1),
      ("Snack", "Tea with sugar", 1), ("Snack", "Banana", 1), ("Dinner", "Veg sandwich", 1)],
     [("Walking (brisk)", 45)]),
    ([("Breakfast", "Upma", 1), ("Lunch", "Roti (chapati)", 3), ("Lunch", "Paneer curry", 1),
      ("Snack", "Apple", 1), ("Snack", "Almonds", 1), ("Dinner", "Boiled rice", 1),
      ("Dinner", "Rajma", 1)],
     [("Gym workout", 40)]),
    ([("Breakfast", "Dosa (plain)", 2), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Chicken curry", 1),
      ("Snack", "Milk (toned)", 1), ("Dinner", "Pizza slice", 2), ("Dinner", "Cold drink", 1)],
     [("Badminton", 30)]),
    ([("Breakfast", "Oats porridge", 1), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Dal (cooked)", 1),
      ("Snack", "Banana", 1), ("Dinner", "Roti (chapati)", 2), ("Dinner", "Mixed vegetable curry", 1)],
     [("Jogging", 25)]),
    ([("Breakfast", "Poha", 1), ("Lunch", "Boiled rice", 1), ("Lunch", "Rajma", 1),
      ("Snack", "Curd", 1), ("Dinner", "Veg sandwich", 1)],
     [("Yoga", 30)]),
    ([("Breakfast", "Aloo paratha", 1), ("Breakfast", "Tea with sugar", 1),
      ("Lunch", "Boiled rice", 1), ("Lunch", "Paneer curry", 1), ("Snack", "Samosa", 1),
      ("Dinner", "Roti (chapati)", 2), ("Dinner", "Chicken curry", 1)],
     []),
    ([("Breakfast", "Idli", 3), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Dal (cooked)", 1),
      ("Snack", "Apple", 1), ("Dinner", "Roti (chapati)", 2), ("Dinner", "Mixed vegetable curry", 1)],
     [("Walking (brisk)", 40), ("Stretching", 15)]),
    ([("Breakfast", "Omelette", 1), ("Lunch", "Veg sandwich", 1), ("Snack", "Banana", 1),
      ("Dinner", "Roti (chapati)", 2), ("Dinner", "Paneer curry", 1)],
     [("Skipping rope", 15)]),
    ([("Breakfast", "Oats porridge", 1), ("Lunch", "Roti (chapati)", 2), ("Lunch", "Rajma", 1),
      ("Snack", "Almonds", 1), ("Snack", "Veg sandwich", 1), ("Dinner", "Roti (chapati)", 2),
      ("Dinner", "Dal (cooked)", 1)],
     [("Cycling", 30)]),
]

# (days before the last day, weight in kg)
WEIGHTS = [(13, 60.0), (11, 59.8), (8, 59.9), (6, 59.6), (4, 59.5), (2, 59.4), (0, 59.2)]


def load(db, last_day=LAST_DAY):
    """Fill the database. Returns the number of meals and workouts added."""
    tracker = FitnessTracker(db, today=lambda: last_day)
    first_day = last_day - timedelta(days=len(DAYS) - 1)
    # the profile is saved with the first weight, on the first day
    tracker.today = lambda: first_day
    ok, message = tracker.save_profile(*PROFILE)
    assert ok, message
    tracker.today = lambda: last_day
    for ago, weight in WEIGHTS:
        day = (last_day - timedelta(days=ago)).strftime("%d-%m-%Y")
        assert tracker.add_weight(day, str(weight))[0]
    meals = workouts = 0
    for offset, (day_meals, day_workouts) in enumerate(DAYS):
        day = (first_day + timedelta(days=offset)).strftime("%d-%m-%Y")
        for meal_type, food, servings in day_meals:
            assert tracker.add_meal(day, meal_type, food, str(servings))[0]
            meals += 1
        for activity, minutes in day_workouts:
            assert tracker.add_workout(day, activity, str(minutes))[0]
            workouts += 1
    return meals, workouts


if __name__ == "__main__":
    end = date.today() if "--today" in sys.argv else LAST_DAY
    database = Database(DB_FILE)
    added = load(database, end)
    database.close()
    print(f"Sample data loaded: {added[0]} meals and {added[1]} workouts, "
          f"ending {end.strftime('%d-%m-%Y')}.")
