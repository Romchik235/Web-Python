"""
urls.py (головний, рівня проекту dental_project) — кореневі маршрути.
Це точка входу для всіх URL. Django спочатку заходить сюди,
а потім передає управління в urls.py застосунку.
"""

# path — створення маршруту
# include — підключення URL з іншого файлу
from django.urls import path, include

urlpatterns = [
    # path('', include('dental_app.urls'))
    # '' — всі адреси починаючи з кореня /
    # include('dental_app.urls') — передаємо управління в dental_app/urls.py
    # Тобто коли приходить запит на /doctors/ — Django передає його
    # у файл dental_app/urls.py де вже шукається точний маршрут
    path('', include('dental_app.urls')),
]
