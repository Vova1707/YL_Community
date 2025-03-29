from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField, IntegerField, EmailField
from wtforms.validators import DataRequired


class Profile_edit_form(FlaskForm):
    name = StringField("Имя:", validators=[DataRequired()])
    surname = TextAreaField("Фамилия:")
    age = IntegerField("Сколько лет:")
    email = EmailField("Email:")
    about = TextAreaField("Немного о себе:")
    image_profile = FileField('Фото профиля')
    submit = SubmitField("Сохранить")