import asyncio
import os
import urllib.parse
from http import HTTPStatus

import aiohttp
from dotenv import load_dotenv

from settings import Config

from .constants import (DISK_INFO_ERROR, DOWNLOAD_LINK_ERROR,
                        UPLOAD_FAILED_MESSAGE, UPLOAD_FILE_ERROR,
                        UPLOAD_URL_ERROR)

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
    tasks = [
        asyncio.create_task(
            upload_single_file(file.filename, file.read())
        )
        for file in files
    ]
    return [
        {
            'filename': files[i].filename,
            'error': str(result) if isinstance(result, Exception)
            else UPLOAD_FAILED_MESSAGE if not result else None,
            'path': result if not isinstance(result, Exception) and result
            else None
        }
        for i, result in enumerate(await asyncio.gather(*tasks))
    ]


async def upload_single_file(filename, file_content):
    """Загрузить один файл на Диск."""
    try:
        return await upload_file(
            await get_upload_url(filename), file_content)
    except RuntimeError as e:
        return e


def upload_multiple_files_sync(files):
    """Синхронная обёртка для загрузки файлов."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(upload_multiple_files(files))
    finally:
        loop.close()


def get_file_download_link_sync(file_path):
    """Синхронная обёртка для получения ссылки на скачивание."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_download_link(file_path))
    finally:
        loop.close()


def process_file_result(result):
    """Обработать результат загрузки файла и получить download_link."""
    file_path = result['path']
    download_link = get_file_download_link_sync(file_path)
    return {
        'filename': result['filename'],
        'file_path': file_path,
        'download_link': download_link
    }
