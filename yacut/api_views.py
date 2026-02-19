from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap

EMPTY_REQUEST = 'Отсутствует тело запроса'
MISSING_URL = '"url" является обязательным полем!'
ID_NOT_FOUND = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API эндпоинт для создания короткой ссылки."""
    data = request.get_json(force=True, silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST)
    if 'url' not in data:
        raise InvalidAPIUsage(MISSING_URL)
    try:
        url_map = URLMap.create(data['url'], data.get('custom_id'))
    except ValueError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify({
        'url': data['url'],
        'short_link': url_map.get_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<short>/', methods=['GET'])
def get_original_url(short):
    """API эндпоинт для получения оригинальной ссылки."""
    if not (url_map := URLMap.get(short)):
        raise InvalidAPIUsage(ID_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original})
