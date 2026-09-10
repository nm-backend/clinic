from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import api_views

router = DefaultRouter()
router.register(r'oms-directions', api_views.OmsDirectionViewSet, basename='omsdirection')
router.register(r'appointments', api_views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', api_views.RegisterView.as_view(), name='api_register'),
    path('callbacks/', api_views.CallbackCreateView.as_view(), name='api_callbacks_create'),
    path('oms-applications/', api_views.OmsApplicationCreateView.as_view(), name='api_oms_create'),
    path('doctors/', api_views.DoctorViewSet.as_view(), name='api_doctors_create'),
    path('services/', api_views.ServiceDirectionViewSet.as_view(), name='api_service_directions_create'),
    path('reviews/', api_views.ReviewViewSet.as_view(), name='api_reviews_create'),
]
