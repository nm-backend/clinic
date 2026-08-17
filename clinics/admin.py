from django.contrib import admin

from clinics.models import (
    Appointment,
    CallbackRequest,
    Clinic,
    ClinicUser,
    Doctor,
    DoctorScheduleSlot,
    Equipment,
    Patient,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)


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
    list_display = ('name', 'city', 'address', 'phone', 'is_active')
    list_filter = ('is_active', 'is_branch')
    search_fields = ('name', 'city', 'address')
    prepopulated_fields = {'slug': ('name',)}
    inlines = (DoctorInline, ServiceInline)


@admin.register(ClinicUser)
class ClinicUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'clinic')
    list_filter = ('role', 'clinic')
    search_fields = ('user__username', 'user__email', 'clinic__name')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'specialty', 'category', 'clinic', 'is_active')
    list_filter = ('clinic', 'category', 'specialty', 'is_active')
    search_fields = ('last_name', 'first_name', 'specialty', 'qualification')
    raw_id_fields = ('clinic', 'category')


@admin.register(DoctorScheduleSlot)
class DoctorScheduleSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'start_at', 'end_at', 'is_available')
    list_filter = ('is_available', 'doctor__clinic')
    search_fields = ('doctor__last_name', 'doctor__first_name')
    date_hierarchy = 'start_at'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'email')
    search_fields = ('last_name', 'first_name', 'phone', 'email')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'clinic', 'price', 'duration_minutes', 'is_active')
    list_filter = ('clinic', 'category', 'is_active')
    search_fields = ('name', 'description')
    raw_id_fields = ('clinic', 'category')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'valid_until', 'color', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'rating', 'created_at', 'is_active')
    list_filter = ('is_active', 'rating')
    search_fields = ('patient_name', 'text', 'doctor__last_name')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'request_type', 'is_processed', 'created_at')
    list_filter = ('request_type', 'is_processed')
    search_fields = ('full_name', 'phone')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'service', 'slot', 'scheduled_at', 'status')
    list_filter = ('status', 'doctor__clinic', 'service__category')
    search_fields = ('patient__last_name', 'patient__first_name', 'patient__phone', 'doctor__last_name', 'doctor__first_name')
    raw_id_fields = ('patient', 'doctor', 'service', 'slot')
    date_hierarchy = 'scheduled_at'
