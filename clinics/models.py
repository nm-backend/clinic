from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Clinic(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг', unique=True, blank=True, null=True)
    city = models.CharField('Город', max_length=120, blank=True)
    address = models.CharField('Адрес', max_length=500)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    description = models.TextField('Описание', blank=True)
    working_hours = models.CharField('Часы работы', max_length=120, blank=True)
    is_branch = models.BooleanField('Филиал', default=False)
    parent_clinic = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='branches',
        null=True,
        blank=True,
        verbose_name='Главная клиника',
    )
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClinicUser(models.Model):
    class Role(models.TextChoices):
        PATIENT = 'patient', 'Пациент'
        DOCTOR = 'doctor', 'Врач'
        ADMIN = 'admin', 'Администратор'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinic_user',
        verbose_name='Пользователь',
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Клиника',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь клиники'
        verbose_name_plural = 'Пользователи клиники'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} ({self.get_role_display()})'


class Doctor(models.Model):
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name='Клиника',
    )
    category = models.ForeignKey(
        'ServiceCategory',
        on_delete=models.SET_NULL,
        related_name='doctors',
        null=True,
        blank=True,
        verbose_name='Направление',
    )
    clinic_user = models.OneToOneField(
        ClinicUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_profile',
        verbose_name='Профиль пользователя',
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    specialty = models.CharField('Специальность', max_length=150)
    phone = models.CharField('Телефон', max_length=30, blank=True)
    bio = models.TextField('О враче', blank=True)
    qualification = models.CharField('Квалификация', max_length=200, blank=True)
    experience_years = models.PositiveIntegerField('Стаж лет', default=0)
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


class DoctorScheduleSlot(models.Model):
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='schedule_slots',
        verbose_name='Врач',
    )
    start_at = models.DateTimeField('Начало')
    end_at = models.DateTimeField('Окончание')
    is_available = models.BooleanField('Свободно', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Слот расписания'
        verbose_name_plural = 'Слоты расписания'
        ordering = ['start_at']

    def __str__(self):
        return f'{self.doctor} — {self.start_at:%d.%m.%Y %H:%M}'


class Patient(models.Model):
    clinic_user = models.OneToOneField(
        ClinicUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_profile',
        verbose_name='Профиль пользователя',
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
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


class ServiceCategory(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)
    slug = models.SlugField('Слаг', unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        related_name='services',
        verbose_name='Направление',
        null=True,
        blank=True,
    )
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
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
    slot = models.ForeignKey(
        DoctorScheduleSlot,
        on_delete=models.SET_NULL,
        related_name='appointments',
        verbose_name='Слот расписания',
        null=True,
        blank=True,
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
