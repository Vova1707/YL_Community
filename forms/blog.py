from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class BlogForms(FlaskForm):
    description = TextAreaField()
    images = FileField(
        'Загрузите изображения',
        render_kw={"multiple": True},
        validators=[
            FileRequired(),
            # FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')
        ],
    )
    # images = MultipleFileField(
    #     'Загрузить изображения', render_kw={'multiple': True}, default=None
    # )
    submit = SubmitField('Загрузить')


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')
