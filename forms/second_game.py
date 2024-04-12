from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired


class StartMenuSecondGame(FlaskForm):
    submit = SubmitField("Сделать ставку")
    Second_stavka = StringField('', validators=[DataRequired()])


class SecondGame(FlaskForm):
    Red = BooleanField("Красное")
    Black = BooleanField("Чёрное")
    Even = BooleanField("Четное")
    Odd = BooleanField("Нечетное")
    Fst_12 = BooleanField("Первые 12 чисел")
    Snd_12 = BooleanField("Вторые 12 чисел")
    Trd_12 = BooleanField("Третие 12 чисел")
    F2to1 = BooleanField("Первый столбец 2to1, начало с 1")
    S2to1 = BooleanField("Второй столбец 2to1, начало с 2")
    T2to1 = BooleanField("Третий столбец 2to1, начало с 5")
    First_to_18 = BooleanField("1to18")
    TN_to_36 = BooleanField("19to36")
    Zero = BooleanField("Нуль")
    submit = SubmitField("Прыжок в неизвестность")
