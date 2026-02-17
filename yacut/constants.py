import re
import string

# Constants for short URL generation
SHORT_LENGTH = 6
SHORT_MAX_LENGTH = 16
CHARACTERS = string.ascii_letters + string.digits
SHORT_PATTERN = f'^[{re.escape(CHARACTERS)}]+$'
MAX_ORIGINAL_LENGTH = 2048
MAX_ATTEMPTS = 100

# Validation messages
ID_EXISTS_MESSAGE = 'Предложенный вариант короткой ссылки уже существует.'
REQUIRED_FIELD_MESSAGE = 'Обязательное поле'
INVALID_URL_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
URL_TOO_LONG_MESSAGE = 'URL слишком длинный'
FILE_REQUIRED_MESSAGE = 'Выберите файл для загрузки'
MESSAGE_WORDS = 'Только буквы и цифры'
FAILED_MESSAGE = 'Не удалось сгенерировать уникальный короткий идентификатор'

# Form labels
ORIGINAL_LINK_LABEL = 'Длинная ссылка'
SHORT_LABEL = 'Ваш вариант короткой ссылки'
FILE_LABEL = 'Файл не выбран'

# Button labels
CREATE_BUTTON = 'Создать'
UPLOAD_BUTTON = 'Загрузить'

# Reserved words
RESERVED_WORDS = {'files'}

# Endpoint names
ENDPOINT = 'redirect_to_original'

# API error messages
EMPTY_REQUEST_MESSAGE = 'Отсутствует тело запроса'
MISSING_URL_MESSAGE = '"url" является обязательным полем!'
ID_NOT_FOUND_MESSAGE = 'Указанный id не найден'
# File upload error messages
FILE_UPLOAD_ERROR = 'Ошибка загрузки файлов: {}'
FILE_PROCESS_ERROR = 'Ошибка обработки результатов: {}'
FILE_NOT_FOUND_MESSAGE = 'Файл не найден на Яндекс Диске'
FILE_DOWNLOAD_ERROR = 'Ошибка при получении файла: {}'

# Yandex Disk API error messages
DISK_INFO_ERROR = 'Не удалось получить информацию о Диске: статус {}'
UPLOAD_URL_ERROR = 'Не удалось получить URL для загрузки {}: статус {}'
UPLOAD_FILE_ERROR = 'Не удалось загрузить файл: статус {}'
DOWNLOAD_LINK_ERROR = 'Не удалось получить ссылку на скачивание {}: статус {}'
UPLOAD_FAILED_MESSAGE = 'Ошибка при загрузке файла'
# File storage prefix
FILE_PREFIX = 'file: '