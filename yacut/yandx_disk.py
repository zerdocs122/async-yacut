import asyncio
import os
import urllib.parse
from http import HTTPStatus

import aiohttp
from dotenv import load_dotenv

from settings import Config

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
            raise Exception(
                f'Failed to get disk info: status {response.status}')


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
            raise Exception(
                f'Failed to get upload URL for {filename}: '
                f'status {response.status}')


async def upload_file(upload_url, file_content):
    """Загрузить файл на Диск по полученному URL."""
    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=file_content) as response:
            if response.status == HTTPStatus.CREATED:
                location = response.headers.get('Location', '')
                return urllib.parse.unquote(location).replace('/disk', '')
            raise Exception(
                f'Failed to upload file: status {response.status}')


async def get_download_link(file_path):
    """Получить ссылку для скачивания файла."""
    params = {'path': file_path}
    async with aiohttp.ClientSession() as session:
        async with session.get(DOWNLOAD_URL,
                               headers=AUTH_HEADERS,
                               params=params) as response:
            if response.status == HTTPStatus.OK:
                return (await response.json()).get('href')
            raise Exception(
                f'Failed to get download link for {file_path}: '
                f'status {response.status}')


async def upload_multiple_files(files):
    """Асинхронная загрузка нескольких файлов."""
    tasks = [
        asyncio.create_task(
            upload_single_file(file.filename, file.read())
        )
        for file in files if file and file.filename
    ]
    if not tasks:
        return []
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [
        {
            'filename': files[i].filename,
            'error': str(result) if isinstance(result, Exception)
            else 'Failed to upload file' if not result else None,
            'path': result if not isinstance(result, Exception) and result
            else None
        }
        for i, result in enumerate(results)
    ]


async def upload_single_file(filename, file_content):
    """Загрузить один файл на Диск."""
    return await upload_file(
        await get_upload_url(filename), file_content)


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