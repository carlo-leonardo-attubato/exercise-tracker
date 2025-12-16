# Exercise Tracker

Track your gym progress with muscle-by-muscle strength scoring based on [strengthlevel.com](https://strengthlevel.com) standards.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `user_data/config.json`:
   ```json
   {"user": {"sex": "male", "weight_kg": 70}}
   ```

3. Create `user_data/workouts.jsonl` (one JSON per line):
   ```json
   {"date": "2025-01-01", "exercises": [{"name": "chest press", "sets": [[10, 50], [8, 55]]}]}
   ```

## Usage

1. Export your data:
   ```bash
   python3 src/export.py
   ```

2. Build the viewer:
   ```bash
   npx esbuild src/app.jsx --bundle --outfile=bundle.js
   ```

3. Open `view.html` in your browser.

## How it works

- **e1RM**: Estimated one-rep max using the Mayhew formula
- **Score**: 0-500 scale based on strength standards (100=beginner, 200=novice, 300=intermediate, 400=advanced, 500=elite)
- **Muscle score**: Weighted average of contributing exercises (isolation=1.0, compound secondary=0.3)
- **Rolling window**: 7-day max for each exercise

## Supported exercises

See `data/muscle_map.json` for the list of exercises and their muscle contributions.

## Adding exercises

1. Add standards to `data/standards.csv`
2. Add muscle mappings to `data/muscle_map.json`
