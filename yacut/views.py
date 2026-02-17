from http import HTTPStatus

from flask import abort, flash, redirect, render_template

from . import app
from .constants import (ENDPOINT, FILE_DOWNLOAD_ERROR, FILE_NOT_FOUND_MESSAGE,
                        FILE_PREFIX, FILE_PROCESS_ERROR, FILE_UPLOAD_ERROR)
from .forms import FileForm, MainForm
from .models import URLMap
from .yandx_disk import (get_file_download_link_sync, process_file_result,
                         upload_multiple_files_sync)


@app.route('/', methods=['GET', 'POST'], endpoint='index')
def index():
    """Главная страница для создания коротких ссылок."""
    form = MainForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        url_map = URLMap.create(form.original_link.data, form.custom_id.data)
    except ValueError as e:
        flash(str(e))
        return render_template('index.html', form=form)

    return render_template('index.html',
                           form=form, short_link=url_map.get_short_url())


@app.route('/files', methods=['GET', 'POST'], endpoint='files_page')
def files_page():
    """Страница для загрузки файлов."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form, uploaded_files=[])

    try:
        upload_results = upload_multiple_files_sync(form.files.data)
    except RuntimeError as e:
        flash(FILE_UPLOAD_ERROR.format(e))
        return render_template('files.html', form=form, uploaded_files=[])

    try:
        uploaded_files = []
        for result in upload_results:
            file_info = process_file_result(result)
            url_map = URLMap.create_file_entry(file_info['file_path'])
            uploaded_files.append({
                'filename': file_info['filename'],
                'short_link': url_map.get_short_url(),
                'download_link': file_info['download_link']
            })
    except (RuntimeError, KeyError) as e:
        flash(FILE_PROCESS_ERROR.format(e))
        return render_template('files.html', form=form, uploaded_files=[])

    return render_template('files.html',
                           form=form, uploaded_files=uploaded_files)


@app.route('/<short>', endpoint=ENDPOINT)
def redirect_to_original(short):
    """Переадресация по короткой ссылке."""
    if not (url_map := URLMap.get_short(short)):
        abort(HTTPStatus.NOT_FOUND)

    if url_map.original.startswith(FILE_PREFIX):
        try:
            download_link = get_file_download_link_sync(
                url_map.original[len(FILE_PREFIX):]
            )

            if download_link:
                return redirect(download_link)
            else:
                return FILE_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND

        except RuntimeError as e:
            return (
                FILE_DOWNLOAD_ERROR.format(e),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

    return redirect(url_map.original)
