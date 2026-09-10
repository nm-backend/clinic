from django.test import TestCase, Client
from .models import Doctor, ServiceDirection, CallbackRequest, OmsApplication, Appointment, Review


class DoctorStrTest(TestCase):
    def test_str(self):
        d = Doctor.objects.create(full_name='Иванов И.И.', specialty='Терапевт', photo='test.png')
        self.assertEqual(str(d), 'Иванов И.И. (Терапевт)')


class ServiceDirectionStrTest(TestCase):
    def test_str(self):
        s = ServiceDirection.objects.create(title='Терапия', image='test.png')
        self.assertEqual(str(s), 'Терапия')


class CallbackStrTest(TestCase):
    def test_str(self):
        c = CallbackRequest.objects.create(name='Петров', phone=79990001112)
        self.assertIn('Петров', str(c))


class ReviewStrTest(TestCase):
    def test_str(self):
        r = Review.objects.create(full_name='Сидоров', age=40, doctor='Иванов', text='ok', rating=5, created_at='2024-01-01')
        self.assertEqual(str(r), 'Сидоров')


class PagesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_doctors(self):
        self.assertEqual(self.client.get('/doctors/').status_code, 200)

    def test_services(self):
        self.assertEqual(self.client.get('/services/').status_code, 200)

    def test_oms(self):
        self.assertEqual(self.client.get('/oms/').status_code, 200)

    def test_dms(self):
        self.assertEqual(self.client.get('/dms/').status_code, 200)

    def test_direction(self):
        self.assertEqual(self.client.get('/direction/').status_code, 200)

    def test_analysis(self):
        self.assertEqual(self.client.get('/analysis/').status_code, 200)

    def test_promotions(self):
        self.assertEqual(self.client.get('/promotions/').status_code, 200)

    def test_informations(self):
        self.assertEqual(self.client.get('/informations/').status_code, 200)

    def test_about(self):
        self.assertEqual(self.client.get('/about/').status_code, 200)

    def test_reviews(self):
        self.assertEqual(self.client.get('/reviews/').status_code, 200)

    def test_contacts(self):
        self.assertEqual(self.client.get('/contacts/').status_code, 200)

    def test_direction_detail(self):
        s = ServiceDirection.objects.create(title='Тест', image='test.png')
        self.assertEqual(self.client.get(f'/direction/{s.id}/').status_code, 200)

    def test_direction_detail_404(self):
        self.assertEqual(self.client.get('/direction/99999/').status_code, 404)


class FormsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_callback(self):
        r = self.client.post('/save-callback/', {'name': 'Тест', 'phone': '79990001112'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(CallbackRequest.objects.count(), 1)

    def test_oms(self):
        r = self.client.post('/oms/', {
            'name': 'ОМС', 'birthdate': '2000-01-01',
            'email': 't@t.com', 'phone': '79990001112', 'service': 'Терапия',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(OmsApplication.objects.count(), 1)

    def test_appointment(self):
        r = self.client.post('/services/', {'full_name': 'Петров', 'phone': '79990001112', 'direction': 'Терапия'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)


class APITest(TestCase):
    def test_doctors(self):
        self.assertEqual(self.client.get('/api/v1/doctors/').status_code, 200)

    def test_services(self):
        self.assertEqual(self.client.get('/api/v1/services/').status_code, 200)

    def test_reviews(self):
        self.assertEqual(self.client.get('/api/v1/reviews/').status_code, 200)

    def test_oms_directions(self):
        self.assertEqual(self.client.get('/api/v1/oms-directions/').status_code, 200)

    def test_callbacks(self):
        r = self.client.post('/api/v1/callbacks/', {'name': 'Тест', 'phone': 79990001112}, content_type='application/json')
        self.assertEqual(r.status_code, 201)

    def test_swagger(self):
        self.assertEqual(self.client.get('/api/v1/swagger/').status_code, 200)

    def test_schema(self):
        self.assertEqual(self.client.get('/api/v1/schema/').status_code, 200)
