#!/usr/bin/env python3

from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    print('Clearing existing data...')
    # Delete join rows first so foreign keys are never left dangling.
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    squat = Exercise(name='Back Squat', category='Strength', equipment_needed=True)
    pushup = Exercise(name='Push-Up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    running = Exercise(name='Treadmill Run', category='Cardio', equipment_needed=True)
    db.session.add_all([squat, pushup, plank, running])

    print('Creating workouts...')
    leg_day = Workout(
        date=date(2026, 10, 26), duration_minutes=60, notes='Focus on form and depth.'
    )
    full_body = Workout(
        date=date(2026, 10, 28), duration_minutes=45, notes='Light full-body session.'
    )
    cardio = Workout(date=date(2026, 10, 30), duration_minutes=30, notes=None)
    db.session.add_all([leg_day, full_body, cardio])

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, sets=5, reps=5),
        WorkoutExercise(workout=leg_day, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=full_body, exercise=pushup, sets=4, reps=15),
        WorkoutExercise(workout=full_body, exercise=squat, sets=3, reps=10),
        WorkoutExercise(workout=full_body, exercise=plank, sets=3, duration_seconds=45),
        WorkoutExercise(workout=cardio, exercise=running, duration_seconds=1500),
    ])

    db.session.commit()
    print('Done seeding.')
