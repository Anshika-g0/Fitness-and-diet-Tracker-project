"""SQLite data layer. This is the only module that contains SQL."""

import sqlite3
from datetime import timedelta

from utils import MEAL_TYPES

# (food name, calories per serving, serving size). Approximate values.
FOODS = [
    ("Roti (chapati)", 100, "1 piece"),
    ("Boiled rice", 205, "1 cup"),
    ("Dal (cooked)", 180, "1 bowl"),
    ("Rajma", 210, "1 bowl"),
    ("Paneer curry", 260, "1 bowl"),
    ("Mixed vegetable curry", 120, "1 bowl"),
    ("Chicken curry", 240, "1 bowl"),
    ("Idli", 60, "1 piece"),
    ("Dosa (plain)", 130, "1 piece"),
    ("Poha", 250, "1 plate"),
    ("Upma", 220, "1 plate"),
    ("Aloo paratha", 290, "1 piece"),
    ("Egg (boiled)", 78, "1 egg"),
    ("Omelette", 154, "2 eggs"),
    ("Oats porridge", 150, "1 bowl"),
    ("Milk (toned)", 120, "1 glass"),
    ("Curd", 100, "1 bowl"),
    ("Banana", 105, "1 medium"),
    ("Apple", 95, "1 medium"),
    ("Almonds", 165, "1 handful"),
    ("Veg sandwich", 250, "1 sandwich"),
    ("Samosa", 260, "1 piece"),
    ("Pizza slice", 285, "1 slice"),
    ("Tea with sugar", 60, "1 cup"),
    ("Cold drink", 150, "1 glass"),
]

# (activity name, MET value). MET = metabolic equivalent of task.
ACTIVITIES = [
    ("Walking (brisk)", 3.8),
    ("Jogging", 7.0),
    ("Running", 9.8),
    ("Cycling", 7.5),
    ("Swimming", 8.0),
    ("Yoga", 2.5),
    ("Stretching", 2.3),
    ("Skipping rope", 11.0),
    ("Gym workout", 6.0),
    ("Badminton", 5.5),
    ("Dancing", 5.0),
    ("Stair climbing", 8.8),
]


class Database:
    """Opens the SQLite file, creates the tables and runs every query."""

    def __init__(self, path="fitness_tracker.db"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
        self.seed_reference_data()

    def close(self):
        self.conn.close()

    # ------------------------------------------------------------- set-up
    def create_tables(self):
        types = ", ".join(f"'{m}'" for m in MEAL_TYPES)
        self.conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS profile (
            profile_id INTEGER PRIMARY KEY CHECK (profile_id = 1),
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK (age BETWEEN 10 AND 100),
            gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female')),
            height_cm REAL NOT NULL CHECK (height_cm > 0),
            activity TEXT NOT NULL,
            goal TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS foods (
            food_id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL UNIQUE,
            calories REAL NOT NULL CHECK (calories >= 0),
            serving TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS activities (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT NOT NULL UNIQUE,
            met REAL NOT NULL CHECK (met > 0)
        );
        CREATE TABLE IF NOT EXISTS meals (
            meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK (meal_type IN ({types})),
            food_id INTEGER NOT NULL,
            servings REAL NOT NULL CHECK (servings > 0),
            calories REAL NOT NULL CHECK (calories >= 0),
            FOREIGN KEY (food_id) REFERENCES foods (food_id)
        );
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            activity_id INTEGER NOT NULL,
            minutes INTEGER NOT NULL CHECK (minutes > 0),
            calories_burned REAL NOT NULL CHECK (calories_burned >= 0),
            FOREIGN KEY (activity_id) REFERENCES activities (activity_id)
        );
        CREATE TABLE IF NOT EXISTS weights (
            log_date TEXT PRIMARY KEY,
            weight_kg REAL NOT NULL CHECK (weight_kg > 0)
        );
        """)
        self.conn.commit()

    def seed_reference_data(self):
        """Insert the food and activity lists the first time only."""
        self.conn.executemany(
            "INSERT OR IGNORE INTO foods (food_name, calories, serving) VALUES (?, ?, ?)",
            FOODS)
        self.conn.executemany(
            "INSERT OR IGNORE INTO activities (activity_name, met) VALUES (?, ?)",
            ACTIVITIES)
        self.conn.commit()

    # ------------------------------------------------------------ profile
    def save_profile(self, name, age, gender, height_cm, activity, goal):
        self.conn.execute("""
            INSERT INTO profile (profile_id, name, age, gender, height_cm, activity, goal)
            VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(profile_id) DO UPDATE SET
                name = excluded.name, age = excluded.age, gender = excluded.gender,
                height_cm = excluded.height_cm, activity = excluded.activity,
                goal = excluded.goal
        """, (name, age, gender, height_cm, activity, goal))
        self.conn.commit()

    def get_profile(self):
        row = self.conn.execute(
            "SELECT name, age, gender, height_cm, activity, goal FROM profile WHERE profile_id = 1"
        ).fetchone()
        if row is None:
            return None
        keys = ("name", "age", "gender", "height_cm", "activity", "goal")
        return dict(zip(keys, row))

    # ----------------------------------------------------- reference data
    def get_foods(self):
        return self.conn.execute(
            "SELECT food_id, food_name, calories, serving FROM foods ORDER BY food_name").fetchall()

    def get_food(self, name):
        return self.conn.execute(
            "SELECT food_id, food_name, calories, serving FROM foods WHERE food_name = ?",
            (name,)).fetchone()

    def get_activities(self):
        return self.conn.execute(
            "SELECT activity_id, activity_name, met FROM activities ORDER BY activity_name").fetchall()

    def get_activity(self, name):
        return self.conn.execute(
            "SELECT activity_id, activity_name, met FROM activities WHERE activity_name = ?",
            (name,)).fetchone()

    # -------------------------------------------------------------- meals
    def add_meal(self, log_date, meal_type, food_id, servings, calories):
        cur = self.conn.execute(
            "INSERT INTO meals (log_date, meal_type, food_id, servings, calories) "
            "VALUES (?, ?, ?, ?, ?)",
            (log_date.isoformat(), meal_type, food_id, servings, calories))
        self.conn.commit()
        return cur.lastrowid

    def get_meals(self, log_date):
        """Meals of one day, in the order Breakfast, Lunch, Snack, Dinner."""
        return self.conn.execute("""
            SELECT m.meal_id, m.meal_type, f.food_name, m.servings, m.calories
            FROM meals m JOIN foods f ON f.food_id = m.food_id
            WHERE m.log_date = ?
            ORDER BY CASE m.meal_type WHEN 'Breakfast' THEN 1 WHEN 'Lunch' THEN 2
                     WHEN 'Snack' THEN 3 ELSE 4 END, m.meal_id
        """, (log_date.isoformat(),)).fetchall()

    def delete_meal(self, meal_id):
        cur = self.conn.execute("DELETE FROM meals WHERE meal_id = ?", (meal_id,))
        self.conn.commit()
        return cur.rowcount

    def get_total_eaten(self, log_date):
        row = self.conn.execute(
            "SELECT COALESCE(SUM(calories), 0) FROM meals WHERE log_date = ?",
            (log_date.isoformat(),)).fetchone()
        return round(row[0], 1)

    def get_meal_type_totals(self, log_date):
        """[(meal type, calories)] for all four meal types (0 when empty)."""
        rows = dict(self.conn.execute(
            "SELECT meal_type, SUM(calories) FROM meals WHERE log_date = ? GROUP BY meal_type",
            (log_date.isoformat(),)).fetchall())
        return [(m, round(rows.get(m, 0), 1)) for m in MEAL_TYPES]

    # ----------------------------------------------------------- workouts
    def add_workout(self, log_date, activity_id, minutes, burned):
        cur = self.conn.execute(
            "INSERT INTO workouts (log_date, activity_id, minutes, calories_burned) "
            "VALUES (?, ?, ?, ?)",
            (log_date.isoformat(), activity_id, minutes, burned))
        self.conn.commit()
        return cur.lastrowid

    def get_workouts(self, log_date):
        return self.conn.execute("""
            SELECT w.workout_id, a.activity_name, w.minutes, w.calories_burned
            FROM workouts w JOIN activities a ON a.activity_id = w.activity_id
            WHERE w.log_date = ? ORDER BY w.workout_id
        """, (log_date.isoformat(),)).fetchall()

    def delete_workout(self, workout_id):
        cur = self.conn.execute("DELETE FROM workouts WHERE workout_id = ?", (workout_id,))
        self.conn.commit()
        return cur.rowcount

    def get_total_burned(self, log_date):
        row = self.conn.execute(
            "SELECT COALESCE(SUM(calories_burned), 0) FROM workouts WHERE log_date = ?",
            (log_date.isoformat(),)).fetchone()
        return round(row[0], 1)

    # ------------------------------------------------------------ weights
    def set_weight(self, log_date, weight_kg):
        """One weight per day: a second entry for the same day replaces the first."""
        self.conn.execute("""
            INSERT INTO weights (log_date, weight_kg) VALUES (?, ?)
            ON CONFLICT(log_date) DO UPDATE SET weight_kg = excluded.weight_kg
        """, (log_date.isoformat(), weight_kg))
        self.conn.commit()

    def get_weights(self):
        return self.conn.execute(
            "SELECT log_date, weight_kg FROM weights ORDER BY log_date").fetchall()

    def get_latest_weight(self):
        row = self.conn.execute(
            "SELECT weight_kg FROM weights ORDER BY log_date DESC LIMIT 1").fetchone()
        return row[0] if row else None

    def delete_weight(self, log_date):
        cur = self.conn.execute(
            "DELETE FROM weights WHERE log_date = ?", (log_date.isoformat(),))
        self.conn.commit()
        return cur.rowcount

    # --------------------------------------------------------- chart data
    def get_daily_totals(self, end_date, days=7):
        """[(date, eaten, burned)] for the last `days` days ending at end_date."""
        start = end_date - timedelta(days=days - 1)
        eaten = dict(self.conn.execute(
            "SELECT log_date, SUM(calories) FROM meals WHERE log_date BETWEEN ? AND ? "
            "GROUP BY log_date", (start.isoformat(), end_date.isoformat())).fetchall())
        burned = dict(self.conn.execute(
            "SELECT log_date, SUM(calories_burned) FROM workouts WHERE log_date BETWEEN ? AND ? "
            "GROUP BY log_date", (start.isoformat(), end_date.isoformat())).fetchall())
        result = []
        for i in range(days):
            day = start + timedelta(days=i)
            key = day.isoformat()
            result.append((day, round(eaten.get(key, 0), 1), round(burned.get(key, 0), 1)))
        return result
