from flask import jsonify, render_template

from . import app, db


class InvalidAPIUsage(Exception):
    """Класс для обработки ошибок API."""
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)


@app.errorhandler(404)
def page_not_found(error):
    """Обработчик ошибки 404 для пользовательского интерфейса."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Обработчик ошибки 500 для пользовательского интерфейса."""
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Обработчик ошибок API."""
    response = jsonify(error.to_dict())
    response.content_type = 'application/json'
    return response, error.status_code