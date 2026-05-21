"""
urls.py (застосунку dental_app) — маршрути URL.
Тут визначається яка функція з views.py викликається для кожної адреси.
Коли браузер відкриває певну адресу — Django шукає відповідний маршрут тут.
"""

# path — функція для створення маршруту URL
from django.urls import path

# Імпортуємо всі функції-представлення з views.py
from . import views

# urlpatterns — список маршрутів.
# Django перебирає їх зверху вниз і зупиняється на першому що підходить.
urlpatterns = [

    # path('', views.home, name='home')
    # '' — порожній рядок = головна сторінка (/)
    # views.home — функція яку викликати
    # name='home' — ім'я маршруту (використовується в шаблонах: {% url 'home' %})
    path('', views.home, name='home'),

    # /doctors/ → викликає функцію doctors_list
    path('doctors/', views.doctors_list, name='doctors'),

    # /doctors/1/ → викликає doctor_detail з doctor_id=1
    # <int:doctor_id> — змінна частина URL, int означає ціле число
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    # /patients/ → список пацієнтів
    path('patients/', views.patients_list, name='patients'),

    # /patients/2/ → деталі пацієнта з id=2
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),

    # /appointments/ → список прийомів
    path('appointments/', views.appointments_list, name='appointments'),
]
