"""Helper functions for the Fitness and Diet Tracker.

This module contains the input validation rules and the fitness formulas.
It has no Tkinter and no SQL code, so every function can be tested alone.
"""

import math
from datetime import datetime

# A warning is shown when this percentage of the daily calorie target is used.
WARNING_PERCENT = 80
# The daily target is never set below this value (a safety limit).
MIN_CALORIE_TARGET = 1200

MEAL_TYPES = ["Breakfast", "Lunch", "Snack", "Dinner"]
GENDERS = ["Male", "Female"]

# Activity level -> multiplier applied to the BMR to get daily energy need.
ACTIVITY_LEVELS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly active (1-3 days a week)": 1.375,
    "Moderately active (3-5 days a week)": 1.55,
    "Very active (6-7 days a week)": 1.725,
}

# Goal -> calories added to (or taken from) the daily energy need.
GOALS = {
    "Lose weight": -500,
    "Maintain weight": 0,
    "Gain weight": 400,
}


# ---------------------------------------------------------------- validation
def validate_date(text, max_date=None):
    """Check a date typed as DD-MM-YYYY. Returns (True, date) or (False, message)."""
    text = (text or "").strip()
    if not text:
        return False, "Date cannot be empty."
    try:
        value = datetime.strptime(text, "%d-%m-%Y").date()
    except ValueError:
        return False, "Enter a real date in the form DD-MM-YYYY, for example 25-10-2026."
    if not 2000 <= value.year <= 2100:
        return False, "The year must be between 2000 and 2100."
    if max_date is not None and value > max_date:
        return False, "The date cannot be in the future."
    return True, value


def validate_number(text, label, minimum, maximum, whole=False, example="10"):
    """Check a number typed in a box.

    The value must lie between minimum and maximum (both included).
    'nan' and 'inf' are rejected. Returns (True, number) or (False, message).
    """
    text = (text or "").strip()
    if not text:
        return False, f"{label} cannot be empty."
    try:
        value = float(text)
    except ValueError:
        return False, f"{label} must be a number, for example {example}."
    if math.isnan(value) or math.isinf(value):
        return False, f"{label} must be a real number."
    if whole:
        if value != int(value):
            return False, f"{label} must be a whole number."
        value = int(value)
    else:
        value = round(value, 2)
    if value < minimum:
        return False, f"{label} must be at least {minimum:g}."
    if value > maximum:
        return False, f"{label} must not be more than {maximum:g}."
    return True, value


def validate_age(text):
    return validate_number(text, "Age", 10, 100, whole=True, example="19")


def validate_height(text):
    return validate_number(text, "Height (cm)", 100, 250, example="162")


def validate_weight(text):
    return validate_number(text, "Weight (kg)", 20, 300, example="58.5")


def validate_servings(text):
    ok, value = validate_number(text, "Servings", 0, 20, example="1.5")
    if ok and value <= 0:
        return False, "Servings must be greater than zero."
    return ok, value


def validate_minutes(text):
    return validate_number(text, "Minutes", 1, 600, whole=True, example="30")


def validate_name(text):
    text = (text or "").strip()
    if not text:
        return False, "Name cannot be empty."
    if len(text) > 40:
        return False, "Name must be at most 40 characters."
    return True, text


def validate_choice(value, options, label):
    """The chosen value must be one of the allowed options."""
    if value not in options:
        return False, f"Please select a {label}."
    return True, value


# ------------------------------------------------------------- calculations
def bmi(weight_kg, height_cm):
    """Body Mass Index = weight (kg) / height (m) squared, to one decimal."""
    metres = height_cm / 100.0
    return round(weight_kg / (metres * metres), 1)


def bmi_category(value):
    """Standard adult BMI classes."""
    if value < 18.5:
        return "Underweight"
    if value < 25:
        return "Normal"
    if value < 30:
        return "Overweight"
    return "Obese"


def bmr(gender, weight_kg, height_cm, age):
    """Basal metabolic rate (kcal/day) by the Mifflin-St Jeor equation."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return round(base + (5 if gender == "Male" else -161), 1)


def daily_target(bmr_value, activity_factor, goal_adjustment):
    """Daily calorie target = BMR x activity factor + goal adjustment.

    The result is rounded and never goes below MIN_CALORIE_TARGET.
    """
    target = round(bmr_value * activity_factor + goal_adjustment)
    return max(MIN_CALORIE_TARGET, target)


def calories_burned(met, weight_kg, minutes):
    """Calories burned = MET x weight (kg) x time (hours)."""
    return round(met * weight_kg * minutes / 60.0, 1)


def day_status(target, net_calories):
    """Decide the status of a day.

    'none'    - no profile / target yet
    'ok'      - less than 80% of the target is used
    'warning' - 80% or more is used, but not above the target
    'over'    - net calories are above the target
    """
    if target is None:
        return "none"
    if net_calories > target:
        return "over"
    if target > 0 and net_calories >= target * WARNING_PERCENT / 100:
        return "warning"
    return "ok"


def percent_used(target, net_calories):
    """Percentage of the daily target used (never below 0)."""
    if not target:
        return 0.0
    return round(max(net_calories, 0) / target * 100, 1)


def kcal(value):
    """Format a calorie value, for example 1,865 kcal."""
    return f"{value:,.0f} kcal"
