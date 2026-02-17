
from http import HTTPStatus

from flask import jsonify, request

from . import app
from .constants import (EMPTY_REQUEST_MESSAGE, ID_NOT_FOUND_MESSAGE,
                        MISSING_URL_MESSAGE)
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API эндпоинт для создания короткой ссылки."""
    data = request.get_json(force=True, silent=True)

    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST_MESSAGE)

    if 'url' not in data:
        raise InvalidAPIUsage(MISSING_URL_MESSAGE)

    try:
        return jsonify({
            'url': data['url'],
            'short_link': URLMap.create(
                data['url'],
                data.get('custom_id')
            ).get_short_url()
        }), HTTPStatus.CREATED
    except ValueError as e:
        raise InvalidAPIUsage(str(e))


@app.route('/api/id/<short>/', methods=['GET'])
def get_original_url(short):
    """API эндпоинт для получения оригинальной ссылки."""
    if not (url_map := URLMap.get_short(short)):
        raise InvalidAPIUsage(ID_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_map.original})
