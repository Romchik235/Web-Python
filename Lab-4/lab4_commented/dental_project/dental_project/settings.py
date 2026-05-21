"""
settings.py — головний файл налаштувань Django проекту.
Всі параметри застосунку задаються тут.
"""

# Path — клас для роботи зі шляхами файлової системи
from pathlib import Path

# BASE_DIR — абсолютний шлях до кореневої папки проекту
# __file__ — шлях до поточного файлу (settings.py)
# .resolve() — отримуємо абсолютний шлях
# .parent.parent — піднімаємось на 2 рівні вгору (до папки dental_project)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY — секретний ключ для шифрування сесій, CSRF токенів тощо.
# У production (на сервері) має бути складним та секретним!
SECRET_KEY = 'django-insecure-dental-lab4-secret-key-2026'

# DEBUG = True — режим розробки.
# Показує детальні помилки в браузері.
# У production завжди має бути False!
DEBUG = True

# ALLOWED_HOSTS — список дозволених хостів для запитів.
# '*' означає дозволити всі хости (для розробки зручно, в production небезпечно)
ALLOWED_HOSTS = ['*']

# INSTALLED_APPS — список підключених застосунків Django.
# Django підключає лише те що перераховано тут.
INSTALLED_APPS = [
    'django.contrib.contenttypes',  # система типів контенту Django
    'django.contrib.staticfiles',   # обробка статичних файлів (CSS, JS, зображення)
    'dental_app',                   # наш власний застосунок
]

# MIDDLEWARE — список проміжного ПЗ.
# Кожен middleware обробляє запит/відповідь по черзі.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # безпека
    'django.middleware.common.CommonMiddleware',           # загальні перевірки URL
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # захист від clickjacking
]

# ROOT_URLCONF — шлях до головного файлу маршрутів.
# Django шукає urlpatterns саме в цьому модулі.
ROOT_URLCONF = 'dental_project.urls'

# TEMPLATES — налаштування шаблонізатора.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DjangoTemplates — стандартний шаблонізатор Django (DTL)

        'DIRS': [],
        # DIRS — додаткові папки де шукати шаблони (порожньо = не шукати окремо)

        'APP_DIRS': True,
        # APP_DIRS: True — шукати шаблони в папці templates/ всередині кожного застосунку
        # Тому наші шаблони лежать в dental_app/templates/dental_app/

        'OPTIONS': {
            'context_processors': [
                # context_processors — функції що автоматично додають змінні в кожен шаблон
                'django.template.context_processors.debug',    # змінна debug
                'django.template.context_processors.request',  # змінна request
            ],
        },
    },
]

# STATIC_URL — URL префікс для статичних файлів (CSS, JS, зображення)
STATIC_URL = '/static/'

# DEFAULT_AUTO_FIELD — тип поля id за замовчуванням для моделей.
# BigAutoField — великий автоінкрементний integer (64-біт)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ПРИМІТКА: У лаб 4 немає розділу DATABASES — бо ми не використовуємо базу даних!
# Всі дані зберігаються у файлі data.py як Python списки.
