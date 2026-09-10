from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from clinics.models import (
    Doctor,
    ServiceDirection,
    Appointment,
    OmsDirection,
    OmsApplication,
    CallbackRequest,
    Review,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class ServiceDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDirection
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('patient', 'created_at')

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')

        if not doctor or not appointment_date or not appointment_time:
            raise serializers.ValidationError(
                'Укажите врача, дату и время приема.'
            )

        if appointment_date < timezone.localdate():
            raise serializers.ValidationError(
                'Нельзя записаться на прошедшую дату.'
            )

        busy = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        ).exclude(status='cancelled')

        if self.instance:
            busy = busy.exclude(id=self.instance.id)

        if busy.exists():
            raise serializers.ValidationError(
                'Это время у врача уже занято.'
            )

        if not attrs.get('direction'):
            attrs['direction'] = doctor.specialty

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['patient'] = user

        if not validated_data.get('full_name'):
            validated_data['full_name'] = user.get_full_name() or user.username

        return Appointment.objects.create(**validated_data)


class OmsDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OmsDirection
        fields = '__all__'


class OmsApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OmsApplication
        fields = '__all__'
        read_only_fields = ('created_at',)


class CallbackRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = '__all__'
        read_only_fields = ('created_at',)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
