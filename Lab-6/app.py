"""
app.py — Лабораторна робота №6
Flask + SQLAlchemy + WTForms + Jinja2 + сесії/куки + CRUD + зв'язки між таблицями

Новинки в порівнянні з лаб 5 (Django):
- Flask замість Django (більш мінімалістичний фреймворк)
- WTForms для форм (замість Django Forms)
- Сесії та куки для зберігання ролі
- Зв'язки: 1:1 (Patient-MedicalCard), 1:N (Doctor-Appointment), M:N (Doctor-Procedure)
"""

# Flask — основний клас веб-застосунку
# render_template — рендерить Jinja2 шаблон і повертає HTML
# redirect — перенаправляє на іншу сторінку
# url_for — генерує URL за назвою маршруту
# request — об'єкт поточного HTTP запиту (GET/POST дані, куки тощо)
# session — словник для зберігання даних між запитами (на стороні сервера)
# flash — додає одноразове повідомлення (зникає після перегляду)
# make_response — дозволяє вручну створити HTTP відповідь (потрібно для кук)
from flask import Flask, render_template, redirect, url_for, request, session, flash, make_response

# SQLAlchemy — ORM для Flask (аналог Django ORM)
from flask_sqlalchemy import SQLAlchemy

# FlaskForm — базовий клас для форм з CSRF захистом
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

# Типи полів форм WTForms
from wtforms import StringField, IntegerField, DateField, TextAreaField, SelectField, DateTimeLocalField

# Валідатори для полів форм
# DataRequired — поле обов'язкове
# Optional — поле необов'язкове
# Length — обмеження довжини рядка
# NumberRange — обмеження числового діапазону
from wtforms.validators import DataRequired, Optional, Length, NumberRange

from datetime import datetime

# Ініціалізація застосунку

# Створюємо Flask застосунок
# __name__ — ім'я поточного модуля, Flask використовує його для пошуку шаблонів
app = Flask(__name__)

# Конфігурація застосунку через словник config
app.config['SECRET_KEY'] = 'dental-flask-lab6-secret-2026'
# SECRET_KEY — секретний ключ для шифрування сесій та CSRF токенів

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dental.db'
# DATABASE_URI — рядок підключення до БД
# sqlite:///dental.db — файл dental.db у поточній папці

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# TRACK_MODIFICATIONS=False — вимикаємо відстеження змін об'єктів
# Це зменшує споживання пам'яті

app.config['WTF_CSRF_ENABLED'] = True
# CSRF_ENABLED=True — захист від CSRF атак у формах
# CSRF токен автоматично додається в кожну форму

# Ініціалізуємо SQLAlchemy і прив'язуємо до нашого застосунку
db = SQLAlchemy(app)

# CSRFProtect — реєструє csrf_token() як глобальну функцію Jinja2
# Без цього {{ csrf_token() }} в шаблонах не працює (TemplateError в адмін-режимі)
csrf = CSRFProtect(app)

# створення Моделей (таблиць БД)

class Doctor(db.Model):
    """Модель Лікар — таблиця 'doctors' в SQLite"""

    # __tablename__ — явно задаємо назву таблиці
    __tablename__ = 'doctors'

    # db.Column — колонка таблиці
    # db.Integer — ціле число, primary_key=True — головний ключ
    id = db.Column(db.Integer, primary_key=True)

    # db.String(100) — рядок до 100 символів, nullable=False — обов'язкове
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))        # nullable=True за замовчуванням
    experience = db.Column(db.Integer, default=0)  # default=0 — якщо не вказано

    # ЗВ'ЯЗОК 1:N (один лікар — багато прийомів)
    # db.relationship — визначає зв'язок на рівні Python (не колонка в БД)
    # back_populates='doctor' — зворотній зв'язок (з Appointment можна дістати doctor)
    # cascade='all, delete-orphan' — при видаленні лікаря видаляються його прийоми
    appointments = db.relationship('Appointment', back_populates='doctor', cascade='all, delete-orphan')

    def __repr__(self):
        # __repr__ — текстове представлення об'єкта (для відображення у формах)
        return f"{self.name} {self.surname}"


class Patient(db.Model):
    """Модель Пацієнт"""
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(250))

    # ЗВ'ЯЗОК 1:N (один пацієнт — багато прийомів)
    appointments = db.relationship('Appointment', back_populates='patient', cascade='all, delete-orphan')

    # ЗВ'ЯЗОК 1:1 (один пацієнт — одна медична карта)
    # uselist=False — вказує що це один об'єкт, а не список
    # cascade='all, delete-orphan' — медкарта пацієнта за потреби в розділі Адмін видаляється разом з пацієнтом
    medical_card = db.relationship('MedicalCard', back_populates='patient', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name} {self.surname}"


class MedicalCard(db.Model):
    """
    Медична карта пацієнта.
    ЗВ'ЯЗОК 1:1 з Patient — кожен пацієнт має рівно одну медкарту.
    """
    __tablename__ = 'medical_cards'
    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey — зовнішній ключ, посилається на id таблиці patients
    # unique=True — гарантує що один пацієнт має лише одну карту (зв'язок 1:1)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), unique=True, nullable=False)

    # Поля медичної карти
    allergies = db.Column(db.Text, default='')           # алергії
    chronic_diseases = db.Column(db.Text, default='')    # хронічні хвороби
    blood_type = db.Column(db.String(10), default='')    # група крові
    notes = db.Column(db.Text, default='')               # нотатки

    # Зворотній зв'язок з Patient
    patient = db.relationship('Patient', back_populates='medical_card')

    def __repr__(self):
        return f"Медкарта пацієнта id={self.patient_id}"


# Проміжна таблиця для зв'язку M:N (багато-до-багатьох)
# Лікар може виконувати багато процедур
# Процедуру може виконувати багато лікарів
# db.Table — створює таблицю без окремого класу
doctor_procedure = db.Table('doctor_procedure',
    # doctor_id — зовнішній ключ на таблицю doctors
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctors.id'), primary_key=True),
    # procedure_id — зовнішній ключ на таблицю procedures
    db.Column('procedure_id', db.Integer, db.ForeignKey('procedures.id'), primary_key=True)
)


class Procedure(db.Model):
    """
    Стоматологічна процедура.
    ЗВ'ЯЗОК M:N з Doctor — лікар може виконувати багато процедур.
    """
    __tablename__ = 'procedures'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # назва процедури
    price = db.Column(db.Float, default=0.0)           # ціна

    # secondary=doctor_procedure — вказуємо проміжну таблицю для M:N зв'язку
    # backref='procedures' — додає атрибут procedures до Doctor
    doctors = db.relationship('Doctor', secondary=doctor_procedure, backref='procedures')

    def __repr__(self):
        return self.name


class Appointment(db.Model):
    """Модель Прийом — зв'язує Patient і Doctor"""
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)

    # Зовнішні ключі для зв'язків з пацієнтом і лікарем
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)

    appointment_date = db.Column(db.String(50), nullable=False)  # дата прийому
    description = db.Column(db.Text, default='')  # опис скарг
    status = db.Column(db.String(20), default='заплановано')  # статус

    # Зв'язки для зручного доступу: appointment.patient, appointment.doctor
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')

    def __repr__(self):
        return f"Прийом #{self.id}"


# Форми за допомогою біблітеки (WTForms)

class DoctorForm(FlaskForm):
    """Форма для лікаря. FlaskForm автоматично додає CSRF захист."""

    # StringField — однорядкове текстове поле
    # validators=[...] — список валідаторів що перевіряють дані
    # DataRequired — поле не може бути порожнім
    # Length(min=2, max=100) — довжина від 2 до 100 символів
    name = StringField("Ім'я", validators=[DataRequired(message="Поле обов'язкове"), Length(min=2, max=100)])
    surname = StringField("Прізвище", validators=[DataRequired(), Length(min=2, max=100)])
    specialization = StringField("Спеціалізація", validators=[DataRequired()])

    # Optional() — поле необов'язкове (валідація пропускається якщо порожнє)
    phone = StringField("Телефон", validators=[Optional(), Length(max=20)])

    # IntegerField — числове поле
    # NumberRange(min=0, max=60) — значення від 0 до 60
    experience = IntegerField("Досвід (роки)", validators=[Optional(), NumberRange(min=0, max=60)])


class PatientForm(FlaskForm):
    """Форма для пацієнта"""
    name = StringField("Ім'я", validators=[DataRequired(), Length(min=2, max=100)])
    surname = StringField("Прізвище", validators=[DataRequired(), Length(min=2, max=100)])
    birth_date = StringField("Дата народження (РРРР-ММ-ДД)", validators=[Optional()])
    phone = StringField("Телефон", validators=[Optional(), Length(max=20)])
    address = StringField("Адреса", validators=[Optional(), Length(max=250)])


class MedicalCardForm(FlaskForm):
    """Форма для медичної карти"""
    blood_type = StringField("Група крові", validators=[Optional()])
    # TextAreaField — багаторядкове текстове поле (<textarea>)
    allergies = TextAreaField("Алергії", validators=[Optional()])
    chronic_diseases = TextAreaField("Хронічні захворювання", validators=[Optional()])
    notes = TextAreaField("Нотатки", validators=[Optional()])


class AppointmentForm(FlaskForm):
    """Форма для прийому"""

    # SelectField — випадаючий список
    # coerce=int — перетворює вибране значення в integer
    # choices заповнюються динамічно у view-функціях
    patient_id = SelectField("Пацієнт", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Лікар", coerce=int, validators=[DataRequired()])
    appointment_date = StringField("Дата та час", validators=[DataRequired()])
    description = TextAreaField("Опис / скарги", validators=[Optional()])

    # choices — список варіантів: (значення_в_БД, Відображення)
    status = SelectField("Статус", choices=[
        ('заплановано', 'Заплановано'),
        ('виконано', 'Виконано'),
        ('скасовано', 'Скасовано')
    ])


# Розділ допоміжних функцій за допомогою Flask

def get_role():
    """
    Визначає роль поточного користувача.
    Спочатку перевіряє сесію (серверна сторона),
    потім куки (клієнтська сторона).
    Якщо нічого немає — повертає 'user'.
    """
    # session — Flask сесія, зберігається на сервері
    # request.cookies — куки, зберігаються в браузері
    return session.get('role', request.cookies.get('role', 'user'))


def require_admin():
    """
    Перевіряє чи є поточний користувач адміністратором.
    Якщо ні — додає flash-повідомлення про помилку і повертає False.
    """
    if get_role() != 'admin':
        # flash(текст, категорія) — одноразове повідомлення
        # 'danger' — категорія для CSS класу (червоний колір)
        flash('Доступ заборонено. Потрібна роль адміністратора.', 'danger')
        return False
    return True


# Розділ Маршрутів (ROUTES)

@app.route('/')
def home():
    """Головна сторінка"""
    role = get_role()
    # render_template — шаблонізатор Jinja2 рендерить шаблон home.html
    # передаємо змінні які будуть доступні в шаблоні
    return render_template('home.html', role=role,
        doctors_count=Doctor.query.count(),       # кількість лікарів
        patients_count=Patient.query.count(),     # кількість пацієнтів
        appointments_count=Appointment.query.count())  # кількість прийомів


@app.route('/set-role/<role>')
def set_role(role):
    """
    Маршрут для зміни ролі.
    /set-role/admin — встановлює роль адміністратора
    /set-role/user  — встановлює роль користувача
    Роль зберігається одночасно в СЕСІЇ і КУКАХ.
    """
    # Перевіряємо що роль допустима
    if role not in ('admin', 'user'):
        role = 'user'

    # Зберігаємо в сесії (серверна сторона, більш безпечно)
    session['role'] = role

    # make_response — створюємо об'єкт відповіді щоб можна було додати куки
    # request.referrer — URL попередньої сторінки (звідки прийшов запит)
    resp = make_response(redirect(request.referrer or url_for('home')))

    # set_cookie — встановлюємо куку в браузері
    # 'role' — назва куки
    # role — значення куки
    # max_age=60*60*24*7 — час життя куки в секундах (7 днів)
    resp.set_cookie('role', role, max_age=60 * 60 * 24 * 7)

    return resp  # відповідь з кукою і редиректом


# Розділ Лікарі (Doctors)

@app.route('/doctors')
def doctors_list():
    """Список всіх лікарів"""
    # Doctor.query.all() — отримуємо всіх лікарів
    # SQL: SELECT * FROM doctors
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors, role=get_role())

# Додаємо в таблицю лікарів
@app.route('/doctors/add', methods=['GET', 'POST'])
def doctor_create():
    """
    Додавання лікаря.
    methods=['GET', 'POST'] — маршрут обробляє обидва типи запитів:
    GET — відкриття порожньої форми
    POST — відправка заповненої форми
    """
    if not require_admin():
        return redirect(url_for('doctors_list'))

    # Створюємо форму. Flask-WTF автоматично читає дані з request.form в методі (за методом) POST
    form = DoctorForm()

    # form.validate_on_submit() — True якщо:
    # 1. Запит POST (форма відправлена)
    # 2. Всі валідатори пройшли успішно перевірку
    if form.validate_on_submit():
        # Створюємо новий об'єкт лікаря з даних форми
        # form.name.data — дані конкретного поля форми
        db.session.add(Doctor(
            name=form.name.data,
            surname=form.surname.data,
            specialization=form.specialization.data,
            phone=form.phone.data,
            experience=form.experience.data or 0  # якщо порожньо — 0
        ))
        # db.session.commit() — зберігаємо зміни в БД
        # SQL: INSERT INTO doctors (name, ...) VALUES (...)
        db.session.commit()
        # 'success' — категорія (зелений колір)
        flash('Лікаря успішно додано!', 'success')
        return redirect(url_for('doctors_list'))

    # GET або невалідна форма — показуємо форму
    return render_template('doctor_form.html', form=form, action='Додати', role=get_role())


@app.route('/doctors/<int:pk>/edit', methods=['GET', 'POST'])
def doctor_update(pk):
    """Редагування лікаря. pk — id лікаря з URL."""
    if not require_admin():
        return redirect(url_for('doctors_list'))

    # get_or_404 — знаходить за pk або повертає помилку 404
    # SQL: SELECT * FROM doctors WHERE id = pk
    doctor = Doctor.query.get_or_404(pk)

    # obj=doctor — заповнює форму поточними даними лікаря
    form = DoctorForm(obj=doctor)

    if form.validate_on_submit():
        # populate_obj — переносить дані форми в об'єкт doctor
        # SQL: UPDATE doctors SET name=... WHERE id=pk
        form.populate_obj(doctor)
        db.session.commit()
        flash('Дані лікаря оновлено!', 'success')
        return redirect(url_for('doctors_list'))

    return render_template('doctor_form.html', form=form, action='Редагувати', role=get_role(), obj=doctor)


@app.route('/doctors/<int:pk>/delete', methods=['POST'])
def doctor_delete(pk):
    """
    Видалення лікаря. Тільки використовуємо метод POST — це захист від випадкового видалення.
    Кнопка видалення в шаблоні відправляє POST запит через форму.
    """
    if not require_admin():
        return redirect(url_for('doctors_list'))

    # db.session.delete — помічаємо об'єкт для видалення
    db.session.delete(Doctor.query.get_or_404(pk))
    # db.session.commit — виконуємо видалення
    # SQL: DELETE FROM doctors WHERE id = pk
    db.session.commit()
    flash('Лікаря видалено!', 'success')
    return redirect(url_for('doctors_list'))


# Розділ Пацієнти (patients)

@app.route('/patients')
def patients_list():
    """Список пацієнтів"""
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients, role=get_role())


# В цьому розділі добавляємо пацієнтів в таблицю (add patients)
@app.route('/patients/add', methods=['GET', 'POST'])
def patient_create():
    """Додавання пацієнта — автоматично створюється медкарта"""
    if not require_admin():
        return redirect(url_for('patients_list'))
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            name=form.name.data, surname=form.surname.data,
            birth_date=form.birth_date.data, phone=form.phone.data,
            address=form.address.data
        )
        db.session.add(patient)
        # flush() — відправляє INSERT в БД але НЕ комітить
        # Потрібно щоб отримати id нового пацієнта для медкарти
        db.session.flush()
        # Автоматично створюємо медкарту для нового пацієнта (зв'язок 1:1)
        db.session.add(MedicalCard(patient_id=patient.id))
        db.session.commit()
        flash('Пацієнта успішно додано!', 'success')
        return redirect(url_for('patients_list'))
    return render_template('patient_form.html', form=form, action='Додати', role=get_role())


@app.route('/patients/<int:pk>/edit', methods=['GET', 'POST'])
def patient_update(pk):
    """Редагування пацієнта"""
    if not require_admin():
        return redirect(url_for('patients_list'))
    patient = Patient.query.get_or_404(pk)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        form.populate_obj(patient)
        db.session.commit()
        flash('Дані пацієнта оновлено!', 'success')
        return redirect(url_for('patients_list'))
    return render_template('patient_form.html', form=form, action='Редагувати', role=get_role(), obj=patient)


@app.route('/patients/<int:pk>/delete', methods=['POST'])
def patient_delete(pk):
    """Видалення пацієнта (медкарта видаляється автоматично через cascade)"""
    if not require_admin():
        return redirect(url_for('patients_list'))
    db.session.delete(Patient.query.get_or_404(pk))
    db.session.commit()
    flash('Пацієнта видалено!', 'success')
    return redirect(url_for('patients_list'))


@app.route('/patients/<int:pk>/medical-card', methods=['GET', 'POST'])
def medical_card(pk):
    """Перегляд та редагування медичної карти пацієнта (зв'язок 1:1)"""
    patient = Patient.query.get_or_404(pk)

    # Якщо медкарти ще немає — створюємо автоматично
    if not patient.medical_card:
        mc = MedicalCard(patient_id=pk)
        db.session.add(mc)
        db.session.commit()

    form = MedicalCardForm(obj=patient.medical_card)

    # Редагування доступне тільки адміну
    if get_role() == 'admin' and form.validate_on_submit():
        form.populate_obj(patient.medical_card)
        db.session.commit()
        flash('Медичну карту оновлено!', 'success')
        return redirect(url_for('patients_list'))

    return render_template('medical_card.html', form=form, patient=patient, role=get_role())


# Розділ Прийоми пацієнтів

@app.route('/appointments')
def appointments_list():
    """Список прийомів"""
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments, role=get_role())


@app.route('/appointments/add', methods=['GET', 'POST'])
def appointment_create():
    """Додавання прийому"""
    if not require_admin():
        return redirect(url_for('appointments_list'))

    form = AppointmentForm()
    # Динамічно заповнюємо choices для SelectField
    # [(id, 'Ім'я Прізвище'), ...] — список кортежів (значення, відображення)
    form.patient_id.choices = [(p.id, f"{p.name} {p.surname}") for p in Patient.query.all()]
    form.doctor_id.choices = [(d.id, f"{d.name} {d.surname}") for d in Doctor.query.all()]

    if form.validate_on_submit():
        db.session.add(Appointment(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            description=form.description.data,
            status=form.status.data
        ))
        db.session.commit()
        flash('Прийом успішно додано!', 'success')
        return redirect(url_for('appointments_list'))

    return render_template('appointment_form.html', form=form, action='Додати', role=get_role())


@app.route('/appointments/<int:pk>/edit', methods=['GET', 'POST'])
def appointment_update(pk):
    """Редагування прийому"""
    if not require_admin():
        return redirect(url_for('appointments_list'))
    appt = Appointment.query.get_or_404(pk)
    form = AppointmentForm(obj=appt)
    form.patient_id.choices = [(p.id, f"{p.name} {p.surname}") for p in Patient.query.all()]
    form.doctor_id.choices = [(d.id, f"{d.name} {d.surname}") for d in Doctor.query.all()]
    if form.validate_on_submit():
        form.populate_obj(appt)
        db.session.commit()
        flash('Прийом оновлено!', 'success')
        return redirect(url_for('appointments_list'))
    return render_template('appointment_form.html', form=form, action='Редагувати', role=get_role())


@app.route('/appointments/<int:pk>/delete', methods=['POST'])
def appointment_delete(pk):
    """Видалення прийому"""
    if not require_admin():
        return redirect(url_for('appointments_list'))
    db.session.delete(Appointment.query.get_or_404(pk))
    db.session.commit()
    flash('Прийом видалено!', 'success')
    return redirect(url_for('appointments_list'))


# Розділ Початкові дані (SEED)

def seed_data():
    """Заповнення бази тестовими даними при першому запуску"""
    if Doctor.query.count() == 0:  # якщо БД порожня
        d1 = Doctor(name="Іван", surname="Петренко", specialization="Терапевт", phone="067-123-45-67", experience=10)
        d2 = Doctor(name="Олена", surname="Коваль", specialization="Хірург", phone="050-765-43-21", experience=15)
        db.session.add_all([d1, d2])  # add_all — додаємо список одразу

        p1 = Patient(name="Марія", surname="Іваненко", birth_date="1990-05-15", phone="093-111-22-33")
        p2 = Patient(name="Василь", surname="Сидоренко", birth_date="1985-08-20", phone="066-444-55-66")
        db.session.add_all([p1, p2])

        # flush — відправляємо в БД але не комітимо, щоб отримати id
        db.session.flush()

        # Створюємо медкарти для пацієнтів (зв'язок 1:1)
        db.session.add_all([
            MedicalCard(patient_id=p1.id, blood_type="II+"),
            MedicalCard(patient_id=p2.id, blood_type="I+")
        ])

        # Створюємо процедури та прив'язуємо до лікарів (зв'язок M:N)
        proc1 = Procedure(name="Видалення зубного каменю", price=500)
        proc2 = Procedure(name="Пломбування", price=1200)
        proc1.doctors = [d1, d2]  # обидва лікарі виконують процедуру 1
        proc2.doctors = [d1]       # тільки перший лікар виконує процедуру 2
        db.session.add_all([proc1, proc2])

        # Додаємо тестовий прийом
        db.session.add(Appointment(
            patient_id=p1.id, doctor_id=d1.id,
            appointment_date="2026-05-15 10:00",
            description="Болить зуб", status="заплановано"
        ))
        db.session.commit()  # зберігаємо все в БД одночасно


# В цьому розділі вже Запускаємо застосунок

# with app.app_context() — виконуємо код в контексті застосунку
# (потрібно щоб мати доступ до db і моделей)
with app.app_context():
    # Створюємо всі таблиці якщо їх ще немає
    # SQL: CREATE TABLE IF NOT EXISTS doctors (...)
    db.create_all()
    # Заповнюємо початковими даними
    seed_data()


# if __name__ == '__main__' — виконується тільки при прямому запуску файлу
# (не виконується якщо файл імпортується як модуль)
if __name__ == '__main__':
    # app.run — запускаємо вбудований сервер Flask
    # debug=True — автоматичне перезавантаження при змінах коду
    # port=5000 — порт на якому працює сервер
    app.run(debug=True, port=5000)
