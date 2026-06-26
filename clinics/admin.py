from django.contrib import admin

from clinics.models import Appointment, Clinic, Doctor, Patient, Service


class DoctorInline(admin.TabularInline):
    model = Doctor
    extra = 0
    fields = ('last_name', 'first_name', 'specialty', 'phone', 'is_active')


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ('name', 'price', 'duration_minutes', 'is_active')


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    inlines = (DoctorInline, ServiceInline)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'specialty', 'clinic', 'is_active')
    list_filter = ('clinic', 'specialty', 'is_active')
    search_fields = ('last_name', 'first_name', 'specialty')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'email')
    search_fields = ('last_name', 'first_name', 'phone')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic', 'price', 'duration_minutes', 'is_active')
    list_filter = ('clinic', 'is_active')
    search_fields = ('name',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'service', 'scheduled_at', 'status')
    list_filter = ('status', 'doctor__clinic')
    search_fields = ('patient__last_name', 'patient__phone')
    raw_id_fields = ('patient', 'doctor', 'service')
