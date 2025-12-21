# Exercise Tracker

Track your gym progress with muscle-by-muscle strength scoring based on [strengthlevel.com](https://strengthlevel.com) standards.

## Usage

Open `index.html` in your browser. All data is stored locally in your browser's localStorage.

### Getting Started

1. Click the gear icon to open Settings
2. Set your sex and weight in Profile
3. Start adding workouts in the Logbook tab

### Features

- **Logbook**: Add, edit, and delete workouts
- **Dashboard**: View muscle scores on body diagram, heatmap, and chart
- **Import/Export**: Backup your data or import from file via Settings

## How it works

- **e1RM**: Estimated one-rep max (configurable formula in Advanced settings)
- **Score**: 0-500 scale based on strength standards (100=beginner, 200=novice, 300=intermediate, 400=advanced, 500=elite)
- **Muscle score**: Weighted average of contributing exercises (isolation=1.0, compound secondary=0.3)
- **Rolling window**: 7-day max for each exercise

## Supported exercises

See `data/muscle_map.json` for the list of exercises and their muscle contributions.

## Adding exercises

1. Add standards to `data/standards.json`
2. Add muscle mappings to `data/muscle_map.json`
