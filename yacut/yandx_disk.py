import asyncio
import os
import urllib.parse
from http import HTTPStatus

import aiohttp
from dotenv import load_dotenv

from settings import Config

# Yandex Disk API error messages
DISK_INFO_ERROR = 'Не удалось получить информацию о Диске: статус {}'
UPLOAD_URL_ERROR = 'Не удалось получить URL для загрузки {}: статус {}'
UPLOAD_FILE_ERROR = 'Не удалось загрузить файл: статус {}'
DOWNLOAD_LINK_ERROR = 'Не удалось получить ссылку на скачивание {}: статус {}'
UPLOAD_FAILED = 'Ошибка при загрузке файла'

load_dotenv()

API_BASE_URL = f'{Config.API_HOST}{Config.API_VERSION}'
DISK_INFO_URL = f'{API_BASE_URL}/disk/'
UPLOAD_URL = f'{API_BASE_URL}/disk/resources/upload'
DOWNLOAD_URL = f'{API_BASE_URL}/disk/resources/download'
DISK_TOKEN = os.environ.get('DISK_TOKEN')

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def get_disk_info():
    """Получить информацию о Диске."""
    async with aiohttp.ClientSession() as session:
        async with session.get(DISK_INFO_URL,
                               headers=AUTH_HEADERS) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()
            raise RuntimeError(DISK_INFO_ERROR.format(response.status))


async def get_upload_url(filename, overwrite=True):
    """Получить URL для загрузки файла."""
    params = {
        'path': f'app: /{filename}',
        'overwrite': str(overwrite).lower()
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(UPLOAD_URL,
                               headers=AUTH_HEADERS,
                               params=params) as response:
            if response.status == HTTPStatus.OK:
                return (await response.json()).get('href')
            raise RuntimeError(
                UPLOAD_URL_ERROR.format(filename, response.status))


async def upload_file(upload_url, file_content):
    """Загрузить файл на Диск по полученному URL."""
    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=file_content) as response:
            if response.status == HTTPStatus.CREATED:
                location = response.headers.get('Location', '')
                return urllib.parse.unquote(location).replace('/disk', '')
            raise RuntimeError(UPLOAD_FILE_ERROR.format(response.status))


async def get_download_link(file_path):
    """Получить ссылку для скачивания файла."""
    params = {'path': file_path}
    async with aiohttp.ClientSession() as session:
        async with session.get(DOWNLOAD_URL,
                               headers=AUTH_HEADERS,
                               params=params) as response:
            if response.status == HTTPStatus.OK:
                return (await response.json()).get('href')
            raise RuntimeError(
                DOWNLOAD_LINK_ERROR.format(file_path, response.status))


async def upload_multiple_files(files):
    """Асинхронная загрузка нескольких файлов."""
    return await asyncio.gather(
        *[
            asyncio.create_task(
                upload_single_file(file.filename, file.read())
            )
            for file in files
        ]
    )


async def upload_files_and_get_urls(files):
    """Загрузить файлы на Яндекс Диск и получить их URL."""
    upload_results = await upload_multiple_files(files)
    download_tasks = [
        get_download_link(file_path)
        for file_path in upload_results
    ]
    return await asyncio.gather(*download_tasks)


async def upload_single_file(filename, file_content):
    """Загрузить один файл на Диск."""
    return await upload_file(await get_upload_url(filename), file_content)


def upload_multiple_files_sync(files):
    """Синхронная обёртка для загрузки файлов."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(upload_multiple_files(files))
    finally:
        loop.close()


def get_files_yandex_disk_urls(files):
    """Загрузить файлы на Яндекс Диск и получить их URL."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(upload_files_and_get_urls(files))
    finally:
        loop.close()


def get_file_download_link_sync(file_path):
    """Синхронная обёртка для получения ссылки на скачивание."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_download_link(file_path))
    finally:
        loop.close()
