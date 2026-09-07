from django.contrib.auth import get_user_model
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
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


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


class CurrentUserSerializer(ModelSerializer):
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

    class Meta:
        model = Appointment
        fields = '__all__'