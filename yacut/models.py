import random
import re
from datetime import datetime

from flask import url_for

from . import db
from .constants import (CHARACTERS, ENDPOINT, FAILED_MESSAGE, FILE_PREFIX,
                        ID_EXISTS_MESSAGE, INVALID_URL_MESSAGE, MAX_ATTEMPTS,
                        MAX_ORIGINAL_LENGTH, RESERVED_WORDS, SHORT_LENGTH,
                        SHORT_MAX_LENGTH, SHORT_PATTERN, URL_TOO_LONG_MESSAGE)


class URLMap(db.Model):
    """Модель для хранения ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_short(short):
        """Получить запись по короткому идентификатору."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def create(original, short=None):
        """Создать новую запись в базе данных."""
        if short:
            if short in RESERVED_WORDS:
                raise ValueError(ID_EXISTS_MESSAGE)

            if len(short) > SHORT_MAX_LENGTH or not re.match(SHORT_PATTERN,
                                                             short):
                raise ValueError(INVALID_URL_MESSAGE)

            if URLMap.get_short(short):
                raise ValueError(ID_EXISTS_MESSAGE)
        else:
            if len(original) > MAX_ORIGINAL_LENGTH:
                raise ValueError(URL_TOO_LONG_MESSAGE)
            short = URLMap.generate_short()

        new_url = URLMap(original=original, short=short)
        db.session.add(new_url)
        db.session.commit()
        return new_url

    @staticmethod
    def create_file_entry(file_path):
        """Создать запись для файла на Яндекс Диске."""
        short = URLMap.generate_short()
        original = f'{FILE_PREFIX}{file_path}'
        new_url = URLMap(original=original, short=short)
        db.session.add(new_url)
        db.session.commit()
        return new_url

    def get_short_url(self):
        """Получить полную короткую ссылку."""
        return url_for(ENDPOINT,
                       short=self.short,
                       _external=True)

    @staticmethod
    def generate_short():
        """Генерирует уникальный короткий идентификатор."""
        for _ in range(MAX_ATTEMPTS):
            short = ''.join(random.choices(CHARACTERS, k=SHORT_LENGTH))
            if short not in RESERVED_WORDS and not URLMap.get_short(short):
                return short
        raise RuntimeError(FAILED_MESSAGE)
