from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (URL, DataRequired, Length, Optional, Regexp,
                                ValidationError)

from .constants import (CREATE_BUTTON, FILE_LABEL, FILE_REQUIRED_MESSAGE,
                        ID_EXISTS_MESSAGE, INVALID_URL_MESSAGE, MESSAGE_WORDS,
                        ORIGINAL_LINK_LABEL, REQUIRED_FIELD_MESSAGE,
                        RESERVED_WORDS, SHORT_LABEL, SHORT_MAX_LENGTH,
                        SHORT_PATTERN, UPLOAD_BUTTON)
from .models import URLMap


class MainForm(FlaskForm):
    """Форма главной страницы."""

    original_link = TextAreaField(
        ORIGINAL_LINK_LABEL,
        validators=[DataRequired(message=REQUIRED_FIELD_MESSAGE),
                    URL(message=INVALID_URL_MESSAGE),
                    Length(max=2048)])

    custom_id = StringField(
        SHORT_LABEL,
        validators=[Length(max=SHORT_MAX_LENGTH), Optional(),
                    Regexp(SHORT_PATTERN,
                           message=MESSAGE_WORDS)])

    submit = SubmitField(CREATE_BUTTON)

    def validate_custom_id(self, field):
        """Валидатор для проверки зарезервированных слов и уникальности."""
        if field.data and field.data in RESERVED_WORDS:
            raise ValidationError(ID_EXISTS_MESSAGE)

        if field.data and URLMap.get_short(field.data):
            raise ValidationError(ID_EXISTS_MESSAGE)


class FileForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(FILE_LABEL,
                              validators=[FileRequired(
                                  message=FILE_REQUIRED_MESSAGE)])
    submit = SubmitField(UPLOAD_BUTTON)
