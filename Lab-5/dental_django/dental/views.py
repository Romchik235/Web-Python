"""
views.py — представлення (обробники запитів) для лаб 5.
На відміну від лаб 4 — тут є база даних, форми, сесії та повний CRUD.
"""

# render — генерує HTML з шаблону + даних
# get_object_or_404 — знаходить об'єкт за id або повертає 404 якщо немає
# redirect — перенаправляє на іншу сторінку
from django.shortcuts import render, get_object_or_404, redirect

# messages — система flash-повідомлень Django (успіх, помилка, тощо)
from django.contrib import messages

# Імпортуємо моделі
from .models import Doctor, Patient, Appointment

# Імпортуємо форми
from .forms import DoctorForm, PatientForm, AppointmentForm


def get_role(request):
    """
    Допоміжна функція для визначення ролі поточного користувача.
    Спочатку перевіряємо URL параметр ?role=..., потім сесію.
    Якщо нічого немає — повертаємо 'user' за замовчуванням.
    """
    # request.GET.get('role', ...) — читаємо параметр role з URL (?role=admin)
    # request.session.get('role', 'user') — читаємо роль з сесії (збережена між запитами)
    return request.GET.get('role', request.session.get('role', 'user'))


# ============ ГОЛОВНА СТОРІНКА ============

def home(request):
    """Головна сторінка з лічильниками"""
    role = get_role(request)

    # Зберігаємо роль в сесії — щоб вона зберігалась між запитами
    # request.session — це як словник що зберігається на сервері між запитами
    request.session['role'] = role

    return render(request, 'dental/home.html', {
        'role': role,
        # .count() — SQL: SELECT COUNT(*) FROM ... — рахує кількість записів
        'doctors_count': Doctor.objects.count(),
        'patients_count': Patient.objects.count(),
        'appointments_count': Appointment.objects.count(),
    })


# ============ ЛІКАРІ ============

def doctors_list(request):
    """Список всіх лікарів"""
    role = get_role(request)
    # Doctor.objects.all() — отримуємо всіх лікарів з БД
    # SQL: SELECT * FROM dental_doctor
    doctors = Doctor.objects.all()
    return render(request, 'dental/doctors.html', {'doctors': doctors, 'role': role})


def doctor_create(request):
    """Додавання нового лікаря"""
    role = get_role(request)

    # Перевірка доступу — лише адмін може додавати
    if role != 'admin':
        # messages.error — додає повідомлення про помилку яке відобразиться на сторінці
        messages.error(request, 'Доступ заборонено. Потрібна роль адміністратора.')
        return redirect('doctors_list')  # перенаправляємо на список

    # request.POST or None:
    # якщо POST запит (відправка форми) — передаємо дані форми
    # якщо GET запит (відкриття сторінки) — передаємо None (порожня форма)
    form = DoctorForm(request.POST or None)

    # form.is_valid() — перевіряє всі валідатори форми
    # Повертає True якщо всі поля заповнені правильно
    if form.is_valid():
        # form.save() — зберігає дані форми в базу даних
        # SQL: INSERT INTO dental_doctor (name, surname, ...) VALUES (...)
        form.save()
        # messages.success — повідомлення про успіх (зелене)
        messages.success(request, 'Лікаря успішно додано!')
        return redirect(f'/doctors/?role=admin')

    # Якщо форма не валідна або GET запит — показуємо форму
    # form з помилками валідації буде автоматично відображена в шаблоні
    return render(request, 'dental/doctor_form.html', {
        'form': form,
        'role': role,
        'action': 'Додати'  # заголовок кнопки
    })


def doctor_update(request, pk):
    """Редагування існуючого лікаря. pk — primary key (id) лікаря"""
    role = get_role(request)
    if role != 'admin':
        return redirect('doctors_list')

    # get_object_or_404 — знаходить лікаря за pk
    # якщо не знайдено — автоматично повертає сторінку 404
    # SQL: SELECT * FROM dental_doctor WHERE id = pk LIMIT 1
    doctor = get_object_or_404(Doctor, pk=pk)

    # instance=doctor — передаємо існуючий об'єкт щоб форма заповнилась поточними даними
    form = DoctorForm(request.POST or None, instance=doctor)

    if form.is_valid():
        # form.save() з instance — оновлює існуючий запис
        # SQL: UPDATE dental_doctor SET name=... WHERE id=pk
        form.save()
        messages.success(request, 'Дані лікаря оновлено!')
        return redirect(f'/doctors/?role=admin')

    return render(request, 'dental/doctor_form.html', {
        'form': form, 'role': role,
        'action': 'Редагувати',
        'object': doctor  # передаємо об'єкт для відображення в заголовку
    })


def doctor_delete(request, pk):
    """Видалення лікаря. Потребує підтвердження (POST запит)"""
    role = get_role(request)
    if role != 'admin':
        return redirect('doctors_list')

    doctor = get_object_or_404(Doctor, pk=pk)

    # Видалення відбувається лише при POST запиті (після підтвердження)
    # GET запит — показує сторінку підтвердження
    if request.method == 'POST':
        # doctor.delete() — видаляє запис з БД
        # SQL: DELETE FROM dental_doctor WHERE id = pk
        doctor.delete()
        messages.success(request, 'Лікаря видалено!')
        return redirect(f'/doctors/?role=admin')

    # GET — показуємо сторінку підтвердження видалення
    return render(request, 'dental/confirm_delete.html', {
        'object': doctor, 'role': role, 'type': 'Лікар'
    })


# ============ ПАЦІЄНТИ ============

def patients_list(request):
    """Список всіх пацієнтів"""
    role = get_role(request)
    patients = Patient.objects.all()
    return render(request, 'dental/patients.html', {'patients': patients, 'role': role})


def patient_create(request):
    """Додавання нового пацієнта"""
    role = get_role(request)
    if role != 'admin':
        return redirect('patients_list')
    form = PatientForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Пацієнта успішно додано!')
        return redirect(f'/patients/?role=admin')
    return render(request, 'dental/patient_form.html', {'form': form, 'role': role, 'action': 'Додати'})


def patient_update(request, pk):
    """Редагування пацієнта"""
    role = get_role(request)
    if role != 'admin':
        return redirect('patients_list')
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        messages.success(request, 'Дані пацієнта оновлено!')
        return redirect(f'/patients/?role=admin')
    return render(request, 'dental/patient_form.html', {
        'form': form, 'role': role, 'action': 'Редагувати', 'object': patient
    })


def patient_delete(request, pk):
    """Видалення пацієнта з підтвердженням"""
    role = get_role(request)
    if role != 'admin':
        return redirect('patients_list')
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Пацієнта видалено!')
        return redirect(f'/patients/?role=admin')
    return render(request, 'dental/confirm_delete.html', {
        'object': patient, 'role': role, 'type': 'Пацієнт'
    })


# ============ ПРИЙОМИ ============

def appointments_list(request):
    """Список всіх прийомів"""
    role = get_role(request)
    # select_related('patient', 'doctor') — оптимізація:
    # завантажує пов'язані об'єкти одним SQL запитом замість N запитів
    # SQL: SELECT ... FROM appointment JOIN patient JOIN doctor
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    return render(request, 'dental/appointments.html', {
        'appointments': appointments, 'role': role
    })


def appointment_create(request):
    """Додавання нового прийому"""
    role = get_role(request)
    if role != 'admin':
        return redirect('appointments_list')
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Прийом успішно додано!')
        return redirect(f'/appointments/?role=admin')
    return render(request, 'dental/appointment_form.html', {
        'form': form, 'role': role, 'action': 'Додати'
    })


def appointment_update(request, pk):
    """Редагування прийому"""
    role = get_role(request)
    if role != 'admin':
        return redirect('appointments_list')
    appt = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appt)
    if form.is_valid():
        form.save()
        messages.success(request, 'Прийом оновлено!')
        return redirect(f'/appointments/?role=admin')
    return render(request, 'dental/appointment_form.html', {
        'form': form, 'role': role, 'action': 'Редагувати'
    })


def appointment_delete(request, pk):
    """Видалення прийому з підтвердженням"""
    role = get_role(request)
    if role != 'admin':
        return redirect('appointments_list')
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appt.delete()
        messages.success(request, 'Прийом видалено!')
        return redirect(f'/appointments/?role=admin')
    return render(request, 'dental/confirm_delete.html', {
        'object': appt, 'role': role, 'type': 'Прийом'
    })
