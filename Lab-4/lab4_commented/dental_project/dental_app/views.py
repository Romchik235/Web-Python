"""
views.py — представлення (функції-обробники) для Django.
Кожна функція тут відповідає за одну сторінку сайту.
Django викликає потрібну функцію коли браузер звертається на певну адресу.
"""

# render — функція яка поєднує шаблон з даними і повертає HTML сторінку
from django.shortcuts import render

# Імпортуємо фіксовані дані з нашого файлу data.py
# DOCTORS, PATIENTS, APPOINTMENTS — це списки словників
from .data import DOCTORS, PATIENTS, APPOINTMENTS


# ============ ГОЛОВНА СТОРІНКА ============

def home(request):
    """
    Обробник головної сторінки (адреса: /).
    request — об'єкт HTTP запиту від браузера (містить GET/POST дані, сесію, тощо).
    """
    # render приймає: request, назву шаблону, словник з даними для шаблону
    # {'title': 'Головна'} — передаємо змінну title в шаблон home.html
    return render(request, 'dental_app/home.html', {'title': 'Головна'})


# ============ ЛІКАРІ ============

def doctors_list(request):
    """
    Список всіх лікарів (адреса: /doctors/).
    Передаємо весь список DOCTORS в шаблон.
    """
    # Передаємо список лікарів і заголовок сторінки в шаблон doctors.html
    return render(request, 'dental_app/doctors.html', {
        'doctors': DOCTORS,  # весь список лікарів з data.py
        'title': 'Лікарі'   # заголовок сторінки
    })


def doctor_detail(request, doctor_id):
    """
    Деталі одного лікаря (адреса: /doctors/<id>/).
    doctor_id — число з URL, наприклад /doctors/1/ → doctor_id = 1
    """
    # next() знаходить перший елемент списку що відповідає умові
    # d for d in DOCTORS if d['id'] == doctor_id — перебираємо лікарів,
    # шукаємо того у кого id збігається з переданим doctor_id
    # None — повертаємо None якщо лікаря не знайдено
    doctor = next((d for d in DOCTORS if d['id'] == doctor_id), None)

    # Якщо лікаря не знайдено — повертаємо помилку 404 (Не знайдено)
    if not doctor:
        from django.http import Http404  # імпортуємо клас помилки
        raise Http404("Лікаря не знайдено")  # Django показує сторінку 404

    # Передаємо дані одного лікаря в шаблон doctor_detail.html
    return render(request, 'dental_app/doctor_detail.html', {
        'doctor': doctor,  # словник з даними одного лікаря
        'title': f"Лікар: {doctor['name']} {doctor['surname']}"  # заголовок сторінки
    })


# ============ ПАЦІЄНТИ ============

def patients_list(request):
    """
    Список всіх пацієнтів (адреса: /patients/).
    """
    return render(request, 'dental_app/patients.html', {
        'patients': PATIENTS,  # весь список пацієнтів з data.py
        'title': 'Пацієнти'
    })


def patient_detail(request, patient_id):
    """
    Деталі одного пацієнта (адреса: /patients/<id>/).
    patient_id — число з URL.
    """
    # Шукаємо пацієнта за id — аналогічно до doctor_detail
    patient = next((p for p in PATIENTS if p['id'] == patient_id), None)

    # Якщо пацієнта не знайдено — помилка 404
    if not patient:
        from django.http import Http404
        raise Http404("Пацієнта не знайдено")

    return render(request, 'dental_app/patient_detail.html', {
        'patient': patient,  # словник з даними одного пацієнта
        'title': f"Пацієнт: {patient['name']} {patient['surname']}"
    })


# ============ ПРИЙОМИ ============

def appointments_list(request):
    """
    Список всіх прийомів (адреса: /appointments/).
    """
    return render(request, 'dental_app/appointments.html', {
        'appointments': APPOINTMENTS,  # весь список прийомів з data.py
        'title': 'Прийоми'
    })
