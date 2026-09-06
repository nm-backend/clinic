from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from clinics.models import Appointment, CallbackRequest
from api.serializers import AppointmentSerializer, CallbackRequestModelSerializer


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.select_related(
        'patient',
        'doctor',
        'doctor__clinic',
        'service',
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        patient_phone = self.request.query_params.get('patient_phone')
        if patient_phone:
            queryset = queryset.filter(patient__phone=patient_phone)

        appointment_status = self.request.query_params.get('status')
        if appointment_status:
            queryset = queryset.filter(status=appointment_status)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == Appointment.Status.CANCELLED:
            raise ValidationError({'status': 'Запись уже отменена'})

        if instance.status == Appointment.Status.COMPLETED:
            raise ValidationError({'status': 'Нельзя отменить завершённую запись'})

        instance.status = Appointment.Status.CANCELLED
        instance.save(update_fields=['status', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CallbackRequestViewSet(ModelViewSet):
    serializer_class = CallbackRequestModelSerializer
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_staff:
            return CallbackRequest.objects.none()
        return CallbackRequest.objects.all()