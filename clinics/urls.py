from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.index, name='home'),
    path('directions/', views.directions, name='directions'),
    path('directions/', views.directions, name='drection_page'),
    path('directions/<str:slug>/', views.direction_detail, name='direction_detail'),
    path('doctors/', views.doctors, name='doctors'),
    path('doctors/', views.doctors, name='doctors_list'),
    path('services/', views.services, name='services'),
    path('services/', views.services, name='services_list'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('promotions/', views.promotions, name='promotions'),
    path('promotions/', views.promotions, name='promotions_page'),
    path('about/', views.about, name='about'),
    path('about/', views.about, name='about_the_clinic'),
    path('reviews/', views.reviews, name='reviews'),
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/', views.contacts, name='contact_page'),
    path('oms/', views.oms, name='oms'),
    path('oms/', views.oms, name='oms_page'),
    path('dms/', views.dms, name='dms'),
    path('dms/', views.dms, name='dms_page'),
    path('analyses/', views.analyses, name='analyses'),
    path('analyses/', views.analyses, name='analysis_page'),
    path('legal/', views.legal, name='legal'),
    path('appointment/', views.appointment_page, name='appointment-page'),
    path('forms/appointment/', views.appointment_request, name='appointment-request'),
    path('forms/callback/', views.callback_request, name='callback-request'),
    path('forms/callback/', views.callback_request, name='save_callback'),
]