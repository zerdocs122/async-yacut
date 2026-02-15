from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import URL, DataRequired, Length, Optional


class MainForm(FlaskForm):
    """Форма главной страницы."""

    original_link = TextAreaField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(message='Введите корректный URL')])

    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(1, 16), Optional()], )

    submit = SubmitField('Создать')


class FileForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField('Файл не выбран',
                              validators=[FileRequired(
                                  message='Выберите файл для загрузки')])
    submit = SubmitField('Загрузить')
