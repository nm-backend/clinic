from django.urls import path

from clinics import views

urlpatterns = [
    path('', views.index, name='index'),

    path('api/clinics/', views.ClinicListAPIView.as_view(), name='api-clinics'),
    path('api/doctors/', views.DoctorListAPIView.as_view(), name='api-doctors'),
    path('api/services/', views.ServiceListAPIView.as_view(), name='api-services'),
    path(
        'api/appointments/',
        views.AppointmentListCreateAPIView.as_view(),
        name='api-appointments',
    ),
    path(
        'api/appointments/<int:pk>/',
        views.AppointmentRetrieveUpdateDestroyAPIView.as_view(),
        name='api-appointment-detail',
    ),
]
