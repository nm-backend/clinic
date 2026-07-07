from django.contrib import admin
from .models import Clinic, Doctor, Service, Appointment

admin.site.register(Clinic)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Appointment)
