import random
import string
from datetime import datetime

from . import db


class URLMap(db.Model):
    """Модель для хранения ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, unique=True, nullable=False)
    short = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        """Метод для сериализации полей модели."""
        return dict(
            id=self.id,
            original=self.original,
            short=self.short,
            timestamp=self.timestamp
        )

    def from_dict(self, data):
        """Метод для десериализации полей модели."""
        for field in ('original', 'short'):
            if field in data:
                setattr(self, field, data[field])


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор переменной длины."""
    characters = string.ascii_letters + string.digits
    length = 6
    return ''.join(random.choice(characters) for _ in range(length))