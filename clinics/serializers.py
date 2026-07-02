from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from clinics.models import (
    Appointment,
    Clinic,
    ClinicUser,
    Doctor,
    DoctorScheduleSlot,
    Patient,
    Service,
    ServiceCategory,
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


class DoctorDetailSerializer(ModelSerializer):
    clinic = ClinicModelSerializer(read_only=True)

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


class PatientModelSerializer(ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


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


class AppointmentModelSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentDetailSerializer(ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    clinic_name = serializers.CharField(source='doctor.clinic.name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentCreateSerializer(serializers.Serializer):
    patient_first_name = serializers.CharField(max_length=100)
    patient_last_name = serializers.CharField(max_length=100)
    patient_phone = serializers.CharField(max_length=30)
    patient_email = serializers.EmailField(required=False, allow_blank=True)
    patient_birth_date = serializers.DateField(required=False, allow_null=True)
    doctor_id = serializers.IntegerField(min_value=1)
    service_id = serializers.IntegerField(min_value=1)
    slot_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_scheduled_at(self, value):
        if value is None:
            return value
        if value <= timezone.now():
            raise serializers.ValidationError('Дата приёма должна быть в будущем')
        return value

    def validate_doctor_id(self, value):
        if not Doctor.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError(
                'Врач не найден или не принимает пациентов',
            )
        return value

    def validate_service_id(self, value):
        if not Service.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError('Услуга не найдена')
        return value

    def validate(self, data):
        doctor = Doctor.objects.select_related('clinic').get(pk=data['doctor_id'])

        if not doctor.clinic.is_active:
            raise serializers.ValidationError('Клиника врача неактивна')

        service = Service.objects.get(pk=data['service_id'])
        if service.clinic_id and service.clinic_id != doctor.clinic_id:
            raise serializers.ValidationError(
                'Услуга недоступна в клинике выбранного врача',
            )

        slot = None
        if data.get('slot_id'):
            slot = DoctorScheduleSlot.objects.filter(
                pk=data['slot_id'],
                doctor=doctor,
                is_available=True,
            ).first()
            if slot is None:
                raise serializers.ValidationError({'slot_id': 'Слот не найден или уже занят'})
            if slot.start_at <= timezone.now():
                raise serializers.ValidationError({'slot_id': 'Слот уже неактуален'})
            data['scheduled_at'] = slot.start_at
        else:
            if data.get('scheduled_at') is None:
                raise serializers.ValidationError({'scheduled_at': 'Обязательное поле'})
            self._check_slot_available(doctor, service, data['scheduled_at'])

        if slot is not None:
            self._check_slot_available(doctor, service, slot.start_at, slot=slot)

        data['doctor'] = doctor
        data['service'] = service
        data['slot'] = slot
        return data

    def _check_slot_available(self, doctor, service, scheduled_at, exclude_id=None, slot=None):
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

    def create(self, validated_data):
        validated_data.pop('doctor_id')
        validated_data.pop('service_id')
        doctor = validated_data.pop('doctor')
        service = validated_data.pop('service')

        phone = validated_data.pop('patient_phone')
        first_name = validated_data.pop('patient_first_name')
        last_name = validated_data.pop('patient_last_name')
        email = validated_data.pop('patient_email', '')
        birth_date = validated_data.pop('patient_birth_date', None)

        patient, created = Patient.objects.get_or_create(
            phone=phone,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'birth_date': birth_date,
            },
        )
        if not created:
            patient.first_name = first_name
            patient.last_name = last_name
            if email:
                patient.email = email
            patient.save(update_fields=['first_name', 'last_name', 'email'])

        slot = validated_data.pop('slot', None)
        scheduled_at = validated_data.pop('scheduled_at')

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            service=service,
            slot=slot,
            scheduled_at=scheduled_at,
            notes=validated_data.pop('notes', ''),
        )
        if slot is not None:
            slot.is_available = False
            slot.save(update_fields=['is_available'])
        return appointment


class AppointmentUpdateSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField(min_value=1, required=False)
    service_id = serializers.IntegerField(min_value=1, required=False)
    scheduled_at = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(
        choices=Appointment.Status.choices,
        required=False,
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_scheduled_at(self, value):
        if value is None:
            return value
        if value <= timezone.now():
            raise serializers.ValidationError('Дата приёма должна быть в будущем')
        return value

    def validate_status(self, value):
        if value == Appointment.Status.COMPLETED:
            raise serializers.ValidationError(
                'Статус "completed" устанавливается только администратором',
            )
        return value

    def validate(self, data):
        instance = self.context.get('appointment')
        if instance is None:
            return data

        if instance.status == Appointment.Status.CANCELLED:
            raise serializers.ValidationError('Нельзя изменить отменённую запись')

        if instance.status == Appointment.Status.COMPLETED:
            raise serializers.ValidationError('Нельзя изменить завершённую запись')

        doctor = instance.doctor
        if 'doctor_id' in data:
            try:
                doctor = Doctor.objects.select_related('clinic').get(
                    pk=data['doctor_id'],
                    is_active=True,
                )
            except Doctor.DoesNotExist:
                raise serializers.ValidationError(
                    'Врач не найден или не принимает пациентов',
                )
            if not doctor.clinic.is_active:
                raise serializers.ValidationError('Клиника врача неактивна')

        service = instance.service
        if 'service_id' in data:
            try:
                service = Service.objects.get(pk=data['service_id'], is_active=True)
            except Service.DoesNotExist:
                raise serializers.ValidationError('Услуга не найдена')

        if service.clinic_id and service.clinic_id != doctor.clinic_id:
            raise serializers.ValidationError(
                'Услуга недоступна в клинике выбранного врача',
            )

        scheduled_at = data.get('scheduled_at', instance.scheduled_at)
        if 'scheduled_at' in data or 'doctor_id' in data or 'service_id' in data:
            create_serializer = AppointmentCreateSerializer()
            create_serializer._check_slot_available(
                doctor, service, scheduled_at, exclude_id=instance.pk,
            )

        data['doctor'] = doctor
        data['service'] = service
        return data

    def update(self, instance, validated_data):
        validated_data.pop('doctor_id', None)
        validated_data.pop('service_id', None)

        if 'doctor' in validated_data:
            instance.doctor = validated_data.pop('doctor')
        if 'service' in validated_data:
            instance.service = validated_data.pop('service')
        if 'scheduled_at' in validated_data:
            instance.scheduled_at = validated_data.pop('scheduled_at')
        if 'status' in validated_data:
            instance.status = validated_data.pop('status')
        if 'notes' in validated_data:
            instance.notes = validated_data.pop('notes')

        instance.save()
        return instance
