from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=100))
    category = fields.Str(required=True, validate=validate.Length(max=50))
    equipment_needed = fields.Bool(required=True)

    @validates('name')
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError('name cannot be blank.')

    @validates('category')
    def validate_category(self, value):
        if not value.strip():
            raise ValidationError('category cannot be blank.')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    notes = fields.Str(load_default=None, allow_none=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1))
    sets = fields.Int(strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1))
    duration_seconds = fields.Int(
        strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1)
    )

    # Related records are included in responses only.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)

    @validates_schema
    def require_a_measure(self, data, **kwargs):
        """A workout exercise must record reps, sets or a duration."""
        if all(data.get(k) is None for k in ('reps', 'sets', 'duration_seconds')):
            raise ValidationError(
                'Provide at least one of reps, sets or duration_seconds.', '_schema'
            )


class WorkoutDetailSchema(WorkoutSchema):
    """A workout with its exercises and the reps/sets/duration for each."""

    workout_exercises = fields.Nested(
        WorkoutExerciseSchema(exclude=('workout',)), many=True, dump_only=True
    )


class ExerciseDetailSchema(ExerciseSchema):
    """An exercise with the workouts it appears in."""

    workout_exercises = fields.Nested(
        WorkoutExerciseSchema(exclude=('exercise',)), many=True, dump_only=True
    )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()
