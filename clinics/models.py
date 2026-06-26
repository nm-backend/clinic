from django.core.validators import MinValueValidator
from django.db import models


class Clinic(models.Model):
    name = models.CharField('Название', max_length=255)
    address = models.CharField('Адрес', max_length=500)
    # Телефон храним строкой — в номере бывают +, скобки и пробелы
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name='Клиника',
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    specialty = models.CharField('Специальность', max_length=150)
    phone = models.CharField('Телефон', max_length=30, blank=True)
    bio = models.TextField('О враче', blank=True)
    # is_active=False — врач недоступен, но история записей остаётся
    is_active = models.BooleanField('Принимает пациентов', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.specialty})'

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'


class Patient(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    # Телефон — ключ для get_or_create при записи на приём
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'


class Service(models.Model):
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Клиника',
        null=True,
        blank=True,
        help_text='Пусто — услуга доступна во всей сети',
    )
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    # DecimalField, а не float — деньги без плавающей погрешности
    price = models.DecimalField(
        'Цена (₽)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    duration_minutes = models.PositiveIntegerField('Длительность (мин)', default=30)
    is_active = models.BooleanField('Доступна для записи', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Запланирован'
        CONFIRMED = 'confirmed', 'Подтверждён'
        CANCELLED = 'cancelled', 'Отменён'
        COMPLETED = 'completed', 'Завершён'

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пациент',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Врач',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='Услуга',
    )
    scheduled_at = models.DateTimeField('Дата и время приёма')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.patient} → {self.doctor} ({self.scheduled_at:%d.%m.%Y %H:%M})'
