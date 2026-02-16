import re
from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import ID_EXISTS_MESSAGE, SHORT_MAX_LENGTH, SHORT_PATTERN, URLMap

# Сообщения об ошибках API
EMPTY_REQUEST_MESSAGE = 'Отсутствует тело запроса'
MISSING_URL_MESSAGE = '"url" является обязательным полем!'
INVALID_URL_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
ID_NOT_FOUND_MESSAGE = 'Указанный id не найден'
RESERVED_ID = 'files'


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API эндпоинт для создания короткой ссылки."""
    data = request.get_json(force=True, silent=True)

    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST_MESSAGE)

    if 'url' not in data:
        raise InvalidAPIUsage(MISSING_URL_MESSAGE)

    url = data['url']
    short = data.get('custom_id')

    if short:
        if short == RESERVED_ID:
            raise InvalidAPIUsage(ID_EXISTS_MESSAGE)

        if len(short) > SHORT_MAX_LENGTH or not re.match(SHORT_PATTERN, short):
            raise InvalidAPIUsage(INVALID_URL_MESSAGE)

        if URLMap.get_by_short(short):
            raise InvalidAPIUsage(ID_EXISTS_MESSAGE)

    try:
        new_url = URLMap.create(url, short)
    except ValueError as e:
        raise InvalidAPIUsage(str(e))

    return jsonify({
        'url': url,
        'short_link': new_url.get_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<short>/', methods=['GET'])
def get_original_url(short):
    """API эндпоинт для получения оригинальной ссылки."""
    url_map = URLMap.get_by_short(short)

    if not url_map:
        raise InvalidAPIUsage(ID_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_map.original})