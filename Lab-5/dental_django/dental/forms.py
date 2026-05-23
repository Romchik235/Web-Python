"""
forms.py — форми Django для введення та валідації даних.
ModelForm — спеціальний тип форми що автоматично генерує поля
на основі моделі. Підключає валідацію і збереження в БД.
"""

# forms — модуль Django з усіма типами форм і полів
from django import forms

# Імпортуємо наші моделі — форми будуть прив'язані до них
from .models import Doctor, Patient, Appointment


class DoctorForm(forms.ModelForm):
    """
    Форма для створення та редагування лікаря.
    ModelForm автоматично створює поля на основі моделі Doctor.
    """

    class Meta:
        """Meta — налаштування форми"""

        # model — до якої моделі прив'язана форма
        model = Doctor

        # fields — які поля моделі включити у форму
        # id не включаємо — він генерується автоматично
        fields = ['name', 'surname', 'specialization', 'phone', 'experience']

        # widgets — налаштування HTML елементів для кожного поля
        widgets = {
            # TextInput — однорядкове текстове поле <input type="text">
            # attrs — HTML атрибути: class для CSS, placeholder для підказки
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Введіть ім'я"}),
            'surname': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введіть прізвище'}),
            'specialization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Спеціалізація'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '0XX-XXX-XX-XX'}),
            # NumberInput — числове поле <input type="number">
            # min: 0 — мінімальне значення в HTML
            'experience': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }

    def clean_experience(self):
        """
        Кастомна валідація поля experience.
        Методи clean_<назва_поля> викликаються автоматично при валідації форми.
        """
        # cleaned_data — словник з вже очищеними (провалідованими) даними
        exp = self.cleaned_data.get('experience')

        # Перевіряємо що досвід не від'ємний
        if exp is not None and exp < 0:
            # ValidationError — помилка валідації, форма не збережеться
            # повідомлення про помилку відображається під полем
            raise forms.ValidationError("Досвід не може бути від'ємним числом.")

        # Повертаємо валідне значення
        return exp


class PatientForm(forms.ModelForm):
    """Форма для створення та редагування пацієнта"""

    class Meta:
        model = Patient
        fields = ['name', 'surname', 'birth_date', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'surname': forms.TextInput(attrs={'class': 'form-input'}),
            # DateInput — поле дати <input type="date">
            # type='date' — браузер показує календар для вибору дати
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
        }


class AppointmentForm(forms.ModelForm):
    """Форма для створення та редагування прийому"""

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'description', 'status']
        widgets = {
            # Select — випадаючий список <select>
            # Django автоматично заповнює його даними з пов'язаної таблиці
            'patient': forms.Select(attrs={'class': 'form-input'}),
            'doctor': forms.Select(attrs={'class': 'form-input'}),

            # DateTimeInput — поле дати та часу
            # type='datetime-local' — браузер показує зручний вибір дати+часу
            'appointment_date': forms.DateTimeInput(
                attrs={'class': 'form-input', 'type': 'datetime-local'}
            ),

            # Textarea — багаторядкове текстове поле <textarea>
            # rows=3 — висота 3 рядки
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),

            # Select для статусу — варіанти беруться з STATUS_CHOICES моделі
            'status': forms.Select(attrs={'class': 'form-input'}),
        }
