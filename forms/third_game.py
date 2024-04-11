from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired


class StartThirdGame(FlaskForm):
    Third_game_sum = StringField('', validators=[DataRequired()])
    submit = SubmitField("Начать")

class ThirdGame(FlaskForm):
    submit = SubmitField("Крутить")