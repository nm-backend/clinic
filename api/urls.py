from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'oms-directions', views.OmsDirectionViewSet, basename='omsdirection')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('callbacks/', views.CallbackCreateView.as_view(), name='api_callbacks_create'),
    path('oms-applications/', views.OmsApplicationCreateView.as_view(), name='api_oms_create'),
    path('doctors/', views.DoctorListCreateView.as_view(), name='api_doctors_list_create'),
    path('services/', views.ServiceDirectionListCreateView.as_view(), name='api_services_list_create'),
    path('reviews/', views.ReviewListCreateView.as_view(), name='api_reviews_list_create'),
]
