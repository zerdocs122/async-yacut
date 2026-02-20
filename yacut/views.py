import asyncio
from http import HTTPStatus

import aiohttp
from flask import abort, flash, redirect, render_template

from . import app, db
from .constants import SHORT_REDIRECT_ENDPOINT
from .forms import FileForm, MainForm
from .models import URLMap
from .yandx_disk import get_files_yandex_disk_urls

FILE_UPLOAD_ERROR = 'Ошибка загрузки файлов: {}'
FILE_PROCESS_ERROR = 'Ошибка обработки результатов: {}'
FILE_NOT_FOUND = 'Файл не найден на Яндекс Диске'
FILE_DOWNLOAD_ERROR = 'Ошибка при получении файла: {}'


@app.route('/', methods=['GET', 'POST'], endpoint='index')
def index():
    """Главная страница для создания коротких ссылок."""
    form = MainForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    try:
        url_map = URLMap.create(
            form.original_link.data,
            form.custom_id.data,
            skip_short_validation=True,
            skip_url_validation=False
        )
    except (ValueError, RuntimeError) as error:
        flash(str(error))
        return render_template('index.html', form=form)

    return render_template(
        'index.html',
        form=form,
        short_link=url_map.get_short_url()
    )


@app.route('/files', methods=['GET', 'POST'], endpoint='files_page')
def files_page():
    """Страница для загрузки файлов."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)
    try:
        files_info = get_files_yandex_disk_urls(form.files.data)
    except (RuntimeError, aiohttp.ClientError, asyncio.TimeoutError,
            OSError, ValueError) as error:
        flash(FILE_UPLOAD_ERROR.format(error))
        return render_template('files.html', form=form)
    try:
        uploaded_files = []
        for file, download_link in zip(form.files.data, files_info):
            url_map = URLMap.create(download_link, commit=False)
            uploaded_files.append(
                {
                    'filename': file.filename,
                    'short_link': url_map.get_short_url(),
                }
            )
        db.session.commit()
        return render_template(
            'files.html',
            form=form,
            uploaded_files=uploaded_files
        )
    except (ValueError, RuntimeError) as error:
        flash(FILE_PROCESS_ERROR.format(error))
        return render_template('files.html', form=form)


@app.route('/<short>', endpoint=SHORT_REDIRECT_ENDPOINT)
def redirect_to_original(short):
    """Переадресация по короткой ссылке."""
    if not (url_map := URLMap.get(short)):
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)
