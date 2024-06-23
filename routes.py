from flask import Blueprint, render_template, request
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from calculations import beam_design

main = Blueprint('main', __name__)


class BeamForm(FlaskForm):
    total_load = FloatField('Total Load (kN/m)', validators=[DataRequired()])
    span = FloatField('Span (m)', validators=[DataRequired()])
    grade_concrete = FloatField('Grade of Concrete (N/mm²)', validators=[DataRequired()])
    grade_steel = FloatField('Grade of Steel (N/mm²)', validators=[DataRequired()])
    max_depth = FloatField('Maximum Depth (mm)', validators=[DataRequired()])
    max_width = FloatField('Maximum Width (mm)', validators=[DataRequired()])
    submit = SubmitField('Calculate')


@main.route('/', methods=['GET', 'POST'])
def index():
    form = BeamForm()
    result = None
    if request.method == 'POST' and form.validate_on_submit():
        total_load = form.total_load.data
        span = form.span.data
        grade_concrete = form.grade_concrete.data
        grade_steel = form.grade_steel.data
        max_depth = form.max_depth.data
        max_width = form.max_width.data

        result = beam_design(total_load, span, grade_concrete, grade_steel, max_depth, max_width)

    return render_template('index.html', form=form, result=result)
