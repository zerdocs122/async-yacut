import asyncio
import os
import urllib.parse

import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
DISK_TOKEN = os.environ.get('DISK_TOKEN')

AUTH_HEADERS = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}


async def get_disk_info():
    """Получить информацию о Диске."""
    url = f'{API_HOST}{API_VERSION}/disk/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=AUTH_HEADERS) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def get_upload_url(filename, overwrite=True):
    """Получить URL для загрузки файла."""
    url = f'{API_HOST}{API_VERSION}/disk/resources/upload'
    params = {
        'path': f'app: /{filename}',
        'overwrite': str(overwrite).lower()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               headers=AUTH_HEADERS,
                               params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('href')
            else:
                return None


async def upload_file(upload_url, file_content):
    """Загрузить файл на Диск по полученному URL."""
    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=file_content) as response:
            if response.status == 201:
                location = response.headers.get('Location', '')
                # Декодируем URL и убираем префикс /disk
                location = urllib.parse.unquote(location).replace('/disk', '')
                return location
            else:
                return None


async def get_download_link(file_path):
    """Получить ссылку для скачивания файла."""
    url = f'{API_HOST}{API_VERSION}/disk/resources/download'
    params = {'path': file_path}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=AUTH_HEADERS,
                               params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('href')
            else:
                return None


async def upload_multiple_files(files):
    """Асинхронная загрузка нескольких файлов."""
    results = []

    tasks = []
    for file in files:
        if file and file.filename:
            task = asyncio.create_task(
                upload_single_file(file.filename, file.read())
            )
            tasks.append(task)

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = {
                    'filename': files[i].filename,
                    'error': str(result)
                }
            elif result:
                results[i] = {
                    'filename': files[i].filename,
                    'path': result
                }
            else:
                results[i] = {
                    'filename': files[i].filename,
                    'error': 'Failed to upload file'
                }

    return results


async def upload_single_file(filename, file_content):
    """Загрузить один файл на Диск."""
    # Получаем URL для загрузки
    upload_url = await get_upload_url(filename)
    if not upload_url:
        raise Exception(f"Failed to get upload URL for {filename}")

    # Загружаем файл
    location = await upload_file(upload_url, file_content)
    if not location:
        raise Exception(f"Failed to upload {filename}")

    return location