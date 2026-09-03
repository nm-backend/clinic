from django.contrib import admin
from django.shortcuts import redirect
from django.urls import converters, include, path, register_converter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


class UnicodeSlugConverter(converters.StringConverter):
    regex = r'[-a-zA-Z0-9_\u0400-\u04ff]+'


register_converter(UnicodeSlugConverter, 'uslug')


def redirect_to_v1_docs(request):
    return redirect('/api/v1/swagger/')


urlpatterns = [
    path('', include('clinics.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/swagger/', redirect_to_v1_docs),
    path('api/redoc/', redirect_to_v1_docs),
]