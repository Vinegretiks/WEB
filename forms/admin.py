from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


class Admin(FlaskForm):
    number = StringField('', validators=[DataRequired()])
    submit_redact = SubmitField('Редактировать пользователя')