#!/usr/bin/env python3
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

from formulas import mayhew

# Colors for terminal output
PURPLE = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


ROOT = Path(__file__).parent.parent


def load_json(filepath):
    with open(ROOT / filepath) as f:
        return json.load(f)


def load_csv(filepath):
    """Load CSV file and return list of dicts."""
    with open(ROOT / filepath) as f:
        return list(csv.DictReader(f))


def load_workouts(filepath):
    """Load workouts from JSONL (one session per line)."""
    workouts = []
    with open(ROOT / filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                workouts.append(json.loads(line))
    return workouts


def load_standards(filename, sex, weight_kg):
    """Load strength standards from CSV, filtered by sex and weight."""
    standards = {}
    for row in load_csv(filename):
        if row["sex"] == sex and int(row["weight_kg"]) == weight_kg:
            standards[row["exercise"]] = {
                "source": row["source"],
                "beginner": float(row["beginner"]),
                "novice": float(row["novice"]),
                "intermediate": float(row["intermediate"]),
                "advanced": float(row["advanced"]),
                "elite": float(row["elite"]),
            }
    return standards


def load_muscle_map(filename):
    """Load muscle map from JSON (exercise -> {muscle: weight})."""
    return load_json(filename)


def get_score(e1rm, standards):
    """Calculate score 0-500+ by interpolating between strength levels."""
    thresholds = [
        (0, 0),
        (standards["beginner"], 100),
        (standards["novice"], 200),
        (standards["intermediate"], 300),
        (standards["advanced"], 400),
        (standards["elite"], 500),
    ]

    for i in range(len(thresholds) - 1):
        lower_weight, lower_score = thresholds[i]
        upper_weight, upper_score = thresholds[i + 1]

        if e1rm <= upper_weight:
            weight_range = upper_weight - lower_weight
            score_range = upper_score - lower_score
            progress = (e1rm - lower_weight) / weight_range
            return lower_score + progress * score_range

    # Above elite - extrapolate
    elite_weight = standards["elite"]
    advanced_weight = standards["advanced"]
    weight_per_100 = elite_weight - advanced_weight
    extra = (e1rm - elite_weight) / weight_per_100 * 100
    return 500 + extra


def get_level(score):
    """Determine strength level from score."""
    if score >= 500:
        return "elite"
    elif score >= 400:
        return "advanced"
    elif score >= 300:
        return "intermediate"
    elif score >= 200:
        return "novice"
    else:
        return "beginner"


def get_exercise_e1rm(workouts, exercise_name, days=7):
    """Get max e1RM for an exercise over the last N days from JSONL."""
    cutoff = datetime.now() - timedelta(days=days)

    best_e1rm = 0
    best_set = None
    best_date = None

    for session in workouts:
        workout_date = datetime.strptime(session["date"], "%Y-%m-%d")
        if workout_date < cutoff:
            continue

        for exercise in session["exercises"]:
            if exercise["name"] != exercise_name:
                continue

            for s in exercise.get("sets", []):
                reps, weight = s[0], s[1]
                e1rm = mayhew(weight, reps)

                if e1rm > best_e1rm:
                    best_e1rm = e1rm
                    best_set = {"reps": reps, "weight": weight}
                    best_date = session["date"]

    return best_e1rm, best_set, best_date


def invert_muscle_map(muscle_map):
    """Convert exercise->{muscle:weight} to muscle->{exercise:weight}."""
    inverted = {}
    for exercise, muscles in muscle_map.items():
        for muscle, weight in muscles.items():
            if muscle not in inverted:
                inverted[muscle] = {}
            inverted[muscle][exercise] = weight
    return inverted


def analyze_workouts(workouts, standards, muscle_map, days=7):
    """Analyze workouts and return scores per muscle group.

    Algorithm (weighted average):
    1. For each muscle, get all exercises that work it
    2. For each exercise performed, calculate score
    3. Muscle score = weighted average of exercise scores
    """
    muscle_scores = {}
    inverted = invert_muscle_map(muscle_map)

    for muscle, exercises in inverted.items():
        total_score = 0
        total_weight = 0

        for exercise, contribution in exercises.items():
            if exercise not in standards:
                continue

            e1rm, best_set, date = get_exercise_e1rm(workouts, exercise, days)

            if e1rm == 0 or best_set is None:
                continue

            score = get_score(e1rm, standards[exercise])
            total_score += contribution * score
            total_weight += contribution

        if total_weight > 0:
            avg_score = total_score / total_weight
            muscle_scores[muscle] = {
                "score": avg_score,
                "level": get_level(avg_score),
            }

    return muscle_scores


def get_score_color(score):
    """Get color based on score."""
    if score >= 500:
        return PURPLE
    elif score >= 400:
        return BLUE
    elif score >= 300:
        return GREEN
    elif score >= 200:
        return YELLOW
    else:
        return RED


def print_report(scores, sex, weight_kg):
    """Print colored report to terminal."""
    print(f"\n{BOLD}Muscle Group Performance (Last 7 Days){RESET}")
    print("=" * 50)
    print(f"{'Muscle':<20} {'Score':>8} {'Level':<12}")
    print("-" * 50)

    for muscle, data in sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True):
        color = get_score_color(data["score"])
        score_str = f"{data['score']:.0f}"
        print(f"{color}{muscle:<20} {score_str:>8} {data['level']:<12}{RESET}")

    print()
    print(f"{PURPLE}* Elite 500{RESET}  {BLUE}* Advanced 400{RESET}  {GREEN}* Intermediate 300{RESET}  {YELLOW}* Novice 200{RESET}  {RED}* Beginner 100{RESET}")
    print()
    print(f"{DIM}Standards from strengthlevel.com for {weight_kg}kg {sex}")
    print(f"e1RM estimated using Mayhew formula")
    print(f"Muscle score = weighted average of contributing exercises{RESET}")


def print_summary(scores):
    """Print colored muscle group summary."""
    if not scores:
        return

    sorted_muscles = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

    print(f"\n{BOLD}Muscle Groups:{RESET}")
    muscle_strs = []
    for muscle, data in sorted_muscles:
        color = get_score_color(data["score"])
        muscle_strs.append(f"{color}{muscle}{RESET}")
    print(" | ".join(muscle_strs))


def main():
    config = load_json("user_data/config.json")
    sex = config["user"]["sex"]
    weight_kg = config["user"]["weight_kg"]

    workouts = load_workouts("user_data/workouts.jsonl")
    standards = load_standards("data/standards.csv", sex, weight_kg)
    muscle_map = load_muscle_map("data/muscle_map.json")

    scores = analyze_workouts(workouts, standards, muscle_map)
    print_report(scores, sex, weight_kg)
    print_summary(scores)


if __name__ == "__main__":
    main()
