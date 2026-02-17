### Как запустить проект Yacut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yandex-praktikum/async-yacut.git
```

```
cd async-yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///db.sqlite3
DISK_TOKEN=your_yandex_disk_token
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```

После запуска сервера API документация доступна по адресу:
[Swagger UI](http://localhost:5000/swagger)

### Технологический стек:

- Python 3.9+
- Flask 2.0+
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Migrate
- aiohttp (для асинхронной работы с Яндекс.Диск)
- SQLite (в режиме разработки)

### Автор:

Михаил Анисимов
- [GitHub](https://github.com/zerdocs122)
- [Email](Dogsig22@gmail@gmail.com)
