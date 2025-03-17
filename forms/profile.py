from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, IntegerField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class Profile_edit_form(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    about = TextAreaField("Расскажите о себе:")
    age = IntegerField("Возраст", validators=[NumberRange(min=0)])
    email = EmailField('Ваш email:', validators=[DataRequired(), Email()])
    image_profile = FileField('Фото профиля')
    submit = SubmitField('Сохранить')
