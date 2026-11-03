from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    exercise_detail_schema,
    exercise_schema,
    exercises_schema,
    workout_detail_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


def error(message, status):
    return jsonify({'error': message}), status


@app.errorhandler(ValidationError)
def handle_schema_error(err):
    return jsonify({'errors': err.messages}), 400


@app.errorhandler(ValueError)
def handle_model_error(err):
    # Raised by the @validates methods on the models.
    return error(str(err), 400)


@app.route('/workouts', methods=['GET'])
def list_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    # Cascade on the relationship removes the associated WorkoutExercises.
    db.session.delete(workout)
    db.session.commit()
    return '', 204


@app.route('/exercises', methods=['GET'])
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = exercise_schema.load(request.get_json(silent=True) or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error('An exercise with that name already exists.', 409)
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    # Cascade on the relationship removes the associated WorkoutExercises.
    db.session.delete(exercise)
    db.session.commit()
    return '', 204


@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST'],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error('Workout not found.', 404)
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error('Exercise not found.', 404)

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
