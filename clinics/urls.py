from django.urls import path
from .views import (
    home_view,
    services_list,
    dms_page,
    direction_page,
    analysis_page,
    promotions_page,
    informations_page,
    about_the_clinic,
    reviews_page,
    contact_page,
)
from . import views

urlpatterns = [
    path("", home_view, name="home"),
    path('doctors/', views.doctors_page, name='doctors_list'),
    path('services/', services_list, name='services_list'),
    path('oms/', views.oms_page, name='oms_page'),
    path('dms/', dms_page, name='dms_page'),
    path('direction/', direction_page, name='drection_page'),
    path('analysis/', analysis_page, name='analysis_page'),
    path('promotions/', promotions_page, name='promotions_page'),
    path('informations/', informations_page, name='informations_page'),
    path('about/', about_the_clinic, name='about_the_clinic'),
    path('save-callback/', views.save_callback, name='save_callback'),
    path('reviews/', reviews_page, name='reviews'),
    path('contacts/', contact_page, name='contact_page'),
]
