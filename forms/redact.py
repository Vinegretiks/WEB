from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import StringField, EmailField
from wtforms.validators import DataRequired


class Admin_redact(FlaskForm):
    email = EmailField('', validators=[DataRequired()])
    name = StringField('', validators=[DataRequired()])
    balance = StringField('', validators=[DataRequired()])
    submit = SubmitField('Сохранить изменения')