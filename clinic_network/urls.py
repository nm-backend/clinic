from django.contrib import admin
from django.shortcuts import redirect
from django.urls import converters, include, path, register_converter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from clinics.views import (
    about,
    analyses,
    appointment_request,
    callback_request,
    contacts,
    direction_detail,
    directions,
    dms,
    doctors,
    index,
    legal,
    oms,
    promotions,
    reviews,
    service_detail,
    services,
)


class UnicodeSlugConverter(converters.StringConverter):
    regex = r'[-a-zA-Z0-9_\u0400-\u04ff]+'


register_converter(UnicodeSlugConverter, 'uslug')


def redirect_to_v1_docs(request):
    return redirect('/api/v1/swagger/')


urlpatterns = [
    path('', index, name='index'),
    path('directions/', directions, name='directions'),
    path('directions/<uslug:slug>/', direction_detail, name='direction_detail'),
    path('doctors/', doctors, name='doctors'),
    path('services/', services, name='services'),
    path('services/<int:pk>/', service_detail, name='service_detail'),
    path('promotions/', promotions, name='promotions'),
    path('about/', about, name='about'),
    path('reviews/', reviews, name='reviews'),
    path('contacts/', contacts, name='contacts'),
    path('oms/', oms, name='oms'),
    path('dms/', dms, name='dms'),
    path('analyses/', analyses, name='analyses'),
    path('legal/', legal, name='legal'),
    path('forms/appointment/', appointment_request, name='appointment-request'),
    path('forms/callback/', callback_request, name='callback-request'),
    path('admin/', admin.site.urls),
    path('api/', include('clinics.urls')),
    path('api/v1/', include('clinics.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/swagger/', redirect_to_v1_docs),
    path('api/redoc/', redirect_to_v1_docs),
]
