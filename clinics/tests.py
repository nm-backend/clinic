from django.contrib.auth import get_user_model
from django.test import TestCase

from clinics.models import (
    CallbackRequest,
    Clinic,
    ClinicUser,
    Doctor,
    Equipment,
    Patient,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)


class SitePagesTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='Клиника 1',
            address='ул. Тестовая, 1',
            phone='+79990000001',
        )
        self.category = ServiceCategory.objects.create(name='Терапия', slug='therapy')
        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            category=self.category,
            first_name='Анна',
            last_name='Смирнова',
            specialty='Терапевт',
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

    def test_direction_detail_page(self):
        response = self.client.get(f'/directions/{self.category.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_service_detail_page(self):
        service = Service.objects.create(
            clinic=self.clinic,
            category=self.category,
            name='Первичный приём',
            price='2000.00',
            duration_minutes=30,
        )
        response = self.client.get(f'/services/{service.pk}/')
        self.assertEqual(response.status_code, 200)


class ApiEndpointTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='Клиника 1',
            address='ул. Тестовая, 1',
            phone='+79990000001',
        )
        self.category = ServiceCategory.objects.create(name='Терапия', slug='therapy')
        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            first_name='Иван',
            last_name='Петров',
            specialty='Терапевт',
        )

    def test_service_categories_endpoint(self):
        response = self.client.get('/api/v1/service-categories/')
        self.assertEqual(response.status_code, 200)

    def test_doctors_endpoint(self):
        response = self.client.get('/api/v1/doctors/')
        self.assertEqual(response.status_code, 200)

    def test_promotions_endpoint(self):
        Promotion.objects.create(title='Скидка', description='-20%')
        response = self.client.get('/api/v1/promotions/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_reviews_endpoint(self):
        Review.objects.create(
            patient_name='Анна',
            text='Хорошо',
            rating=5,
            doctor=self.doctor,
        )
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)

    def test_equipment_endpoint(self):
        Equipment.objects.create(name='МРТ')
        response = self.client.get('/api/v1/equipment/')
        self.assertEqual(response.status_code, 200)

    def test_review_serializer_contains_doctor_name(self):
        Review.objects.create(
            patient_name='Анна',
            text='Хорошо',
            rating=5,
            doctor=self.doctor,
        )
        response = self.client.get('/api/v1/reviews/')
        payload = response.json()
        self.assertEqual(payload[0]['doctor_name'], 'Петров Иван')

    def test_user_registration(self):
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


class FormTests(TestCase):
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

    def test_callback_request_invalid_data(self):
        response = self.client.post(
            '/forms/callback/',
            {'full_name': 'И', 'phone': '123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CallbackRequest.objects.exists())

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
