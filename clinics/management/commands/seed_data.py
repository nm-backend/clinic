from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from clinics.models import Appointment, Clinic, Doctor, Patient, Service


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для сети клиник'

    def handle(self, *args, **options):
        if Clinic.objects.exists():
            self.stdout.write(self.style.WARNING('Данные уже существуют, пропуск инициализации'))
            return

        clinic1 = Clinic.objects.create(
            name='Клиника «Здоровье+»',
            address='г. Москва, ул. Ленина, 10',
            phone='+7 (495) 111-22-33',
            email='info@zdorovie-plus.ru',
            description='Многопрофильная клиника в центре города',
        )
        clinic2 = Clinic.objects.create(
            name='Клиника «МедЛайн»',
            address='г. Москва, пр. Мира, 45',
            phone='+7 (495) 444-55-66',
            email='contact@medline.ru',
            description='Семейная клиника с широким спектром услуг',
        )

        doctors_data = [
            (clinic1, 'Иван', 'Петров', 'Терапевт'),
            (clinic1, 'Анна', 'Сидорова', 'Кардиолог'),
            (clinic1, 'Михаил', 'Козлов', 'Невролог'),
            (clinic2, 'Елена', 'Морозова', 'Терапевт'),
            (clinic2, 'Дмитрий', 'Волков', 'Хирург'),
            (clinic2, 'Ольга', 'Новикова', 'Педиатр'),
        ]
        doctors = []
        for clinic, first, last, specialty in doctors_data:
            doctors.append(Doctor.objects.create(
                clinic=clinic,
                first_name=first,
                last_name=last,
                specialty=specialty,
                phone=f'+7900{len(doctors):07d}',
            ))

        services_data = [
            (None, 'Первичный приём', 1500, 30),
            (None, 'Повторный приём', 1200, 20),
            (clinic1, 'ЭКГ', 2500, 30),
            (clinic1, 'УЗИ', 3500, 45),
            (clinic2, 'Хирургический осмотр', 2000, 30),
            (clinic2, 'Детский приём', 1800, 30),
        ]
        for clinic, name, price, duration in services_data:
            Service.objects.create(
                clinic=clinic,
                name=name,
                price=price,
                duration_minutes=duration,
                description=f'Услуга: {name}',
            )

        patient = Patient.objects.create(
            first_name='Алексей',
            last_name='Смирнов',
            phone='+79001234567',
            email='alexey@example.com',
        )

        Appointment.objects.create(
            patient=patient,
            doctor=doctors[0],
            service=Service.objects.get(name='Первичный приём'),
            scheduled_at=timezone.now() + timedelta(days=2, hours=10),
            status=Appointment.Status.CONFIRMED,
            notes='Тестовая запись',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Создано: {Clinic.objects.count()} клиник, '
            f'{Doctor.objects.count()} врачей, '
            f'{Service.objects.count()} услуг, '
            f'{Patient.objects.count()} пациентов, '
            f'{Appointment.objects.count()} записей',
        ))
