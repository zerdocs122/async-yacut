from flask import render_template, flash, request, redirect
import asyncio
from . import app, db
from .forms import MainForm, FileForm
from .models import URLMap, get_unique_short_id
from .yandx_disk import upload_multiple_files, get_download_link


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница для создания коротких ссылок."""
    form = MainForm()
    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data.strip() if form.custom_id.data else ''

        if custom_id:
            if custom_id == 'files':
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form)

            existing_url = URLMap.query.filter_by(short=custom_id).first()
            if existing_url:
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form)
            short_id = custom_id
        else:
            while True:
                short_id = get_unique_short_id()
                if not URLMap.query.filter_by(short=short_id).first():
                    break

        new_url = URLMap(
            original=original_link,
            short=short_id
        )
        db.session.add(new_url)
        db.session.commit()

        flash(
            f'Ваша короткая ссылка: {request.host_url}{short_id}'
        )
        return render_template('index.html', form=form)

    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def files_page():
    """Страница для загрузки файлов."""
    form = FileForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = form.files.data
        if files:
            uploaded_files = process_files_upload(files)

    return render_template('files.html',
                           form=form, uploaded_files=uploaded_files)


def process_files_upload(files):
    """Обрабатывает загрузку файлов на Яндекс Диск."""
    uploaded_files = []

    try:
        loop = asyncio.new_event_loop()
        upload_results = (
            loop.run_until_complete(upload_multiple_files(files))
        )

        for result in upload_results:
            file_info = process_upload_result(result)
            if file_info:
                uploaded_files.append(file_info)

        if uploaded_files:
            db.session.commit()
            flash('Файлы успешно загружены на Яндекс Диск')

    except Exception as e:
        flash(f'Ошибка при загрузке файлов: {str(e)}')

    return uploaded_files


def process_upload_result(result):
    """Обрабатывает результат загрузки одного файла."""
    if 'error' in result:
        flash(
            f'Ошибка загрузки {result["filename"]}:\n'
            f'{result["error"]}'
        )
        return None

    short_id = generate_unique_short_id()
    file_path = result['path']
    download_link = get_file_download_link(file_path)

    save_file_to_database(file_path, short_id)

    return {
        'filename': result['filename'],
        'short_link': f'{request.host_url}{short_id}',
        'download_link': download_link
    }


def generate_unique_short_id():
    """Генерирует уникальный короткий идентификатор."""
    while True:
        short_id = get_unique_short_id()
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def get_file_download_link(file_path):
    """Получает ссылку для скачивания файла."""
    try:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(
            get_download_link(file_path)
        )
    except Exception:
        return None


def save_file_to_database(file_path, short_id):
    """Сохраняет информацию о файле в базу данных."""
    new_url = URLMap(
        original=f'file: {file_path}',
        short=short_id
    )
    db.session.add(new_url)


@app.route('/<short_id>')
def redirect_to_original(short_id):
    """Переадресация по короткой ссылке."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()

    if url_map.original.startswith('file:'):
        try:
            loop = asyncio.new_event_loop()
            download_link = (
                loop.run_until_complete(
                    get_download_link(url_map.original[5:]))
            )

            if download_link:
                return redirect(download_link)
            else:
                return "Файл не найден на Яндекс Диске", 404

        except Exception as e:
            return (
                f"Ошибка при получении файла: {str(e)}", 500
            )

    return redirect(url_map.original)