from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='ФИО врача')
    specialty = models.CharField(max_length=150, verbose_name='Специализация')
    photo = models.ImageField(upload_to='doctors/', verbose_name='Фотография')
    appointment_url = models.URLField('Ссылка на запись', max_length=500, default='#', blank=True)

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def __str__(self):
        return f"{self.full_name} ({self.specialty})"


class ServiceDirection(models.Model):
    title = models.CharField('Название направления', max_length=150)
    image = models.ImageField('Изображение', upload_to='services/')
    link_url = models.URLField('Ссылка/URL', max_length=200, blank=True, default='#')

    class Meta:
        verbose_name = 'Направление работы'
        verbose_name_plural = 'Направления нашей работы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('done', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    full_name = models.CharField('ФИО', max_length=255)
    phone = models.CharField('Телефон', max_length=50)
    direction = models.CharField('Направление', max_length=150)
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        null=True,
        blank=True,
        verbose_name='Пациент',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name='Врач',
    )
    appointment_date = models.DateField('Дата приема', null=True, blank=True)
    appointment_time = models.TimeField('Время приема', null=True, blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
    )
    created_at = models.DateTimeField('Дата заявки', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на прием'
        verbose_name_plural = 'Заявки на прием'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.direction})"


class OmsDirection(models.Model):
    title = models.CharField(max_length=250, verbose_name='Название направления')
    description = models.CharField(verbose_name='Описание', max_length=500)
    link = models.URLField(max_length=500, default='#', verbose_name='Ссылка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        verbose_name = 'Направление ОМС'
        verbose_name_plural = 'Направления ОМС'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class OmsApplication(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')
    birthdate = models.DateField(max_length=50, verbose_name='Дата рождения')
    email = models.EmailField(verbose_name='E-mail')
    phone = models.IntegerField(max_length=50, verbose_name='Телефон')
    service = models.CharField(max_length=100, verbose_name='Услуга')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='Регион')
    doctor = models.CharField(max_length=255, blank=True, null=True, verbose_name='Врач')
    reason = models.CharField(max_length=255, blank=True, null=True, verbose_name='Причина обращения')
    source = models.CharField(max_length=100, blank=True, null=True, verbose_name='Источник')
    file = models.FileField(upload_to='oms_files/', blank=True, null=True, verbose_name='Документы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')

    class Meta:
        verbose_name = 'Заявка на ОМС'
        verbose_name_plural = 'Заявки на ОМС'

    def __str__(self):
        return f"Заявка от {self.name}"


class CallbackRequest(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')
    phone = models.IntegerField(max_length=20, verbose_name='Номер телефона')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')

    class Meta:
        verbose_name = 'Заявка на звонок'
        verbose_name_plural = 'Заявки на звонок'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.phone}"


class Review(models.Model):
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    doctor = models.CharField(max_length=150)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateField()

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name
