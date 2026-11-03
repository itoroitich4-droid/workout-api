# Workout Tracker API

## Description

A Flask REST API for a workout tracking application used by personal trainers. It tracks **workouts** and the **exercises** performed in them. Exercises are reusable across workouts, and each exercise added to a workout records its own reps, sets and/or duration through the `WorkoutExercise` join table.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate (SQLite) and Marshmallow.

### Data model

- **Exercise**: `id`, `name` (unique), `category`, `equipment_needed`
- **Workout**: `id`, `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table): `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

A Workout has many Exercises through WorkoutExercises, and an Exercise has many Workouts through WorkoutExercises. Deleting a workout or exercise also deletes its WorkoutExercises.

### Validations

| Level | Rules |
| --- | --- |
| Table constraints | unique exercise name; non-blank name/category; `duration_minutes > 0`; `reps`, `sets`, `duration_seconds` > 0 when set; at least one of reps/sets/duration_seconds present |
| Model validations (`@validates`) | non-blank `name`/`category`; boolean `equipment_needed`; valid `date`; positive integer `duration_minutes`, `reps`, `sets`, `duration_seconds` |
| Schema validations (Marshmallow) | required fields and lengths; non-blank `name`/`category`; `duration_minutes`, `reps`, `sets`, `duration_seconds` >= 1 (strict integers); schema-level check that a WorkoutExercise has at least one of reps/sets/duration_seconds |

## Installation

Requires Python 3.8+ and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone <your-repo-url>
cd workout-app
pipenv install
pipenv shell
cd server

# create the database
export FLASK_APP=app.py
flask db init
flask db migrate -m "Create exercises, workouts and workout_exercises tables"
flask db upgrade head

# load example data (safe to re-run; it clears existing data first)
python seed.py
```

## Running the app

From the `server/` directory:

```bash
flask run -p 5555
# or
python app.py
```

The API is served at `http://127.0.0.1:5555`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/workouts` | List all workouts. |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration_seconds from the join table. 404 if not found. |
| POST | `/workouts` | Create a workout. Body: `date` (YYYY-MM-DD), `duration_minutes`, optional `notes`. |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises. Returns 204. |
| GET | `/exercises` | List all exercises. |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in. 404 if not found. |
| POST | `/exercises` | Create an exercise. Body: `name`, `category`, `equipment_needed`. Returns 409 if the name already exists. |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises. Returns 204. |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout. Body: any of `reps`, `sets`, `duration_seconds` (at least one required). |

Invalid input returns `400` with an `errors` (schema) or `error` (model) message.

### Example requests

```bash
curl -X POST localhost:5555/exercises -H 'Content-Type: application/json' \
  -d '{"name": "Deadlift", "category": "Strength", "equipment_needed": true}'

curl -X POST localhost:5555/workouts -H 'Content-Type: application/json' \
  -d '{"date": "2026-11-04", "duration_minutes": 50, "notes": "Pull day"}'

curl -X POST localhost:5555/workouts/1/exercises/1/workout_exercises \
  -H 'Content-Type: application/json' -d '{"sets": 3, "reps": 8}'
```
