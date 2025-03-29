from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, TextAreaField, StringField, MultipleFileField
from wtforms.validators import DataRequired, Optional

class BlogForms(FlaskForm):
    title = StringField("Название:", validators=[DataRequired()])
    description = TextAreaField()
    images = MultipleFileField('Загрузить изображения', render_kw={'multiple': True}, default=None)
    submit = SubmitField('Загрузить')

class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')