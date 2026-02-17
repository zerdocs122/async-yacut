import os


class Config(object):
    """Конфигурация проекта."""

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my-secret-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    API_HOST = 'https://cloud-api.yandex.net/'
    API_VERSION = 'v1'
