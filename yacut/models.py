import random
import string
from datetime import datetime

from . import db

SHORT_LENGTH = 6
SHORT_MAX_LENGTH = 16
SHORT_PATTERN = r'^[a-zA-Z0-9]+$'
ID_EXISTS_MESSAGE = 'Предложенный вариант короткой ссылки уже существует.'
CHARACTERS = string.ascii_letters + string.digits
MAX_ORIGINAL_LENGTH = 2048


class URLMap(db.Model):
    """Модель для хранения ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_by_short(short):
        """Получить запись по короткому идентификатору."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def create(original, short=None):
        """Создать новую запись в базе данных."""
        if short is None:
            while True:
                chars = CHARACTERS
                short = ''.join(random.choice(chars)
                                for _ in range(SHORT_LENGTH))
                if not URLMap.query.filter_by(short=short).first():
                    break
        else:
            if URLMap.query.filter_by(short=short).first():
                raise ValueError(ID_EXISTS_MESSAGE)
        new_url = URLMap(original=original, short=short)
        db.session.add(new_url)
        db.session.commit()
        return new_url

    def get_short_url(self):
        """Получить полную короткую ссылку."""
        from flask import url_for
        return url_for('redirect_to_original',
                       short=self.short,
                       _external=True)

    @staticmethod
    def generate_short():
        """Генерирует уникальный короткий идентификатор."""
        while True:
            short = ''.join(random.choice(CHARACTERS)
                            for _ in range(SHORT_LENGTH))
            if not URLMap.get_by_short(short):
                return short

    @staticmethod
    def create_file_entry(file_path, short):
        """Создает запись о файле в базе данных."""
        new_url = URLMap(
            original=f'file: {file_path}',
            short=short
        )
        db.session.add(new_url)
        db.session.commit()
        return new_url