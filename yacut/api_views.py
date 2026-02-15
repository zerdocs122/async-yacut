import re

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap, get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API эндпоинт для создания короткой ссылки."""
    data = request.get_json(force=True, silent=True)

    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    # Проверка валидности URL
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )

    if not url_pattern.match(url):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')

    if custom_id:
        if custom_id == 'files':
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.')

        if len(custom_id) > 16 or not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки')

        existing_url = URLMap.query.filter_by(short=custom_id).first()
        if existing_url:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.')
        short_id = custom_id
    else:
        while True:
            short_id = get_unique_short_id()
            if not URLMap.query.filter_by(short=short_id).first():
                break

    new_url = URLMap(original=url, short=short_id)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        'url': url,
        'short_link': f'{request.host_url}{short_id}'
    }), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    """API эндпоинт для получения оригинальной ссылки."""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)

    if url_map.original.startswith('file:'):
        return jsonify({'url': f'file: {url_map.original[5:]}'})

    return jsonify({'url': url_map.original})