from http import HTTPStatus

from flask import abort, flash, redirect, render_template

from . import app, db
from .constants import SHORT_REDIRECT_ENDPOINT
from .forms import FileForm, MainForm
from .models import URLMap
from .yandx_disk import get_file_download_link_sync, get_files_yandex_disk_urls

# File operation messages
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
        short_link = URLMap.create(
            form.original_link.data,
            form.custom_id.data,
            skip_short_validation=True,
            skip_url_validation=bool(form.custom_id.data)
        ).get_short_url()
    except Exception as e:
        flash(str(e))
        return render_template('index.html', form=form)
    return render_template('index.html',
                           form=form, short_link=short_link)


@app.route('/files', methods=['GET', 'POST'], endpoint='files_page')
def files_page():
    """Страница для загрузки файлов."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)
    try:
        files_info = get_files_yandex_disk_urls(form.files.data)
    except Exception as e:
        flash(FILE_UPLOAD_ERROR.format(e))
        return render_template('files.html', form=form)
    try:
        uploaded_files = [
            {
                'filename': file_info['filename'],
                'short_link': URLMap.create(
                    f'file: {file_info["file_path"]}',
                    commit=False
                ).get_short_url()
            }
            for file_info in files_info
        ]
        if files_info:
            db.session.commit()
    except Exception as e:
        flash(FILE_PROCESS_ERROR.format(e))
        return render_template('files.html', form=form)
    return render_template('files.html',
                           form=form, uploaded_files=uploaded_files)


@app.route('/<short>', endpoint=SHORT_REDIRECT_ENDPOINT)
def redirect_to_original(short):
    """Переадресация по короткой ссылке."""
    if not (url_map := URLMap.get_url_map(short)):
        abort(HTTPStatus.NOT_FOUND)
    if url_map.original.startswith('file: '):
        return redirect(get_file_download_link_sync(
            url_map.original[len('file: '):]
        ))
    return redirect(url_map.original)
