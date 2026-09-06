from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

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


def check_slot_available(doctor, service, scheduled_at, exclude_id=None, slot=None):
    end_time = scheduled_at + timezone.timedelta(minutes=service.duration_minutes)
    busy = Appointment.objects.filter(
        doctor=doctor,
        status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
        scheduled_at__lt=end_time,
    )
    if exclude_id:
        busy = busy.exclude(pk=exclude_id)
    if slot is not None:
        busy = busy.filter(slot__in=[slot, None])

    for existing in busy:
        existing_end = existing.scheduled_at + timezone.timedelta(
            minutes=existing.service.duration_minutes,
        )
        if existing.scheduled_at < end_time and existing_end > scheduled_at:
            raise serializers.ValidationError(
                'У врача уже есть запись на это время',
            )


class ClinicModelSerializer(ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'


class DoctorModelSerializer(ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'


class ServiceCategoryModelSerializer(ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServiceModelSerializer(ModelSerializer):
    clinic_name = serializers.CharField(
        source='clinic.name',
        read_only=True,
        default='Доступна во всей сети',
    )
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = '__all__'


class PromotionModelSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'


class ReviewModelSerializer(ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


class EquipmentModelSerializer(ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class CallbackRequestModelSerializer(ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ('id', 'request_type', 'full_name', 'phone', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_full_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Укажите имя')
        return value.strip()

    def validate_phone(self, value):
        digits = ''.join(ch for ch in value if ch.isdigit())
        if len(digits) < 10:
            raise serializers.ValidationError('Укажите корректный номер телефона')
        return value.strip()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=ClinicUser.Role.choices, default=ClinicUser.Role.PATIENT)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        if get_user_model().objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Пользователь уже существует'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        role = validated_data.pop('role')
        user = get_user_model().objects.create_user(**validated_data, password=password)
        ClinicUser.objects.create(user=user, role=role)
        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ClinicUser
        fields = ('username', 'email', 'role', 'clinic')


class AppointmentSerializer(ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    clinic_name = serializers.CharField(source='doctor.clinic.name', read_only=True)

    patient_first_name = serializers.CharField(max_length=100, write_only=True, required=False)
    patient_last_name = serializers.CharField(max_length=100, write_only=True, required=False)
    patient_phone = serializers.CharField(max_length=30, write_only=True, required=False)
    patient_email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    patient_birth_date = serializers.DateField(required=False, allow_null=True, write_only=True)
    doctor_id = serializers.IntegerField(min_value=1, write_only=True, required=False)
    service_id = serializers.IntegerField(min_value=1, write_only=True, required=False)
    slot_id = serializers.IntegerField(min_value=1, required=False, allow_null=True, write_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'service', 'slot', 'scheduled_at',
            'status', 'notes', 'created_at', 'updated_at',
            'patient_name', 'doctor_name', 'service_name', 'clinic_name',
            'patient_first_name', 'patient_last_name', 'patient_phone',
            'patient_email', 'patient_birth_date', 'doctor_id', 'service_id', 'slot_id',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'patient', 'doctor', 'service']

    def validate_scheduled_at(self, value):
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError('Дата приёма должна быть в будущем')
        return value

    def validate_status(self, value):
        if value == Appointment.Status.COMPLETED:
            raise serializers.ValidationError('Статус "completed" устанавливается только администратором')
        return value

    def validate(self, data):
        doctor_id = data.get('doctor_id')
        service_id = data.get('service_id')
        slot_id = data.get('slot_id')
        scheduled_at = data.get('scheduled_at')

        if self.instance is None:
            if not doctor_id:
                raise serializers.ValidationError({'doctor_id': 'Обязательное поле'})
            if not service_id:
                raise serializers.ValidationError({'service_id': 'Обязательное поле'})
            if not slot_id and not scheduled_at:
                raise serializers.ValidationError({'scheduled_at': 'Обязательное поле'})

        doctor = Doctor.objects.select_related('clinic').get(pk=doctor_id) if doctor_id else (self.instance.doctor if self.instance else None)
        service = Service.objects.get(pk=service_id) if service_id else (self.instance.service if self.instance else None)

        if doctor and not doctor.is_active:
            raise serializers.ValidationError({'doctor_id': 'Врач не принимает пациентов'})
        if doctor and not doctor.clinic.is_active:
            raise serializers.ValidationError({'doctor_id': 'Клиника врача неактивна'})
        if service and not service.is_active:
            raise serializers.ValidationError({'service_id': 'Услуга недоступна'})

        slot = None
        if slot_id:
            slot = DoctorScheduleSlot.objects.filter(
                pk=slot_id, doctor=doctor, is_available=True
            ).first()
            if not slot:
                raise serializers.ValidationError({'slot_id': 'Слот не найден или уже занят'})
            if slot.start_at <= timezone.now():
                raise serializers.ValidationError({'slot_id': 'Слот уже неактуален'})
            data['scheduled_at'] = slot.start_at

        check_at = data.get('scheduled_at', self.instance.scheduled_at if self.instance else None)
        if doctor and service and check_at:
            end_time = check_at + timezone.timedelta(minutes=service.duration_minutes)
            busy = Appointment.objects.filter(
                doctor=doctor,
                status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
                scheduled_at__lt=end_time,
            )
            if self.instance:
                busy = busy.exclude(pk=self.instance.pk)
            if slot is not None:
                busy = busy.filter(slot__in=[slot, None])
            for existing in busy:
                existing_end = existing.scheduled_at + timezone.timedelta(minutes=existing.service.duration_minutes)
                if existing.scheduled_at < end_time and existing_end > check_at:
                    raise serializers.ValidationError('У врача уже есть запись на это время')

        data['doctor'] = doctor
        data['service'] = service
        data['slot'] = slot
        return data

    def create(self, validated_data):
        patient_first_name = validated_data.pop('patient_first_name', '')
        patient_last_name = validated_data.pop('patient_last_name', '')
        patient_phone = validated_data.pop('patient_phone', '')
        patient_email = validated_data.pop('patient_email', '')
        patient_birth_date = validated_data.pop('patient_birth_date', None)
        doctor = validated_data.pop('doctor')
        service = validated_data.pop('service')
        slot = validated_data.pop('slot', None)
        scheduled_at = validated_data.pop('scheduled_at')

        patient, _ = Patient.objects.update_or_create(
            phone=patient_phone,
            defaults={
                'first_name': patient_first_name,
                'last_name': patient_last_name,
                'email': patient_email,
                'birth_date': patient_birth_date,
            },
        )

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            service=service,
            slot=slot,
            scheduled_at=scheduled_at,
            notes=validated_data.pop('notes', ''),
            status=Appointment.Status.SCHEDULED,
        )
        if slot is not None:
            slot.is_available = False
            slot.save(update_fields=['is_available'])
        return appointment

    def update(self, instance, validated_data):
        for field in ('doctor', 'service', 'slot', 'scheduled_at', 'status', 'notes'):
            if field in validated_data:
                setattr(instance, field, validated_data.pop(field))
        instance.save()
        return instance
