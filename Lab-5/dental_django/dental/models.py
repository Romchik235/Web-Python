"""
models.py — моделі бази даних для лабораторної роботи №5.
Модель = клас Python який описує таблицю в базі даних SQLite.
Django ORM автоматично перетворює ці класи в SQL таблиці.
"""

# models — модуль Django з усіма типами полів і базовим класом Model
from django.db import models


class Doctor(models.Model):
    """
    Модель Лікар — відповідає таблиці 'dental_doctor' в SQLite.
    Наслідує models.Model — завдяки цьому Django знає що це таблиця.
    """

    # CharField — поле для короткого тексту (VARCHAR в SQL)
    # max_length=100 — максимальна довжина рядка
    # verbose_name — людська назва поля (відображається в адмін-панелі та формах)
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    surname = models.CharField(max_length=100, verbose_name="Прізвище")
    specialization = models.CharField(max_length=150, verbose_name="Спеціалізація")

    # blank=True — поле необов'язкове у формах (можна залишити порожнім)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    # IntegerField — ціле число
    # default=0 — значення за замовчуванням якщо не вказано
    experience = models.IntegerField(default=0, verbose_name="Досвід (роки)")

    def __str__(self):
        # __str__ — що повертати при перетворенні об'єкта в рядок
        # Використовується в select-полях форм та адмін-панелі
        return f"{self.name} {self.surname} ({self.specialization})"

    class Meta:
        """Meta — додаткові налаштування моделі"""
        verbose_name = "Лікар"          # назва в однині
        verbose_name_plural = "Лікарі"  # назва в множині


class Patient(models.Model):
    """Модель Пацієнт"""

    name = models.CharField(max_length=100, verbose_name="Ім'я")
    surname = models.CharField(max_length=100, verbose_name="Прізвище")

    # DateField — поле дати (DATE в SQL)
    # null=True — дозволяє NULL в базі даних
    # blank=True — дозволяє порожнє значення у формі
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")

    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.CharField(max_length=250, blank=True, verbose_name="Адреса")

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        verbose_name = "Пацієнт"
        verbose_name_plural = "Пацієнти"


class Appointment(models.Model):
    """Модель Прийом — містить зв'язки з Лікарем і Пацієнтом"""

    # STATUS_CHOICES — список варіантів для поля status
    # Кожен елемент: ('значення_в_БД', 'Відображення для користувача')
    STATUS_CHOICES = [
        ('planned', 'Заплановано'),
        ('done', 'Виконано'),
        ('cancelled', 'Скасовано'),
    ]

    # ForeignKey — зовнішній ключ, зв'язок багато-до-одного
    # Patient — на яку модель посилаємось
    # on_delete=models.CASCADE — якщо пацієнта видалено, видалити і його прийоми
    # related_name='appointments' — ім'я для зворотнього зв'язку
    #   (дозволяє звертатись: patient.appointments.all())
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Пацієнт"
    )

    # Аналогічний зв'язок з лікарем
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Лікар"
    )

    # DateTimeField — поле дати та часу (DATETIME в SQL)
    appointment_date = models.DateTimeField(verbose_name="Дата та час прийому")

    # TextField — довгий текст (TEXT в SQL), необов'язкове
    description = models.TextField(blank=True, verbose_name="Опис / скарги")

    # choices=STATUS_CHOICES — обмежуємо значення переліком STATUS_CHOICES
    # default='planned' — нові прийоми за замовчуванням мають статус "заплановано"
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name="Статус"
    )

    def __str__(self):
        return f"Прийом {self.patient} у {self.doctor} — {self.appointment_date}"

    class Meta:
        verbose_name = "Прийом"
        verbose_name_plural = "Прийоми"
        # ordering — сортування за замовчуванням при запитах
        # '-appointment_date' — мінус означає сортування за спаданням (нові спочатку)
        ordering = ['-appointment_date']
