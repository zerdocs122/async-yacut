import re
import string

SHORT_LENGTH = 6
SHORT_MAX_LENGTH = 16
CHARACTERS = string.ascii_letters + string.digits
SHORT_PATTERN = f'^[{re.escape(CHARACTERS)}]+$'
MAX_ORIGINAL_LENGTH = 2048
MAX_ATTEMPTS = 100
SHORT_RESERVED = {'files'}
SHORT_REDIRECT_ENDPOINT = 'redirect_to_original'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
SHORT_INVALID_URL = 'Указано недопустимое имя для короткой ссылки'
