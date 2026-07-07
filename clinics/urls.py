from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clinics', views.ClinicViewSet)
router.register(r'doctors', views.DoctorViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'appointments', views.AppointmentViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
]
