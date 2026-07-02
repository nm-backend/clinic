from django.urls import path

from clinics import views

urlpatterns = [
    path('', views.index, name='index'),

    path('clinics/', views.ClinicListAPIView.as_view(), name='api-clinics'),
    path('doctors/', views.DoctorListAPIView.as_view(), name='api-doctors'),
    path('service-categories/', views.ServiceCategoryListAPIView.as_view(), name='api-service-categories'),
    path('services/', views.ServiceListAPIView.as_view(), name='api-services'),
    path('available-slots/', views.AvailableSlotsAPIView.as_view(), name='api-available-slots'),
    path('auth/register/', views.RegisterAPIView.as_view(), name='auth-register'),
    path('auth/me/', views.CurrentUserAPIView.as_view(), name='auth-me'),
    path('patients/me/appointments/', views.PatientAppointmentsAPIView.as_view(), name='patient-appointments'),
    path('appointments/', views.AppointmentListCreateAPIView.as_view(), name='api-appointments'),
    path('appointments/<int:pk>/', views.AppointmentRetrieveUpdateDestroyAPIView.as_view(), name='api-appointment-detail'),
]
