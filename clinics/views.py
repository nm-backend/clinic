from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response

from clinics.models import Appointment, Clinic, Doctor, Service
from clinics.serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentModelSerializer,
    AppointmentUpdateSerializer,
    ClinicModelSerializer,
    DoctorModelSerializer,
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

        return queryset


class ServiceListAPIView(ListAPIView):
    serializer_class = ServiceModelSerializer

    def get_queryset(self):
        queryset = Service.objects.select_related('clinic').filter(is_active=True)

        clinic_id = _get_int_query_param(self.request, 'clinic_id')
        if clinic_id is not None:
            queryset = queryset.filter(
                Q(clinic_id=clinic_id) | Q(clinic__isnull=True),
            )

        return queryset


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
