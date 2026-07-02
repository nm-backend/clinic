from datetime import date, datetime, time

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clinics.models import Appointment, Clinic, ClinicUser, Doctor, DoctorScheduleSlot, Service, ServiceCategory
from clinics.serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentModelSerializer,
    AppointmentUpdateSerializer,
    ClinicModelSerializer,
    CurrentUserSerializer,
    DoctorModelSerializer,
    RegisterSerializer,
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
        raise ValidationError({param_name: 'Должно быть целым числом'})


def index(request):
    return render(request, 'index.html')


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
            doctor = Doctor.objects.select_related('clinic').get(pk=doctor_id, is_active=True)
        except Doctor.DoesNotExist as exc:
            raise ValidationError({'doctor_id': 'Врач не найден'}) from exc

        service = doctor.clinic.services.first()
        if service is None:
            service = Service.objects.filter(is_active=True).order_by('duration_minutes').first()

        if service is None:
            return Response([])

        slots = []
        doctor_slots = DoctorScheduleSlot.objects.filter(
            doctor=doctor,
            start_at__date=day,
            is_available=True,
        ).order_by('start_at')

        # Получение списка свободных слотов для врача
        if doctor_slots.exists():
            for slot in doctor_slots:
                if slot.start_at <= timezone.now():
                    continue
                if Appointment.objects.filter(
                    doctor=doctor,
                    status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
                    slot=slot,
                ).exists():
                    continue
                slots.append({
                    'id': slot.id,
                    'start': slot.start_at.isoformat(),
                    'end': slot.end_at.isoformat(),
                })
        else:
            start_time = time(8, 0)
            end_time = time(20, 0)

            current = datetime.combine(day, start_time)
            end_dt = datetime.combine(day, end_time)
            timezone_info = timezone.get_current_timezone()
            current = timezone.make_aware(current, timezone_info)
            end_dt = timezone.make_aware(end_dt, timezone_info)

            while current < end_dt:
                slot_end = current + timezone.timedelta(minutes=service.duration_minutes)
                if current > timezone.now() and not Appointment.objects.filter(
                    doctor=doctor,
                    status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
                    scheduled_at__lt=slot_end,
                ).filter(scheduled_at__lt=slot_end).exists():
                    overlap = False
                    for existing in Appointment.objects.filter(
                        doctor=doctor,
                        status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
                    ):
                        existing_end = existing.scheduled_at + timezone.timedelta(minutes=existing.service.duration_minutes)
                        if existing.scheduled_at < slot_end and existing_end > current:
                            overlap = True
                            break
                    if not overlap:
                        slots.append({
                            'start': current.isoformat(),
                            'end': slot_end.isoformat(),
                        })
                current += timezone.timedelta(minutes=30)

        return Response(slots)


class PatientAppointmentsAPIView(ListAPIView):
    serializer_class = AppointmentDetailSerializer

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


class AppointmentListCreateAPIView(ListCreateAPIView):
    serializer_class = AppointmentModelSerializer

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            'patient',
            'doctor',
            'doctor__clinic',
            'service',
        )

        patient_phone = self.request.query_params.get('patient_phone')
        if patient_phone:
            queryset = queryset.filter(patient__phone=patient_phone)

        appointment_status = self.request.query_params.get('status')
        if appointment_status:
            queryset = queryset.filter(status=appointment_status)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(
            AppointmentDetailSerializer(appointment).data,
            status=status.HTTP_201_CREATED,
        )


class AppointmentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentModelSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return Appointment.objects.select_related(
            'patient',
            'doctor',
            'doctor__clinic',
            'service',
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AppointmentDetailSerializer
        if self.request.method in ('PUT', 'PATCH'):
            return AppointmentUpdateSerializer
        return AppointmentModelSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())

        if serializer_class is AppointmentUpdateSerializer:
            kwargs['context']['appointment'] = self.get_object()

        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = AppointmentUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={**self.get_serializer_context(), 'appointment': instance},
        )
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(AppointmentDetailSerializer(appointment).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == Appointment.Status.CANCELLED:
            raise ValidationError({'status': 'Запись уже отменена'})

        if instance.status == Appointment.Status.COMPLETED:
            raise ValidationError({'status': 'Нельзя отменить завершённую запись'})

        instance.status = Appointment.Status.CANCELLED
        instance.save(update_fields=['status', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


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
