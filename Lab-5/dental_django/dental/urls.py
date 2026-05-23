"""
urls.py — маршрути URL для лабораторної роботи №5.
На відміну від лаб 4 — тут є маршрути для CRUD операцій (add/edit/delete).
"""

from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка
    path('', views.home, name='home'),

    # --- ЛІКАРІ ---
    # /doctors/ → список лікарів
    path('doctors/', views.doctors_list, name='doctors_list'),
    # /doctors/add/ → форма додавання
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    # /doctors/3/edit/ → форма редагування лікаря з id=3
    # <int:pk> — змінна pk (primary key) типу integer з URL
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    # /doctors/3/delete/ → підтвердження видалення лікаря з id=3
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),

    # --- ПАЦІЄНТИ ---
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    # --- ПРИЙОМИ ---
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/add/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
]
