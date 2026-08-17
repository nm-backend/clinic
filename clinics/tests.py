from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from clinics.models import (
    Appointment,
    CallbackRequest,
    Clinic,
    ClinicUser,
    Doctor,
    DoctorScheduleSlot,
    Equipment,
    Patient,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)


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


class SitePagesTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='Клиника 1',
            address='ул. Тестовая, 1',
            phone='+79990000001',
        )
        self.category = ServiceCategory.objects.create(
            name='Гинекология',
            slug='ginekologiya',
        )
        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            category=self.category,
            first_name='Анна',
            last_name='Смирнова',
            specialty='Гинеколог',
        )
        self.service = Service.objects.create(
            clinic=self.clinic,
            category=self.category,
            name='Первичный приём',
            price='2000.00',
            duration_minutes=30,
        )

    def test_all_site_pages_render(self):
        for url in [
            '/',
            '/directions/',
            '/doctors/',
            '/services/',
            '/promotions/',
            '/about/',
            '/reviews/',
            '/contacts/',
            '/oms/',
            '/dms/',
            '/analyses/',
            '/legal/',
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_unicode_slug_direction_detail(self):
        cyrillic_category = ServiceCategory.objects.create(name='Отоларингология')
        response = self.client.get(f'/directions/{cyrillic_category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Отоларингология')

    def test_direction_detail_shows_services_and_reviews(self):
        Review.objects.create(
            patient_name='Анна Петрова',
            text='Отличный специалист',
            rating=5,
            doctor=self.doctor,
        )
        response = self.client.get(f'/directions/{self.category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Когда нужно обратиться')
        self.assertContains(response, 'Первичный приём')
        self.assertContains(response, 'Анна Петрова')

    def test_services_page_groups_by_category(self):
        response = self.client.get('/services/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Гинекология')
        self.assertContains(response, 'Первичный приём')

    def test_service_detail_page(self):
        response = self.client.get(f'/services/{self.service.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Первичный приём')

    def test_doctors_filter_by_category(self):
        response = self.client.get('/doctors/', {'category': self.category.slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Смирнова')


class ContentApiTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='Клиника 1',
            address='ул. Тестовая, 1',
            phone='+79990000001',
        )
        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            first_name='Иван',
            last_name='Петров',
            specialty='Терапевт',
        )

    def test_promotions_reviews_equipment_endpoints(self):
        Promotion.objects.create(title='Скидка', description='-20%')
        Review.objects.create(
            patient_name='Анна Петрова',
            text='Хорошая клиника',
            rating=5,
            doctor=self.doctor,
        )
        Equipment.objects.create(name='МРТ')

        for url in ['/api/v1/promotions/', '/api/v1/reviews/', '/api/v1/equipment/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(len(response.json()) > 0)

    def test_review_serializer_contains_doctor_name(self):
        Review.objects.create(
            patient_name='Анна Петрова',
            text='Хорошая клиника',
            rating=5,
            doctor=self.doctor,
        )
        response = self.client.get('/api/v1/reviews/')
        payload = response.json()
        self.assertEqual(payload[0]['doctor_name'], 'Петров Иван')

    def test_index_renders_new_blocks(self):
        Promotion.objects.create(title='Скидка -20%', description='на МРТ')
        Review.objects.create(
            patient_name='Анна Петрова',
            text='Отличный врач',
            rating=5,
            doctor=self.doctor,
        )
        Equipment.objects.create(name='Компьютерный томограф')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Скидка -20%')
        self.assertContains(response, 'Компьютерный томограф')
        self.assertContains(response, 'Анна Петрова')

    def test_callback_request_creates_record(self):
        response = self.client.post(
            '/forms/callback/',
            {'full_name': 'Иван Иванов', 'phone': '+7 900 123-45-67'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CallbackRequest.objects.filter(
            full_name='Иван Иванов',
            request_type=CallbackRequest.Type.CALLBACK,
        ).exists())

    def test_callback_request_invalid_data(self):
        response = self.client.post(
            '/forms/callback/',
            {'full_name': 'И', 'phone': '123'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CallbackRequest.objects.exists())

    def test_appointment_request_creates_record(self):
        response = self.client.post(
            '/forms/appointment/',
            {'full_name': 'Иван Иванов', 'phone': '+7 900 123-45-67'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CallbackRequest.objects.filter(
            full_name='Иван Иванов',
            request_type=CallbackRequest.Type.APPOINTMENT,
        ).exists())

    def test_callback_requests_api_staff_only(self):
        CallbackRequest.objects.create(
            full_name='Иван Иванов',
            phone='+79001234567',
        )
        self.assertEqual(self.client.get('/api/v1/callback-requests/').json(), [])

        user = get_user_model().objects.create_superuser(
            username='admin', password='AdminPass123', email='admin@example.com',
        )
        self.client.force_login(user)
        response = self.client.get('/api/v1/callback-requests/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
