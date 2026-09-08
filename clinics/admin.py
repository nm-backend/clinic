from django.contrib import admin
from .models import (
    Doctor,
    ServiceDirection,
    Appointment,
    OmsDirection,
    OmsApplication,
    CallbackRequest,
    Review,
)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty')
    search_fields = ('full_name', 'specialty')


@admin.register(ServiceDirection)
class ServiceDirectionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'phone', 'doctor',
        'appointment_date', 'appointment_time',
        'status', 'created_at',
    )
    list_filter = ('status', 'doctor', 'appointment_date')
    search_fields = ('full_name', 'phone', 'doctor__full_name')
    readonly_fields = ('created_at',)


@admin.register(OmsDirection)
class OmsDirectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')


@admin.register(OmsApplication)
class OmsApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at',)


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'doctor', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('full_name', 'doctor')
