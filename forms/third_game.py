from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired


class StartThirdGame(FlaskForm):  # создание кнопки и поля для ввода данных
    Third_game_sum = StringField('', validators=[DataRequired()])
    submit = SubmitField("Начать")


class ThirdGame(FlaskForm):  # создание кнопки
    submit = SubmitField("Крутить")
