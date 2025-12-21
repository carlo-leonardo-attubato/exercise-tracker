#!/usr/bin/env python3
"""Export workout analysis to data.js for visualization."""
import json
from datetime import datetime, timedelta
from pathlib import Path

from analyze import (
    ROOT,
    load_json,
    load_workouts,
    load_standards,
    load_muscle_map,
    invert_muscle_map,
    get_score,
)
from formulas import mayhew

# All muscles from react-body-highlighter (minus head), ordered head to feet
ALL_MUSCLES = [
    "neck",
    "trapezius",
    "front-deltoids",
    "back-deltoids",
    "chest",
    "upper-back",
    "biceps",
    "triceps",
    "forearm",
    "abs",
    "obliques",
    "lower-back",
    "gluteal",
    "adductor",
    "abductors",
    "quadriceps",
    "hamstring",
    "calves",
]


def get_rolling_scores(workouts, standards, muscle_map, window_days=7):
    """Calculate rolling max scores for each muscle on each workout date.

    Returns:
        dates: list of date strings
        scores: dict of muscle -> list of scores (with backfill)
        trained: dict of muscle -> list of bools (True if trained that day)
    """
    inverted = invert_muscle_map(muscle_map)
    dates = sorted(set(w["date"] for w in workouts))

    # Build a map of date -> exercises done that day
    exercises_by_date = {}
    for session in workouts:
        d = session["date"]
        exercises_by_date[d] = set(ex["name"] for ex in session["exercises"] if "sets" in ex)

    result = {muscle: [] for muscle in ALL_MUSCLES}
    trained = {muscle: [] for muscle in ALL_MUSCLES}

    for target_date in dates:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        cutoff = target_dt - timedelta(days=window_days)

        # Which muscles were trained on this specific date?
        exercises_today = exercises_by_date.get(target_date, set())
        muscles_today = set()
        for ex_name in exercises_today:
            if ex_name in muscle_map:
                muscles_today.update(muscle_map[ex_name].keys())

        for muscle in ALL_MUSCLES:
            exercises = inverted.get(muscle, {})
            total_score = 0
            total_weight = 0

            for exercise, contribution in exercises.items():
                if exercise not in standards:
                    continue

                best_e1rm = 0
                for session in workouts:
                    session_dt = datetime.strptime(session["date"], "%Y-%m-%d")
                    if session_dt < cutoff or session_dt > target_dt:
                        continue

                    for ex in session["exercises"]:
                        if ex["name"] != exercise:
                            continue
                        for s in ex.get("sets", []):
                            reps, weight = s[0], s[1]
                            e1rm = mayhew(weight, reps)
                            if e1rm > best_e1rm:
                                best_e1rm = e1rm

                if best_e1rm > 0:
                    score = get_score(best_e1rm, standards[exercise])
                    total_score += contribution * score
                    total_weight += contribution

            if total_weight > 0:
                result[muscle].append(round(total_score / total_weight))
            else:
                result[muscle].append(None)

            # Mark trained only if an exercise targeting this muscle was done TODAY
            trained[muscle].append(muscle in muscles_today)

    return dates, result, trained


def get_user_dir():
    """Find user folder in user_data/. Prompts if multiple exist."""
    user_data = ROOT / "user_data"
    users = [d.name for d in user_data.iterdir() if d.is_dir() and d.name.startswith(".")]

    if not users:
        print("No user folders found in user_data/")
        print("Create one like: user_data/.your_name/")
        exit(1)

    if len(users) == 1:
        return f"user_data/{users[0]}"

    print("Multiple users found:")
    for i, u in enumerate(users):
        print(f"  {i + 1}. {u[1:]}")  # Remove leading dot for display
    choice = input("Select user (number): ")
    return f"user_data/{users[int(choice) - 1]}"


def main():
    user_dir = get_user_dir()

    config = load_json(f"{user_dir}/config.json")
    sex = config["user"]["sex"]
    weight_kg = config["user"]["weight_kg"]

    workouts = load_workouts(f"{user_dir}/workouts.jsonl")
    standards = load_standards("data/standards.csv", sex, weight_kg)
    muscle_map = load_muscle_map("data/muscle_map.json")

    dates, scores, trained = get_rolling_scores(workouts, standards, muscle_map)

    # Format dates as MM-DD
    dates_short = [d[5:] for d in dates]

    data = {
        "dates": dates_short,
        "muscles": ALL_MUSCLES,
        "scores": scores,
        "trained": trained,
        "user": {"sex": sex, "weight_kg": weight_kg},
    }

    output = f"const DATA = {json.dumps(data, indent=2)};\n"

    out_path = ROOT / "user_data" / "data.js"
    out_path.write_text(output)
    print(f"Exported to {out_path}")


if __name__ == "__main__":
    main()
