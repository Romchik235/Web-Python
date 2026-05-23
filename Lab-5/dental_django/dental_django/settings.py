"""
settings.py — налаштування Django проекту для лаб 5.
Відмінність від лаб 4: додано DATABASES (SQLite), сесії, messages.
"""

from pathlib import Path

# Абсолютний шлях до кореневої папки проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретний ключ для шифрування даних (CSRF, сесії тощо)
SECRET_KEY = 'django-insecure-dental-lab5-secret-key-2026'

# DEBUG=True — режим розробки, показує детальні помилки
DEBUG = True

# Дозволені хости — '*' дозволяє всі (тільки для розробки)
ALLOWED_HOSTS = ['*']

# Підключені застосунки Django
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'dental',
]

# Middleware — обробники запитів по черзі
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    # НОВЕ в лаб 5: SessionMiddleware — підтримка сесій
    # Сесії зберігають дані між запитами (наприклад роль користувача)
    'django.contrib.sessions.middleware.SessionMiddleware',
    # НОВЕ в лаб 5: MessageMiddleware — підтримка flash-повідомлень
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Головний файл маршрутів
ROOT_URLCONF = 'dental_django.urls'

# Налаштування шаблонізатора
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,  # шукати шаблони в templates/ застосунку
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        # НОВЕ в лаб 5: процесор для повідомлень
        # Автоматично додає messages в контекст кожного шаблону
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# DATABASES — НОВЕ в лаб 5 (в лаб 4 цього не було!)
# Налаштування підключення до бази даних
DATABASES = {
    'default': {
        # ENGINE — який тип БД використовувати
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite — вбудований в Python, не потрібен сервер
        # NAME — шлях до файлу бази даних
        # BASE_DIR / 'dental.db' — файл dental.db в папці проекту
        'NAME': BASE_DIR / 'dental.db',
    }
}

# SESSION_ENGINE — де зберігати сесії
# db — в базі даних (таблиця django_session)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# URL префікс для статичних файлів
STATIC_URL = '/static/'

# Тип автоінкрементного поля id за замовчуванням
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
