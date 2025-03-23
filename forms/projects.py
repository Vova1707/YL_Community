from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired

class Project_create_form(FlaskForm):
    title = StringField("Название:", validators=[DataRequired()])
    description = TextAreaField("Описание:")
    description_doptext = "Будет размещено в README.MD"
    file = FileField('Архив вашего проекта', validators=[DataRequired()])
    file_doptext = "Необязательно прикреплять сейчас, можно после создания проект"
    file_extension = ["zip"]
    file_extension_str = "Возможные расширения: " + ", ".join(file_extension)
    submit = SubmitField("Создать")


class Project_create_form(FlaskForm):
    title = StringField("Название:", validators=[DataRequired()])
    description = TextAreaField("Описание:")
    description_doptext = "Будет размещено в README.MD"
    file = FileField('Архив вашего проекта', validators=[DataRequired()])
    file_doptext = "Необязательно прикреплять сейчас, можно после создания проект"
    file_extension = ["zip"]
    file_extension_str = "Возможные расширения: " + ", ".join(file_extension)
    submit = SubmitField("Создать")