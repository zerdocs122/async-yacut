import random
import re
from datetime import datetime

from flask import url_for

from . import db
from .constants import (CHARACTERS, MAX_ATTEMPTS, MAX_ORIGINAL_LENGTH,
                        SHORT_EXISTS, SHORT_INVALID_URL, SHORT_LENGTH,
                        SHORT_MAX_LENGTH, SHORT_PATTERN,
                        SHORT_REDIRECT_ENDPOINT, SHORT_RESERVED)

# Error and status messages
FAILED = (
    'Не удалось сгенерировать уникальный короткий '
    'идентификатор (попыток: {})'
)
URL_TOO_LONG = 'URL слишком длинный'


class URLMap(db.Model):
    """Модель для хранения ссылок."""
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_url_map(short):
        """Получить запись по короткому идентификатору."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def create(original, short=None, skip_short_validation=False,
               skip_url_validation=False, commit=True):
        """Создать новую запись в базе данных."""
        if short:
            if not skip_short_validation:
                if (len(short) > SHORT_MAX_LENGTH or
                        not re.match(SHORT_PATTERN, short)):
                    raise ValueError(SHORT_INVALID_URL)
            if short in SHORT_RESERVED or URLMap.get_url_map(short):
                raise ValueError(SHORT_EXISTS)
        else:
            if not skip_url_validation:
                if len(original) > MAX_ORIGINAL_LENGTH:
                    raise ValueError(URL_TOO_LONG)
            short = URLMap.generate_short()
        new_url = URLMap(original=original, short=short)
        db.session.add(new_url)
        if commit:
            db.session.commit()
        return new_url

    def get_short_url(self):
        """Получить полную короткую ссылку."""
        return url_for(SHORT_REDIRECT_ENDPOINT,
                       short=self.short,
                       _external=True)

    @staticmethod
    def generate_short():
        """Генерирует уникальный короткий идентификатор."""
        for _ in range(MAX_ATTEMPTS):
            short = ''.join(random.choices(CHARACTERS, k=SHORT_LENGTH))
            if short not in SHORT_RESERVED and not URLMap.get_url_map(short):
                return short
        raise RuntimeError(FAILED.format(MAX_ATTEMPTS))
