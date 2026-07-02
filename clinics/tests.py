from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from clinics.models import Appointment, Clinic, ClinicUser, Doctor, DoctorScheduleSlot, Patient, Service, ServiceCategory


class ClinicApiTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='Клиника 1',
            address='ул. Тестовая, 1',
            phone='+79990000001',
        )
        self.category = ServiceCategory.objects.create(
            name='Терапия',
            slug='therapy',
        )
        self.service = Service.objects.create(
            clinic=self.clinic,
            category=self.category,
            name='Первичный приём',
            price='2000.00',
            duration_minutes=30,
        )
        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            first_name='Анна',
            last_name='Смирнова',
            specialty='Терапевт',
        )
        self.patient = Patient.objects.create(
            first_name='Иван',
            last_name='Иванов',
            phone='+79990000002',
        )

    def test_service_categories_endpoint(self):
        response = self.client.get('/api/v1/service-categories/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(any(item['name'] == 'Терапия' for item in payload))

    def test_available_slots_exclude_booked_time(self):
        target_day = (timezone.now() + timedelta(days=1)).date()
        booked_at = datetime.combine(target_day, time(10, 0), tzinfo=timezone.get_current_timezone())
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            scheduled_at=booked_at,
            status=Appointment.Status.SCHEDULED,
        )

        response = self.client.get(
            '/api/v1/available-slots/',
            {'doctor_id': self.doctor.id, 'date': target_day.strftime('%Y-%m-%d')},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(any(slot['start'].startswith(target_day.strftime('%Y-%m-%dT10:')) for slot in payload))

    def test_user_registration_creates_profile(self):
        response = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'newpatient',
                'email': 'patient@example.com',
                'password': 'StrongPass123',
                'password_confirm': 'StrongPass123',
                'role': 'patient',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(get_user_model().objects.filter(username='newpatient').exists())
        self.assertTrue(ClinicUser.objects.filter(user__username='newpatient').exists())

    def test_doctors_and_services_can_be_filtered(self):
        second_clinic = Clinic.objects.create(name='Клиника 2', address='ул. Вторичная, 2', phone='+79990000003')
        second_doctor = Doctor.objects.create(
            clinic=second_clinic,
            first_name='Петр',
            last_name='Петров',
            specialty='Кардиолог',
        )
        Service.objects.create(
            clinic=second_clinic,
            category=self.category,
            name='УЗИ сердца',
            price='3500.00',
            duration_minutes=45,
        )

        doctors_response = self.client.get('/api/v1/doctors/', {'clinic_id': second_clinic.id})
        self.assertEqual(doctors_response.status_code, 200)
        self.assertTrue(any(item['id'] == second_doctor.id for item in doctors_response.json()))

        services_response = self.client.get('/api/v1/services/', {'category_id': self.category.id})
        self.assertEqual(services_response.status_code, 200)
        self.assertTrue(any(item['name'] == 'Первичный приём' for item in services_response.json()))

    def test_appointment_can_be_bound_to_slot(self):
        slot = DoctorScheduleSlot.objects.create(
            doctor=self.doctor,
            start_at=timezone.now() + timedelta(days=2, hours=1),
            end_at=timezone.now() + timedelta(days=2, hours=2),
            is_available=True,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            slot=slot,
            scheduled_at=slot.start_at,
            status=Appointment.Status.SCHEDULED,
        )
        self.assertEqual(appointment.slot, slot)
