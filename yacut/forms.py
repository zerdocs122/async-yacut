from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (URL, DataRequired, Length, Optional, Regexp,
                                ValidationError)

from .models import ID_EXISTS_MESSAGE, SHORT_MAX_LENGTH, SHORT_PATTERN

ORIGINAL_LINK_LABEL = 'Длинная ссылка'
CUSTOM_ID_LABEL = 'Ваш вариант короткой ссылки'
FILE_LABEL = 'Файл не выбран'

CREATE_BUTTON = 'Создать'
UPLOAD_BUTTON = 'Загрузить'

REQUIRED_FIELD_MESSAGE = 'Обязательное поле'
INVALID_URL_MESSAGE = 'Введите корректный URL'
FILE_REQUIRED_MESSAGE = 'Выберите файл для загрузки'

RESERVED_WORDS = {'files'}
MESSAGE_WORDS = 'Только буквы и цифры'


def validate_custom_id(form, field):
    """Валидатор для проверки зарезервированных слов."""
    if field.data and field.data in RESERVED_WORDS:
        raise ValidationError(ID_EXISTS_MESSAGE)


class MainForm(FlaskForm):
    """Форма главной страницы."""

    original_link = TextAreaField(
        ORIGINAL_LINK_LABEL,
        validators=[DataRequired(message=REQUIRED_FIELD_MESSAGE),
                    URL(message=INVALID_URL_MESSAGE),
                    Length(max=2048)])

    custom_id = StringField(
        CUSTOM_ID_LABEL,
        validators=[Length(max=SHORT_MAX_LENGTH), Optional(),
                    Regexp(SHORT_PATTERN,
                           message=MESSAGE_WORDS),
                    validate_custom_id])

    submit = SubmitField(CREATE_BUTTON)


class FileForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(FILE_LABEL,
                              validators=[FileRequired(
                                  message=FILE_REQUIRED_MESSAGE)])
    submit = SubmitField(UPLOAD_BUTTON)
