from datetime import date, datetime, time

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clinics.models import (
    Appointment,
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
from api.serializers import (
    AppointmentSerializer,
    ClinicModelSerializer,
    CurrentUserSerializer,
    DoctorModelSerializer,
    EquipmentModelSerializer,
    PromotionModelSerializer,
    RegisterSerializer,
    ReviewModelSerializer,
    ServiceCategoryModelSerializer,
    ServiceModelSerializer,
)


def _get_int_query_param(request, param_name):
    raw_value = request.query_params.get(param_name)
    if raw_value is None or raw_value == '':
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        raise ValidationError({param_name: 'Должно быть целым чисном'})


class ClinicListAPIView(ListAPIView):
    serializer_class = ClinicModelSerializer

    def get_queryset(self):
        return Clinic.objects.filter(is_active=True)


class DoctorListAPIView(ListAPIView):
    serializer_class = DoctorModelSerializer

    def get_queryset(self):
        queryset = Doctor.objects.select_related('clinic').filter(
            is_active=True,
            clinic__is_active=True,
        )

        clinic_id = _get_int_query_param(self.request, 'clinic_id')
        if clinic_id is not None:
            queryset = queryset.filter(clinic_id=clinic_id)

        specialty = self.request.query_params.get('specialty')
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)

        category_id = _get_int_query_param(self.request, 'category_id')
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)

        return queryset


class ServiceCategoryListAPIView(ListAPIView):
    serializer_class = ServiceCategoryModelSerializer

    def get_queryset(self):
        return ServiceCategory.objects.all()


class ServiceListAPIView(ListAPIView):
    serializer_class = ServiceModelSerializer

    def get_queryset(self):
        queryset = Service.objects.select_related('clinic', 'category').filter(is_active=True)

        clinic_id = _get_int_query_param(self.request, 'clinic_id')
        if clinic_id is not None:
            queryset = queryset.filter(
                Q(clinic_id=clinic_id) | Q(clinic__isnull=True),
            )

        category_id = _get_int_query_param(self.request, 'category_id')
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)

        return queryset


class AvailableSlotsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        doctor_id = _get_int_query_param(request, 'doctor_id')
        day_value = request.query_params.get('date')

        if doctor_id is None or not day_value:
            raise ValidationError({'doctor_id': 'Обязательный параметр', 'date': 'Обязательный параметр'})

        try:
            day = date.fromisoformat(day_value)
        except ValueError as exc:
            raise ValidationError({'date': 'Неверный формат даты'}) from exc

        try:
            doctor = Doctor.objects.get(pk=doctor_id, is_active=True)
        except Doctor.DoesNotExist as exc:
            raise ValidationError({'doctor_id': 'Врач не найден'}) from exc

        slots = DoctorScheduleSlot.objects.filter(
            doctor=doctor,
            start_at__date=day,
            is_available=True,
        ).exclude(
            appointments__status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED]
        ).order_by('start_at').values('id', 'start_at', 'end_at')

        result = [
            {'id': s['id'], 'start': s['start_at'].isoformat(), 'end': s['end_at'].isoformat()}
            for s in slots
            if s['start_at'] > timezone.now()
        ]

        return Response(result)


class PatientAppointmentsAPIView(ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        patient_id = _get_int_query_param(self.request, 'patient_id')
        phone = self.request.query_params.get('phone')
        queryset = Appointment.objects.select_related(
            'patient',
            'doctor',
            'doctor__clinic',
            'service',
        )

        if self.request.user.is_authenticated:
            clinic_user = ClinicUser.objects.filter(user=self.request.user).first()
            if clinic_user and clinic_user.patient_profile_id:
                return queryset.filter(patient=clinic_user.patient_profile)

        if patient_id is not None:
            return queryset.filter(patient_id=patient_id)
        if phone:
            return queryset.filter(patient__phone=phone)
        return queryset.none()


class PromotionListAPIView(ListAPIView):
    serializer_class = PromotionModelSerializer

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True)


class ReviewListAPIView(ListAPIView):
    serializer_class = ReviewModelSerializer

    def get_queryset(self):
        return Review.objects.filter(is_active=True).select_related('doctor')


class EquipmentListAPIView(ListAPIView):
    serializer_class = EquipmentModelSerializer

    def get_queryset(self):
        return Equipment.objects.filter(is_active=True)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = ClinicUser.objects.get(user=user)
        return Response(CurrentUserSerializer(profile).data, status=status.HTTP_201_CREATED)


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = ClinicUser.objects.filter(user=request.user).first()
        if profile is None:
            profile = ClinicUser.objects.create(user=request.user, role=ClinicUser.Role.PATIENT)
        return Response(CurrentUserSerializer(profile).data)