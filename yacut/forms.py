from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (URL, DataRequired, Length, Optional, Regexp,
                                ValidationError)

from .constants import (MAX_ORIGINAL_LENGTH, SHORT_EXISTS, SHORT_INVALID_URL,
                        SHORT_MAX_LENGTH, SHORT_PATTERN, SHORT_RESERVED)
from .models import URLMap

# Form label messages
ORIGINAL_LINK_LABEL = 'Длинная ссылка'
SHORT_LABEL = 'Ваш вариант короткой ссылки'
FILE_LABEL = 'Файл не выбран'
CREATE_BUTTON = 'Создать'
UPLOAD_BUTTON = 'Загрузить'

# Validation messages
REQUIRED_FIELD = 'Обязательное поле'
SHORT_VALID_CHARS = 'Только буквы и цифры'
FILE_REQUIRED = 'Выберите файл для загрузки'


class MainForm(FlaskForm):
    """Форма главной страницы."""
    original_link = TextAreaField(
        ORIGINAL_LINK_LABEL,
        validators=[DataRequired(message=REQUIRED_FIELD),
                    URL(message=SHORT_INVALID_URL),
                    Length(max=MAX_ORIGINAL_LENGTH)])
    custom_id = StringField(
        SHORT_LABEL,
        validators=[Length(max=SHORT_MAX_LENGTH), Optional(),
                    Regexp(SHORT_PATTERN,
                           message=SHORT_VALID_CHARS)])

    submit = SubmitField(CREATE_BUTTON)

    def validate_custom_id(self, field):
        """Валидатор для проверки зарезервированных слов и уникальности."""
        if (field.data and (field.data in SHORT_RESERVED or
                            URLMap.get_url_map(field.data))):
            raise ValidationError(SHORT_EXISTS)


class FileForm(FlaskForm):
    """Форма для загрузки файлов."""
    files = MultipleFileField(FILE_LABEL,
                              validators=[FileRequired(
                                  message=FILE_REQUIRED)])
    submit = SubmitField(UPLOAD_BUTTON)
