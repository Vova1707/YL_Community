from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField, IntegerField, EmailField
from wtforms.validators import DataRequired


class Profile_edit_form(FlaskForm):
    name = StringField("Название:", validators=[DataRequired()])
    surname = TextAreaField()
    age = IntegerField()
    email = EmailField()
    about = TextAreaField()
    image_profile = FileField('Архив вашего проекта', validators=[DataRequired()])
    submit = SubmitField("Сохранить")