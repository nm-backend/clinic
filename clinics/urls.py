from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('directions/', views.directions, name='directions'),
    path('directions/<str:slug>/', views.direction_detail, name='direction_detail'),
    path('doctors/', views.doctors, name='doctors'),
    path('services/', views.services, name='services'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('promotions/', views.promotions, name='promotions'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews, name='reviews'),
    path('contacts/', views.contacts, name='contacts'),
    path('oms/', views.oms, name='oms'),
    path('dms/', views.dms, name='dms'),
    path('analyses/', views.analyses, name='analyses'),
    path('legal/', views.legal, name='legal'),
    path('forms/appointment/', views.appointment_request, name='appointment-request'),
    path('forms/callback/', views.callback_request, name='callback-request'),
]