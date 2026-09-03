from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views
from api import viewsets

router = DefaultRouter()
router.register('appointments', viewsets.AppointmentViewSet, basename='appointment')
router.register('callback-requests', viewsets.CallbackRequestViewSet, basename='callback-request')

urlpatterns = [
    path('', include(router.urls)),
    path('clinics/', views.ClinicListAPIView.as_view(), name='clinic-list'),
    path('doctors/', views.DoctorListAPIView.as_view(), name='doctor-list'),
    path('service-categories/', views.ServiceCategoryListAPIView.as_view(), name='service-category-list'),
    path('services/', views.ServiceListAPIView.as_view(), name='service-list'),
    path('available-slots/', views.AvailableSlotsAPIView.as_view(), name='available-slots'),
    path('patient-appointments/', views.PatientAppointmentsAPIView.as_view(), name='patient-appointments'),
    path('promotions/', views.PromotionListAPIView.as_view(), name='promotion-list'),
    path('reviews/', views.ReviewListAPIView.as_view(), name='review-list'),
    path('equipment/', views.EquipmentListAPIView.as_view(), name='equipment-list'),
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/me/', views.CurrentUserAPIView.as_view(), name='current-user'),
]