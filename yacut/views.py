from http import HTTPStatus

from flask import abort, flash, redirect, render_template, url_for

from . import app
from .forms import FileForm, MainForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'], endpoint='index')
def index():
    """Главная страница для создания коротких ссылок."""
    form = MainForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    short = form.custom_id.data
    try:
        new_url = URLMap.create(form.original_link.data, short)
    except ValueError as e:
        flash(str(e))
        return render_template('index.html', form=form)

    flash(f'Ваша короткая ссылка: {new_url.get_short_url()}')
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'], endpoint='files_page')
def files_page():
    """Страница для загрузки файлов."""
    form = FileForm()
    uploaded_files = []

    if form.validate_on_submit() and form.files.data:
        uploaded_files = process_files_upload(form.files.data)

    return render_template('files.html',
                           form=form, uploaded_files=uploaded_files)


def process_files_upload(files):
    """Обрабатывает загрузку файлов на Яндекс Диск."""
    from .yandx_disk import upload_multiple_files_sync

    upload_results = upload_multiple_files_sync(files)

    uploaded_files = [
        process_upload_result(result) for result in upload_results
        if process_upload_result(result)
    ]

    if uploaded_files:
        flash('Файлы успешно загружены на Яндекс Диск')

    return uploaded_files


def process_upload_result(result):
    """Обрабатывает результат загрузки одного файла."""
    if result.get('error') is not None:
        flash(f'Ошибка загрузки {result["filename"]}: {result["error"]}')
        return None

    from .yandx_disk import get_file_download_link_sync

    short = URLMap.generate_short()
    file_path = result['path']
    download_link = get_file_download_link_sync(file_path)

    URLMap.create_file_entry(file_path, short)

    return {
        'filename': result['filename'],
        'short_link': url_for('redirect_to_original',
                              short=short, _external=True),
        'download_link': download_link
    }


@app.route('/<short>', endpoint='redirect_to_original')
def redirect_to_original(short):
    """Переадресация по короткой ссылке."""
    url_map = URLMap.get_by_short(short)

    if not url_map:
        abort(HTTPStatus.NOT_FOUND)

    if url_map.original.startswith('file:'):
        try:
            from .yandx_disk import get_file_download_link_sync
            download_link = get_file_download_link_sync(
                url_map.original[5:]
            )

            if download_link:
                return redirect(download_link)
            else:
                return "Файл не найден на Яндекс Диске", HTTPStatus.NOT_FOUND

        except Exception as e:
            return (
                f"Ошибка при получении файла: {e}",
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

    return redirect(url_map.original)