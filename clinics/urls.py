from django.urls import path

from clinics.views import (
    AppointmentListCreateAPIView,
    AppointmentRetrieveUpdateDestroyAPIView,
    AvailableSlotsAPIView,
    CallbackRequestListCreateAPIView,
    ClinicListAPIView,
    CurrentUserAPIView,
    DoctorListAPIView,
    EquipmentListAPIView,
    PatientAppointmentsAPIView,
    PromotionListAPIView,
    RegisterAPIView,
    ReviewListAPIView,
    ServiceCategoryListAPIView,
    ServiceListAPIView,
)

urlpatterns = [
    path('clinics/', ClinicListAPIView.as_view(), name='clinic-list'),
    path('doctors/', DoctorListAPIView.as_view(), name='doctor-list'),
    path('categories/', ServiceCategoryListAPIView.as_view(), name='category-list'),
    path('services/', ServiceListAPIView.as_view(), name='service-list'),
    path('slots/', AvailableSlotsAPIView.as_view(), name='available-slots'),
    path('appointments/', AppointmentListCreateAPIView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentRetrieveUpdateDestroyAPIView.as_view(), name='appointment-detail'),
    path('appointments/patient/', PatientAppointmentsAPIView.as_view(), name='patient-appointments'),
    path('promotions/', PromotionListAPIView.as_view(), name='promotion-list'),
    path('reviews/', ReviewListAPIView.as_view(), name='review-list'),
    path('equipment/', EquipmentListAPIView.as_view(), name='equipment-list'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('callbacks/', CallbackRequestListCreateAPIView.as_view(), name='callback-list-create'),
]