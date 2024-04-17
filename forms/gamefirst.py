from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


class GameFirst(FlaskForm):  # создание кнопки и поял для ввода
    number = StringField('', validators=[DataRequired()])
    submit = SubmitField('Предположить')
